#!/usr/bin/env python3
"""tbaMUD / CircleMUD session manager.

A MUD is a persistent world: your position, current room, combat, and
inventory only make sense within a single continuous connection. So instead
of reconnecting for every command, this tool keeps ONE connection alive in a
background daemon and lets you talk to it with quick subcommands.

    mud.py start        connect + log in, spawn the background session
    mud.py send "look"  send one command line, print the game's reply
    mud.py read         print anything the game pushed since you last looked
    mud.py status       is a session alive? in-game yet?
    mud.py stop         quit the character and shut the session down

Connection details come from the environment (with sensible defaults for the
local tbaMUD used in this project):

    MUD_HOST   (default: localhost)
    MUD_PORT   (default: 4000)
    MUD_USER   (default: dummy)
    MUD_PASS   (default: helloworld)
    MUD_STATE_DIR  where runtime files live
                   (default: $TMPDIR/mud-player-<host>-<port>)

The daemon speaks to the outside world over a Unix domain socket and writes a
full raw transcript to transcript.log inside the state dir, which is handy for
debugging or for reconstructing what happened.
"""

import json
import os
import re
import socket
import sys
import threading
import time

# --- configuration ---------------------------------------------------------

HOST = os.environ.get("MUD_HOST", "localhost")
PORT = int(os.environ.get("MUD_PORT", "4000"))
USER = os.environ.get("MUD_USER", "dummy")
PASSWORD = os.environ.get("MUD_PASS", "helloworld")

STATE_DIR = os.environ.get(
    "MUD_STATE_DIR",
    os.path.join(
        os.environ.get("TMPDIR", "/tmp"), f"mud-player-{HOST}-{PORT}"
    ),
)
SOCK_PATH = os.path.join(STATE_DIR, "daemon.sock")
STATE_PATH = os.path.join(STATE_DIR, "state.json")
TRANSCRIPT_PATH = os.path.join(STATE_DIR, "transcript.log")
DAEMON_LOG = os.path.join(STATE_DIR, "daemon.log")

# The in-game prompt on tbaMUD looks like "23H 100M 84V ... >". Seeing it is
# the surest sign we've cleared the login/menu screens and are actually in the
# world, ready to accept commands.
PROMPT_RE = re.compile(r"\d+H\s+\d+M\s+\d+V", re.IGNORECASE)

# CSI / ANSI escape sequences — colour codes, screen clears, cursor moves.
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


# --- byte-level helpers ----------------------------------------------------


def strip_telnet(data: bytes) -> bytes:
    """Remove telnet IAC negotiation so it doesn't pollute the transcript.

    tbaMUD probes the client (terminal type, MXP, MSDP, window size...) using
    IAC command sequences. We're not a real terminal and don't answer them, so
    we just filter them out of the byte stream.
    """
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        if b == 255:  # IAC
            cmd = data[i + 1] if i + 1 < n else 0
            if cmd in (251, 252, 253, 254):  # WILL/WONT/DO/DONT + option
                i += 3
            elif cmd == 250:  # SB ... IAC SE (subnegotiation)
                end = data.find(b"\xff\xf0", i)
                i = end + 2 if end != -1 else n
            else:
                i += 2
            continue
        out.append(b)
        i += 1
    return bytes(out)


def clean(text: str) -> str:
    """Human-readable view: drop ANSI codes and bare carriage returns."""
    text = ANSI_RE.sub("", text)
    return text.replace("\r", "")


# --- daemon side -----------------------------------------------------------


