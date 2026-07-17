#!/usr/bin/env python3
"""Resolve and initialize the mud-player skill's persistent memory files.

The skill tracks two files across a play session:
    data/player.md   character state (vitals, location, inventory, goal)
    data/world.md     accumulated map/knowledge of the game world

These are plain markdown, meant to be read and edited directly (with
Read/Edit) by whatever is driving the MUD — this script only resolves paths
and scaffolds the files, it never touches their content once they exist.

Location defaults to <project_root>/data, where project_root is inferred
from this script's own position: .claude/skills/mud-player/scripts/memory.py
implies project_root is five levels up. Override with MUD_DATA_DIR if the
skill is installed somewhere that doesn't hold (e.g. a global skills dir, or
you want memory scoped to a different folder).

Usage:
    memory.py paths   print the resolved absolute paths, one per line
                       (player.md then world.md) — doesn't touch the files
    memory.py init     create data dir + player.md/world.md from templates
                       if missing or empty; never overwrites real content
"""
import os
import sys
from pathlib import Path

PLAYER_TEMPLATE = """\
# Player Memory

_Reflects the CURRENT state only — overwrite stale values in place rather
than appending a history. The daemon's transcript.log is the history if one
is ever needed. Updated after (almost) every command sent to the MUD._

## Current Goal
- Goal: (none set)
- Plan: (none)
- Progress: (none)

## Character
- Name:
- Level:
- Class / Guild:
- Title:

## Vitals
- HP: ?/?
- Mana: ?/?
- Move: ?/?
- Position:
- Conditions:

## Location
- Room:
- Area:

## Progress
- Exp:
- Exp to next level:
- Gold:
- Quest points:

## Inventory
- (empty)

## Equipment
- (empty)

## Skills & Spells
- (none known yet)
"""

WORLD_TEMPLATE = """\
# World Memory

_Accumulated map and knowledge of the game world. One entry per room/NPC/
monster — update an existing entry in place when you learn something new
about it, don't duplicate. This is meant to make later navigation faster,
not to be a full transcript._

## Map
<!-- Room name -- exits (direction: destination when known) -- notable contents -->

## Guilds & Trainers
<!-- Guild/class name -- location -- guildmaster -- skills/spells trainable there -->

## Shops & Services
<!-- Shop name -- location -- what it sells/does -->

## Monsters
<!-- Name -- location(s) seen -- approx level/difficulty -- notes (loot, danger) -->

## Points of Interest / Hazards
<!-- Zone level warnings, quest hooks, locked doors, anything worth remembering -->
"""


def resolve_data_dir() -> Path:
    override = os.environ.get("MUD_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    here = Path(__file__).resolve()
    try:
        project_root = here.parents[4]
        if (project_root / ".claude").is_dir():
            return project_root / "data"
    except IndexError:
        pass
    # Skill isn't at the expected .claude/skills/<name>/scripts depth
    # (e.g. installed globally) — fall back to the current directory rather
    # than guess wrong.
    return Path.cwd() / "data"


def cmd_paths(player_path: Path, world_path: Path) -> int:
    print(player_path)
    print(world_path)
    return 0


def cmd_init(data_dir: Path, player_path: Path, world_path: Path) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    created = []
    if not player_path.exists() or player_path.stat().st_size == 0:
        player_path.write_text(PLAYER_TEMPLATE)
        created.append(str(player_path))
    if not world_path.exists() or world_path.stat().st_size == 0:
        world_path.write_text(WORLD_TEMPLATE)
        created.append(str(world_path))
    if created:
        print("Initialized: " + ", ".join(created))
    else:
        print("Already initialized:")
        print(player_path)
        print(world_path)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    data_dir = resolve_data_dir()
    player_path = data_dir / "player.md"
    world_path = data_dir / "world.md"

    if cmd == "paths":
        return cmd_paths(player_path, world_path)
    if cmd == "init":
        return cmd_init(data_dir, player_path, world_path)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
