# World Memory

_Accumulated map and knowledge of the game world. One entry per room/NPC/
monster — update an existing entry in place when you learn something new
about it, don't duplicate. This is meant to make later navigation faster,
not to be a full transcript._

## Map
- Bakery -- exits: s: Main St (bakery/armory junction) -- baker NPC, sells bread/pastry
- Main St (bakery/armory junction) -- exits: n: Bakery, s: Armory, e: Main St (market jct), w: (unexplored) -- Peacekeepers, cityguard patrol here
- Main St (market jct) -- exits: n: Temple Square? (via Market Sq), e: Market Square, s: Armory, w: Main St (bakery/armory jct)
- Armory -- exits: n: Main St (bakery/armory jct) -- armorer NPC, sells armor
- Main St (magic shop/gate jct) -- exits: n: Magic Shop, e: Main St (market jct), s: Mages' Guild entrance, w: West Gate -- cityguard, fidos
- Magic Shop -- exits: s: Main St (magic shop/gate jct) -- wizard NPC
- The Entrance To The Mages' Guild -- exits: n: Main St (magic shop/gate jct), s: (unexplored) -- sorcerer guards entrance, ATM. NOT the warrior guild.
- Market Square -- exits: n: Temple Square, e/w: Main St, s: Common Square -- central hub, statue
- Temple Square -- exits: n: Temple of Midgaard, e: Grunting Boar Inn, s: Market Square, w: Clerics' Guild entrance -- fountain, cityguards
- The Entrance To The Clerics' Guild -- exits: n: bar (blocked, "guard humiliates you"), e: Temple Square -- knight templar guards it, Peacekeeper, cityguard, ATM. NOT the warrior guild.
- Temple Of Midgaard -- exits: n: By The Temple Altar, e: Donation Room, s: Temple Square, w: Reading Room, d: (unexplored)
- Reading Room -- exits: e: Temple Of Midgaard -- teleporter device (zone travel), bulletin board (empty), saleswoman NPC
- The Midgaard Donation Room -- exits: w: Temple Of Midgaard -- charity NPC
- By The Temple Altar -- exits: n: Behind The Temple Altar, s: Temple Of Midgaard -- statue of Odin
- Behind The Temple Altar -- exits: n: The Great Field Of Midgaard, s: By The Temple Altar
- The Great Field Of Midgaard -- exits: n: (continues, loops back to itself once), e: Entrance To The Newbie Zone, s: Behind The Temple Altar, w: The Dirt Path -- open countryside
- The Dirt Path -- exits: e: Great Field, w: The Great Chessboard Of Midgaard (gate, "above your recommended level" warning at lvl 1)
- Entrance To The Newbie Zone -- exits: n: The Beginning Of The Passage, w: Great Field
- The Beginning Of The Passage -- exits: e: The Dirty Hallway, s: Entrance To The Newbie Zone -- newbie monster + creepy little crawling thing here (weak, per zone design)
- The Dirty Hallway -- exits: e: A Nexus, s: door (closed/unexplored), w: The Beginning Of The Passage -- newbie monster, creepy little crawling thing, and someone's pet dragon here
- A Nexus -- exits: n & e both lead into the SAME bright ring loop from opposite ends (n: A Bright Hallway -> Statue's Room -> The Hallway -> North Stairs -> South Stairs -> A Bright Hallway(2) -> back to Nexus via e), s: More Of The Hallway, w: The Dirty Hallway -- ring is now fully mapped, all 4 Nexus exits explored; mob spawns wander here
- A Bright Hallway -- exits: n: The Statue's Room, s: A Nexus -- clean/decorated; floor design = "Crest of the Harlequin Guild" (not the warrior guild)
- The Statue's Room -- exits: e: The Hallway, s: A Bright Hallway, n: statue (decorative only, not a real exit despite room text) -- "clueless newbie" mob spawns here (~33 exp)
- The Hallway -- exits: e: The North Stairs, w: The Statue's Room -- decorated with banners/pictures
- The North Stairs -- exits: s: The South Stairs, w: The Hallway, u: balcony (unexplored) -- domed room, stairs up to open-air balcony
- The South Stairs -- exits: n: The North Stairs, s: A Narrow Passage, w: A Bright Hallway (2nd, e/w one), u: balcony (unexplored) -- domed room, stairs up to open-air balcony; "annoying newbie" spawns here (~151 exp)
- A Bright Hallway (2nd instance, e/w exits) -- exits: e: The South Stairs, w: (unexplored) -- another Harlequin Guild crest room; distinct from the n/s "A Bright Hallway" off A Nexus (this maze reuses room names)
- A Narrow Passage -- exits: n: The South Stairs, s: small oak door (closed, "hear movement" behind it -- good candidate for the red room / minotaur) -- "talkative newbie" mob spawns here, gave 375-377 exp (best grind spot found)
- The Balcony (up from South Stairs, also reachable from North Stairs via u) -- exits: n: (connects toward North Stairs balcony, unexplored), d: back down -- semicircle balcony overlooking Midgaard to the south-west; no red-room sighting from here
- More Of The Hallway -- exits: n: A Nexus, s: Another Corner, w: door (closed/unexplored) -- creepy little crawling thing here
- Another Corner -- exits: n: More Of The Hallway, e: door (was closed, now open) to The Alchemist's Room, w: A Brighter Hallway
- A Brighter Hallway -- exits: e: Another Corner, w: The End Of The Passage -- mob spawns wander here
- The End Of The Passage -- exits: e: A Brighter Hallway, w: open air (exits the newbie zone dungeon, likely back to Great Field area) -- creepy little crawling things spawn here; pet dragon reported here too (not yet seen directly)
- The Alchemist's Room -- exits: n: door (unexplored), w: Another Corner, d: dark stairway down (WARNING SIGN: "If you are below level 7 and alone, or below level 4 then bugger off! Or else don't blame me if you die...") -- Newbie Alchemist NPC here
- Grunting Boar Inn entrance hall -- exits: n: Post Office, e: bar, w: Temple Square, u: Reception -- cityguard
- The Grunting Boar (bar) -- exits: w: entrance hall -- bartender, drunks, sells drinks
- Post Office -- exits: s: entrance hall -- postmaster NPC
- Reception (Grunting Boar Inn, up from entrance hall) -- exits: n: Cryogenic Center, d: entrance hall -- receptionist, ATM
- The Cryogenic Center -- exits: s: Reception -- cryogenicist NPC
- West Gate area (Inside The West Gate Of Midgaard) -- exits: e: Main St, s: Wall Road, w: Outside The West Gate -- 4-5 cityguards
- Outside The West Gate Of Midgaard -- exits: e: Inside The West Gate -- edge of a forest to the west (not explored past this room); janitor, Peacekeepers. NOT the warrior guild.
- Wall Road (multiple linked segments running along west wall, connecting West Gate down to a river bridge and the Concourse/Promenade loop around the east side) -- one segment has "letters written on the wall" (not yet read)
- On The Bridge -- exits n/s along Wall Road, crosses the river
- The Concourse / The Promenade (river-side path forming a loop from the west bridge around to the northeast wall corner and down to Park Road) -- Town Crier NPC wanders this loop
- Park Road (multi-segment path south from Promenade) -- one segment has the Cityguard HQ building (closed door, "Authorized Personnel Only" sign -- NOT a guild); road bends east into the Road Crossing
- The Road Crossing -- exits n/e/s/w/u -- a giant chain runs up into the sky; road sign: N/S = Emerald Avenue, E/W = Park Road, Up = "Redferne's Flying Citadel" (separate high-level zone, not explored — likely too high level for a lvl 1 character)
- Emerald Avenue (multi-segment, loops from Road Crossing north to the Promenade) -- north end has Town Hall to the east and the (Eastern) Park Entrance to the west
- Town Hall: Waiting Room -- exits: w: Emerald Ave, e: Mayor's Office -- secretary NPC
- Town Hall: Mayor's Office -- exits: w: Waiting Room -- dead end, Mayor NPC asleep. NOT the warrior guild.
- Eastern Park Entrance -- exits: e: Emerald Ave (north end), w: park interior
- The Western Park Entrance / Eastern Park Entrance / park interior paths ("A Path In The Park" x2) -- small ring of paths around The Pond, connecting to both park entrances and north to "A Small Path In The Park" / Park Cafe
- The Pond -- exits e/w back to the two "A Path In The Park" rooms -- duck, duckling, swan; swimming only, not a guild
- Park Cafe -- exits: w: Park Entrance (western) -- Maid NPC, Sexton NPC
- Common Square -- exits: n: Market Square, e: Dark Alley, s: The Dump, w: Poor Alley -- beastly fidos
- The Dump -- exits: n: Common Square, d: sewer (unexplored)
- The Dark Alley -- exits: w: Common Square, s: Guild of Thieves, e: Dark Alley At The Levee -- mercenaries. NOT the warrior guild (this is thieves').
- The Dark Alley At The Levee -- exits: e/w along alley, s: The Levee
- The Levee -- exits: n: Dark Alley At The Levee, s: river (needs a boat) -- retired captain sells boats
- Eastern End Of Poor Alley -- exits: e: Common Square, s: Grubby Inn, w: Poor Alley -- beastly fidos
- Poor Alley (west end) -- exits: e: Eastern End Of Poor Alley, w: city wall (dead end) -- beggar NPC
- Grubby Inn -- exits: n: Eastern End Of Poor Alley -- Filthy the bartender, beggar

## Guilds & Trainers
- Mages' Guild -- south off Main St (magic shop/gate junction, west end of Main Street) -- sorcerer guards entrance -- NOT warrior guild
- Clerics' Guild -- west off Temple Square -- knight templar guards entrance, inner bar is blocked to non-members -- NOT warrior guild
- Guild of Thieves -- south off The Dark Alley -- not yet entered -- NOT confirmed warrior guild (by name), but interior untested
- Warriors' Guild -- LOCATION NOT YET FOUND after exploring nearly all of Midgaard proper (Main St, Market/Temple/Common Squares, Dark Alley, Poor Alley, the park/Emerald Ave/Town Hall loop, Wall Road/Concourse/Promenade, West Gate + just outside it, the newbie zone). Ruled out: Mages' Guild, Clerics' Guild, Town Hall, Cityguard HQ. Remaining unexplored leads: the "strange structure" east of the Great Field path (north of the temple, past Behind The Temple Altar); south exit from the Mages' Guild entrance hall; down/sewer exit from The Dump; further into the forest west of Outside The West Gate; inside the Thieves' Guild itself. Start the next search there rather than re-walking the rest of the map above.

## Shops & Services
- Bakery -- north of Main St bakery/armory jct -- buy/sell bread, pastry
- Armory -- south of Main St bakery/armory jct -- buy/sell armor
- Magic Shop -- north of Main St magic-shop/gate jct -- magic items
- Grunting Boar bar -- east of its entrance hall, off Temple Square -- drinks
- Grubby Inn -- south of Eastern End Of Poor Alley -- drinks, rough crowd
- Park Cafe -- east of Western Park Entrance -- food/tea
- ATMs (automatic teller machines) -- Temple Of Midgaard, Reception (Grunting Boar Inn), Mages'/Clerics' Guild entrances

## Monsters
- Oozing green gelatinous blob -- seen at Main St junctions, Magic Shop, Park Cafe -- wanders, low threat presumed (untested)
- Beastly fido -- seen at west Main St, Common Square, Poor Alley -- pack scavenger, low level presumed
- Newbie monster / creepy little crawling thing -- Entrance To The Newbie Zone dungeon -- intentionally weak, meant for lvl 1
- Someone's pet dragon (loose) -- End Of The Passage, newbie zone -- unclear threat, treat cautiously
- Massive minotaur -- per user, located in "the red room" inside the Newbie Zone, presumed past the level-7-warning stairway down from The Alchemist's Room (not yet visually confirmed). Goal target; do not engage below level 7 solo.

## Points of Interest / Hazards
- Dark stairway down from The Alchemist's Room (newbie zone) -- warning sign: level 7+ required if alone, or level 4+ in a group, else "don't blame me if you die." Likely leads to the tougher area where the reported "massive minotaur" lives. Dummy is level 1 -- descending now would be extremely dangerous, probably fatal.
- The Great Chessboard Of Midgaard (west of The Dirt Path) -- flagged "above your recommended level" for a level 1 character; avoid unless risk is wanted
- Teleporter device in the Reading Room -- transfers between zones; `look teleporter` lists usage (`teleport <zone>`), zone list via `help zones`
- Guards ("cityguard"/"Peacekeeper") block hostile action in town but don't block normal movement except specific guarded doors (e.g. Clerics' Guild inner bar)