class Session:
    """Owns the live socket to the MUD and buffers everything it sends us."""

    def __init__(self):
        self.sock = None
        self.buf = bytearray()  # raw bytes after telnet stripping
        self.lock = threading.Lock()
        self.last_recv = 0.0
        self.alive = True
        self.in_game = False

    def connect_and_login(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=15)
        self.sock.settimeout(2.0)
        # Read the opening banner and step through name/password. We drive
        # this synchronously (before the reader thread starts) so login errors
        # surface immediately instead of getting lost in the buffer.
        self._expect(("known?", "what name", "by what name"), timeout=15)
        self._send_line(USER)
        marker = self._expect(
            ("password", "already playing", "no such", "not a valid"),
            timeout=10,
        )
        if "no such" in marker or "not a valid" in marker:
            raise RuntimeError(f"login rejected: {marker!r}")
        self._send_line(PASSWORD)

        # After the password we might land in one of a few places: straight
        # into the game (a reconnect), a MOTD page waiting for RETURN, or the
        # account menu where "1" enters the game. Keep reading and nudging
        # until we detect the in-game prompt or run out of patience.
        deadline = time.time() + 12
        acc = ""
        while time.time() < deadline:
            chunk = self._read_available(timeout=1.5)
            acc += clean(chunk).lower()
            if PROMPT_RE.search(acc):
                self.in_game = True
                break
            if "password" in acc and "incorrect" in acc:
                raise RuntimeError("incorrect password")
            if re.search(r"\b1\)\s", acc) or "enter the game" in acc:
                self._send_line("1")
                acc = ""
            elif "press return" in acc or "return to continue" in acc \
                    or "[ press" in acc:
                # A paged screen (MOTD, story) waiting for a keypress. Note we
                # deliberately do NOT treat "(motd)" as a signal here — the
                # in-game prompt itself contains "(motd)", which would make us
                # spam blank lines forever.
                self._send_line("")
                acc = ""
        if not self.in_game:
            raise RuntimeError("could not confirm we entered the game")

    # -- low-level, login-phase reads (no reader thread yet) --

    def _read_available(self, timeout: float) -> str:
        self.sock.settimeout(timeout)
        data = bytearray()
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                self.sock.settimeout(0.3)  # drain the rest of the burst
        except socket.timeout:
            pass
        text = strip_telnet(bytes(data))
        self._record(text)
        return text.decode("latin-1", "replace")

    def _expect(self, needles, timeout: float) -> str:
        deadline = time.time() + timeout
        acc = ""
        while time.time() < deadline:
            acc += clean(self._read_available(timeout=1.0)).lower()
            for needle in needles:
                if needle in acc:
                    return acc
        raise RuntimeError(
            f"timed out waiting for {needles!r}; saw: {acc[-200:]!r}"
        )

    def _send_line(self, line: str):
        self.sock.sendall((line + "\r\n").encode("latin-1", "replace"))

    def _record(self, raw: bytes):
        try:
            with open(TRANSCRIPT_PATH, "ab") as fh:
                fh.write(raw)
        except OSError:
            pass

    # -- steady-state reader thread --

    def reader_loop(self):
        self.sock.settimeout(1.0)
        while self.alive:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            if not chunk:
                break
            clean_bytes = strip_telnet(chunk)
            self._record(clean_bytes)
            with self.lock:
                self.buf += clean_bytes
                self.last_recv = time.time()
        self.alive = False

    def send(self, line: str, max_wait: float, idle: float) -> str:
        """Send a command and return the output it produces.

        We can't know in advance how much the game will say, so we wait until
        output has been quiet for `idle` seconds (meaning the reply finished),
        capped at `max_wait`. This keeps snappy commands snappy while still
        capturing long room descriptions or combat spam.
        """
        with self.lock:
            start = len(self.buf)
        self.sock.sendall((line + "\r\n").encode("latin-1", "replace"))
        deadline = time.time() + max_wait
        while time.time() < deadline:
            time.sleep(idle)
            with self.lock:
                grew = len(self.buf) > start
                quiet = (time.time() - self.last_recv) >= idle
            if grew and quiet:
                break
        with self.lock:
            raw = bytes(self.buf[start:])
        return clean(raw.decode("latin-1", "replace"))

    def read_new(self) -> str:
        with self.lock:
            raw = bytes(self.buf)
            self.buf = bytearray()
        return clean(raw.decode("latin-1", "replace"))


def write_state(**kwargs):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(kwargs, fh)
    os.replace(tmp, STATE_PATH)


