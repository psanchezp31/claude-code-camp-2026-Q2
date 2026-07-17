---
name: mud-player
description: >-
  Play a tbaMUD / CircleMUD-style text MUD over a telnet connection on behalf
  of the user — connecting, logging in, exploring rooms, moving, fighting,
  managing inventory, and pursuing in-game goals, including long-running ones
  like "reach level 7" or "hunt down and kill the swamp troll" that span many
  commands. Use this whenever the user wants to connect to, log into, or play
  a MUD / tbaMUD / CircleMUD / DikuMUD, or asks you to drive a character in a
  text adventure server (e.g. "connect to the mud", "log into tbaMUD and
  explore", "go kill something and level up", "check my inventory in the
  game", "find my starting guild and practice kick"). Tracks character state
  and a map of the world in data/player.md and data/world.md so long or
  summarized sessions don't lose track of progress. The default target is the
  local tbaMUD on localhost:4000 with character dummy/helloworld, but host,
  port, and credentials are configurable.
---

# Playing a MUD (tbaMUD / CircleMUD)

A MUD (Multi-User Dungeon) is a live text world you interact with by typing
short commands (`look`, `north`, `kill rat`, `get sword`, `inventory`) and
reading the text it sends back. tbaMUD is a modern continuation of CircleMUD,
which descends from DikuMUD, so its command set and screens are the classic
Diku style.

The single most important thing to understand: **a MUD is stateful and
persistent within one connection.** Your character stands in a specific room;
combat, hunger, and position all live inside one continuous session. You cannot
reconnect for every command — you must hold one connection open and send
commands into it over time. The bundled `scripts/mud.py` does exactly that: it
runs a background daemon that owns the connection, so you interact with the
world through quick subcommands while the session persists between them.

## The workflow

Use `scripts/mud.py` (run it with `python3`). From the skill directory:

```bash
python3 scripts/mud.py start          # connect + log in (do this once)
python3 scripts/mud.py send "look"    # send a command, see the reply
python3 scripts/mud.py send "north"
python3 scripts/mud.py read           # drain anything that arrived unprompted
python3 scripts/mud.py status         # is the session alive / in-game?
python3 scripts/mud.py stop           # quit the character, close the session
```

Typical loop:

1. **Load memory.** Run `python3 scripts/memory.py init` (creates
   `data/player.md` / `data/world.md` from templates if they don't already
   exist — harmless to run every time), then `Read` both files. They tell you
   who the character is, where they were, and what they were working toward —
   see "Memory" below.
2. **Start once.** Run `start`. It connects, feeds the username/password,
   clicks through the MOTD and account menu, and returns when the character is
   actually in the world (`in_game=True`). If a session is already running,
   `start` just tells you so — it won't open a second connection.
3. **Orient.** `send "look"` to see the current room, then `send "exits"`.
   Read the room name, description, exits line (`[ Exits: n e s w ]`), and any
   creatures or items mentioned.
4. **Act, one command at a time.** Send a single MUD command per `send` call
   and read the reply before deciding the next move. Each reply ends with the
   prompt line `NNH NNM NNV (news) (motd) >`, which shows current hit points
   (H), mana (M), and movement (V) — watch these, especially in combat.
5. **Update memory, every time.** After each `send`, fold anything relevant
   out of the reply into `player.md` / `world.md` before moving on — see
   "Memory" below. This is what makes goals durable across a long play
   session.
6. **Pursue the goal.** Explore by moving through exits; fight with
   `kill <target>`; pick things up with `get <item>` / `get all`; check
   yourself with `score`, `inventory` (`i`), and `equipment` (`eq`). For
   anything spanning multiple commands, see "Long-running goals" below.
7. **Stop when done.** `send "quit"` leaves cleanly, or `stop` quits the
   character and tears the session down.

## Reading the output

Each `send` prints just the text the game produced in response, with ANSI
colour codes and telnet noise already stripped. The trailing prompt tells you
the command completed and shows your vitals. If output ever looks truncated
(the game was still printing when the capture window closed), call `read` to
pick up the rest, or send the command again.

`read` (without sending anything) is useful because MUDs push text at you
unprompted — another player speaks, a mob wanders in, a fight tick lands, you
get hungry. Poll `read` between actions during combat or when waiting.

## Essential MUD commands (send these as the argument to `send`)

| Intent | Command |
|--------|---------|
| Look at the room / a thing | `look`, `look <target>` |
| Move | `north` `south` `east` `west` `up` `down` (or `n s e w u d`) |
| List exits | `exits` |
| Your character sheet | `score` |
| Inventory / worn gear | `inventory` (`i`) / `equipment` (`eq`) |
| Pick up / drop | `get <item>`, `get all`, `drop <item>` |
| Wear / wield | `wear <item>`, `wield <weapon>` |
| Attack | `kill <target>` (combat then auto-continues each round) |
| Flee a losing fight | `flee` |
| Talk | `say <msg>`, `tell <player> <msg>` |
| Rest to recover | `rest`, then `stand` |
| Get help | `help`, `help <topic>` |

Watch your `H` (hit points) in the prompt during combat — if it drops
dangerously low, `flee`. The default character `dummy` is level 1, so avoid
zones the game warns are "above your recommended level" unless the user
explicitly wants the risk.

## Memory: player.md and world.md

A MUD session can run for a very long time and this conversation may get
summarized along the way — raw game text scrolling past isn't enough to
reliably pick back up hours later. So the skill keeps two markdown files as
its actual state:

- **`data/player.md`** — the character's current state: vitals, location,
  inventory/equipment, known skills, and the standing goal (see below).
- **`data/world.md`** — a running map of the world: rooms and their exits,
  where guilds/shops/trainers are, and what monsters live where.

`scripts/memory.py` only resolves paths and scaffolds these files — you read
and edit the content yourself with `Read`/`Edit`:

```bash
python3 scripts/memory.py paths   # print the two resolved file paths
python3 scripts/memory.py init    # create them from templates if missing/empty
```

They default to `data/` at the project root (found by walking up from this
skill's own install location). Set `MUD_DATA_DIR` to override that if it
resolves wrong — e.g. the skill is installed outside a project.

**Update both files after (almost) every `send`**, not just at big moments —
that's what keeps them trustworthy enough to resume from. Keep each edit
small and targeted rather than rewriting the whole file:

- **player.md**: the Vitals block (HP/Mana/Move) comes straight off the
  trailing prompt line — update it whenever the numbers changed. Update
  Location whenever you move. Touch Inventory/Equipment/Skills/Progress only
  when the command actually changed them — most `send` calls only need a
  one-line edit to Vitals. This file describes the *current* state; overwrite
  stale values in place, don't accumulate history (the daemon's
  `transcript.log` already is the history, if one is ever needed).
- **world.md**: the first time you see a room, NPC, or monster, log it. If
  you're back in an already-logged room, don't add a duplicate entry — only
  edit it if you learned something new (an untried exit, a guildmaster you
  hadn't noticed). One entry per thing, kept current.

## Long-running goals

Goals like "reach level 7", "find my starting guild and practice kick", or
"hunt down and kill the swamp troll" span many commands and outlive any
single reply from the game. Two habits make that tractable:

1. **Record the goal.** As soon as you have one, write it into player.md's
   `Current Goal` section along with a short plan (e.g. "1) `help warrior` to
   confirm my class's skills and guild 2) locate the guild in world.md or by
   exploring 3) practice kick there"). Update `Progress` as milestones land.
   If you're ever unsure what you were mid-way through doing — after a long
   detour, a context summary, or just picking the session back up — re-read
   player.md's Current Goal before deciding the next command instead of
   guessing.
2. **Navigate using world.md, not memory of the last few messages.** Check
   whether the guild/monster/shop you need is already logged before wandering
   blind. If it isn't, explore systematically — pick an unexplored exit, log
   what you find, keep going — rather than re-walking rooms you've already
   recorded.

A goal is scoped to the current play session — it doesn't need to survive
`stop`/restart, so there's no need to persist "resume instructions" beyond
what player.md's Current Goal already captures while the session is live.

Notes for common goal types:

- **Learning a skill (e.g. "practice kick"):** `practice` with no argument
  lists what you know and how many practice sessions you have left. You can
  only actually practice inside your own class's guild, in front of a
  guildmaster — trying it with a trainer, shopkeeper, or armorer fails with
  "You can only practice skills in your guild." Use `help <class>` (e.g.
  `help warrior`) to see which skills your class gets, and check world.md's
  Guilds & Trainers section (or explore to find it) for where that guild is.
- **Leveling:** low-level mobs near the starting city give exp at low risk.
  Track exp/level in player.md's Progress section so you know how close you
  are without re-running `score` constantly.
- **Hunting a named monster:** check world.md's Monsters section for a known
  location first. If it's not listed, expand outward from the city, logging
  every room and monster you pass so the map is filled in for next time.

## Configuration

Connection settings come from the environment, with defaults for this
project's local MUD. Override them by exporting variables before `start`:

- `MUD_HOST` (default `localhost`)
- `MUD_PORT` (default `4000`)
- `MUD_USER` (default `dummy`)
- `MUD_PASS` (default `helloworld`)

## Recovering from trouble

- **`start` reports a login failure or timeout** — read the raw transcript at
  `$TMPDIR/mud-player-<host>-<port>/transcript.log` (default
  `/tmp/mud-player-localhost-4000/transcript.log`) to see exactly what the
  server sent. The daemon's own stderr is in `daemon.log` beside it.
- **`send` says the session ended** — the MUD closed the connection (you quit,
  were killed, or idled out). Run `start` again; a still-logged-in character
  will simply reconnect.
- **Output seems out of sync** — call `read` to flush the buffer, then resume.
- **Not sure what state you're in** — `send "look"` is always safe and
  re-orients you.

## Notes on this skill's approach

The daemon keeps a full raw transcript of the session, so if the user asks
"what happened" or wants a recap, that file is the source of truth. When
playing toward a goal, narrate progress to the user in plain language (where
you are, what you found, what you did) rather than dumping raw game text at
them — read the MUD's output yourself, then summarise and decide.
