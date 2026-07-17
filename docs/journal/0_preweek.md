# Preweek Technical Documentation

## Technical Goal

The technical goal of Preweek (Explore) is to determine how well Agent Architectures fit our business use-case.

Examples of Agent Architectures That Scale With Effort:
- [Ref 1] An agent file with referenced files, e.g. AGENT.md, `@~/docs/*.md`
- Agent Skills driven by a main agent, e.g. `~/.skills`
- Filesystem Subagent driven by a coding harness or Coding Agent SDK, e.g. `~/subagents`
- AI workflow automation platform, e.g. n8n
- Use a generic AI Agent SDK that leverages plug-and-play generic AI packages
- Use low-level first-party LLM SDKs and write our own agentic loop
- Use REST APIs directly, write our own agentic loop
  - The agentic loop is model-driven orchestration with middleware programmatic guidance
  - The agentic loop is code-driven orchestration

## Technical Uncertainty

- I'm uncertain if an LLM's thinking mode and other "intelligence" parameters are sufficient to hold memory and drive decisions for a work-specific use-case.
- I'm uncertain whether a coding harness can interact with a MUD without an interface or SDK, or manage the telnet session at all.

## Technical Hypotheses

- Based on [Ref 1], I think we'll have issues with the coding harness driving the MUD without an interface, because there's no defined API — we're driving commands over a protocol we need to live-monitor. Telnet communication seems like it will be a sticking point.
- I think we'll need an interface, because managing a long-lived telnet session may prove difficult. In the past I've always found managing live sessions challenging.
- I think the only agent architecture that will be able to drive our use-case is one where we implement a specialized agentic loop, since I think generic model memory won't be capable enough to remember and navigate the MUD world — generic architectures will lack one of these two things.

## Technical Observations

- An AGENT.md-only approach could not reliably connect to the MUD. It could produce scripts, but creating a connection to the MUD was unreliable, and it needed deterministic, hard-coded knowledge of the MUD's TUI to work at all.
- Skills and Subagents, paired with a script to manage the telnet session, performed. They were able to actually play the MUD, but maybe not efficiently.
- Using markdown files as memory, where the coding harness updates simple memory files itself, produced brittle navigation instructions. For example:

```sh
To reach the **Newbie Zone** from Market Square:
1. `north` → Temple Square
2. `north` → Temple
3. `north` → Altar
4. `north` → Behind Altar
5. `north` → Great Field
6. `north` → Great Field (with newbie zone sign)
7. `east` → Newbie Zone entrance
8. `north` → Enter corridor
```

- Concretely, the mud-player skill (Skills + a Python telnet-daemon script) logged in, explored the Newbie Zone, and leveled the character from 1 to 3 by grinding weak mobs — real proof Skills/Subagents can drive live game state, not just produce plausible-looking scripts. It also hit a hard progression gate: a sign requiring level 7 (solo) before it's safe to reach the room holding our primary challenge target, the Massive Minotaur.

## Technical Conclusions

- Skills and Subagents are capable of driving the MUD.
- We do need specialized memory for map navigation and world data — storing the map as a room/exit graph (rather than a fixed turn-by-turn script) held up better than the brittle instructions above, since re-navigation used known exits instead of replaying a memorized path. This is likely the direction to keep for Week 2's specialized memory design.
- We opened a new technical use-case: whether our agent should handle multiple sessions for multiple players playing at the same time, since co-op is a common factor in MUDs which we forgot to consider in our design.
- We could not explore n8n completely due to technical restraints executing external scripts.
- Implementing our own specialized loops remains technically uncertain and will need to be explored in depth in Week 2.
- Without a customized agentic loop, the agents could not perform goals efficiently, and did not have any key meta strategies or long-horizon player strategies.

## Key Takeaway

When we have a specialized use-case like playing a MUD, we likely cannot leverage generic SDKs for Agents because we need specialized tooling and agentic loops.