def run_daemon():
    os.makedirs(STATE_DIR, exist_ok=True)
    # Fresh transcript per session so it maps to one continuous playthrough.
    open(TRANSCRIPT_PATH, "wb").close()
    session = Session()
    try:
        session.connect_and_login()
    except Exception as exc:  # noqa: BLE001 - report any login failure upward
        write_state(ok=False, error=str(exc), pid=os.getpid())
        return

    threading.Thread(target=session.reader_loop, daemon=True).start()
    write_state(ok=True, in_game=session.in_game, pid=os.getpid())

    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCK_PATH)
    srv.listen(5)
    srv.settimeout(1.0)

    running = True
    while running and session.alive:
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue
        with conn:
            try:
                req = json.loads(conn.recv(65536).decode("utf-8"))
            except (ValueError, OSError):
                continue
            op = req.get("op")
            if op == "send":
                out = session.send(
                    req.get("line", ""),
                    float(req.get("max_wait", 3.0)),
                    float(req.get("idle", 0.4)),
                )
                _reply(conn, ok=True, output=out, alive=session.alive)
            elif op == "read":
                _reply(conn, ok=True, output=session.read_new(),
                       alive=session.alive)
            elif op == "status":
                _reply(conn, ok=True, in_game=session.in_game,
                       alive=session.alive)
            elif op == "stop":
                try:
                    # Graceful CircleMUD exit: leave the world, then the menu.
                    session.send("quit", 2.0, 0.4)
                    session.send("0", 1.5, 0.4)
                except OSError:
                    pass
                _reply(conn, ok=True, output="session stopped")
                running = False

    session.alive = False
    try:
        session.sock.close()
    except OSError:
        pass
    for path in (SOCK_PATH, STATE_PATH):
        try:
            os.unlink(path)
        except OSError:
            pass


def _reply(conn, **payload):
    try:
        conn.sendall(json.dumps(payload).encode("utf-8"))
    except OSError:
        pass


# --- client side -----------------------------------------------------------


def daemon_alive() -> bool:
    if not os.path.exists(SOCK_PATH):
        return False
    try:
        c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        c.settimeout(2.0)
        c.connect(SOCK_PATH)
        c.close()
        return True
    except OSError:
        return False


def call_daemon(payload: dict, timeout: float = 30.0) -> dict:
    c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    c.settimeout(timeout)
    c.connect(SOCK_PATH)
    c.sendall(json.dumps(payload).encode("utf-8"))
    data = bytearray()
    while True:
        try:
            chunk = c.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
    c.close()
    if not data:
        return {"ok": False, "error": "no response from daemon"}
    return json.loads(data.decode("utf-8"))


def cmd_start():
    if daemon_alive():
        st = call_daemon({"op": "status"})
        print(f"Session already running (in_game={st.get('in_game')}).")
        return 0
    os.makedirs(STATE_DIR, exist_ok=True)
    if os.path.exists(STATE_PATH):
        os.unlink(STATE_PATH)
    import subprocess

    with open(DAEMON_LOG, "ab") as log:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "__daemon__"],
            stdout=log,
            stderr=log,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            env=os.environ.copy(),
        )
    # Wait for the daemon to finish logging in and report status.
    deadline = time.time() + 25
    while time.time() < deadline:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH) as fh:
                try:
                    st = json.load(fh)
                except ValueError:
                    time.sleep(0.2)
                    continue
            if st.get("ok"):
                print(f"Connected to {HOST}:{PORT} as {USER} "
                      f"(in_game={st.get('in_game')}).")
                return 0
            print(f"Login failed: {st.get('error')}", file=sys.stderr)
            return 1
        time.sleep(0.3)
    print("Timed out waiting for the session to start. "
          f"See {DAEMON_LOG}", file=sys.stderr)
    return 1


def cmd_send(argv):
    if not daemon_alive():
        print("No session running. Run 'mud.py start' first.",
              file=sys.stderr)
        return 1
    line = " ".join(argv)
    resp = call_daemon({"op": "send", "line": line})
    sys.stdout.write(resp.get("output", ""))
    if not resp.get("output", "").endswith("\n"):
        sys.stdout.write("\n")
    if not resp.get("alive", True):
        print("[session ended — the connection was closed by the MUD]",
              file=sys.stderr)
    return 0


def cmd_read():
    if not daemon_alive():
        print("No session running.", file=sys.stderr)
        return 1
    resp = call_daemon({"op": "read"})
    sys.stdout.write(resp.get("output", ""))
    return 0


def cmd_status():
    if not daemon_alive():
        print("stopped")
        return 0
    st = call_daemon({"op": "status"})
    print(f"running (in_game={st.get('in_game')}, alive={st.get('alive')})")
    return 0


def cmd_stop():
    if not daemon_alive():
        print("No session running.")
        return 0
    call_daemon({"op": "stop"})
    print("Session stopped.")
    return 0


USAGE = __doc__


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return 1
    cmd = sys.argv[1]
    if cmd == "__daemon__":
        run_daemon()
        return 0
    if cmd == "start":
        return cmd_start()
    if cmd == "send":
        return cmd_send(sys.argv[2:])
    if cmd == "read":
        return cmd_read()
    if cmd == "status":
        return cmd_status()
    if cmd == "stop":
        return cmd_stop()
    print(USAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
