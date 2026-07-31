# Week 1 Technical Documentation

## Technical Goal

Preweek ended with two open threads: implementing our own specialized agentic loop, and designing specialized memory for map navigation. Week 1 (Baseline) takes the first one.

The technical goal of Week 1 is to find out what it actually costs to write our own coding harness from scratch — no Agent SDK, no framework, just `net/http` and `json` — and to build it in a way a bootcamper can read.

We built BOUKENSHA, a Ruby coding harness, as thirteen numbered steps, where each step is a complete, runnable copy of the framework at that point in its life:

| Step | What it adds |
|---|---|
| `00_config` | Config directory, `settings.yaml`, `.env` |
| `01_struct_skeleton` | `Tool`, `Message`, `Context` |
| `02_the_registry` | Storing tools and dispatching them |
| `03_prompt_builder` | Assembling the API payload |
| `04_api_client` | One HTTP round trip; backend and task abstractions |
| `05_agent_loop` | The loop — request, dispatch tools, know when to stop |
| `06_the_logger` | Session logs as JSON Lines |
| `07_the_run_dsl` | `Boukensha.run(task: "…")` |
| `08_the_repl_loop` | `Boukensha.repl` — many turns, history accumulates |
| `09_global_executable` | Gemspec, `bin/boukensha`, `~/.boukensharc` loader |
| `10_standard_tool_library` | `Tools::FileSystem`, `Tools::Shell` |
| `11_tui` | A charm/bubbletea terminal UI |
| `12_context` | Token tracking, colour coding, auto-compaction |

Alongside it we built `log_viz`, a small Sinatra app that renders the `.jsonl` session logs as a browsable transcript with per-call cost and token breakdowns.

## Technical Uncertainty

- I'm uncertain how much code an agentic loop actually is. Preweek concluded we need one, but not that it's affordable to write and maintain ourselves.
- I'm uncertain whether one loop can speak to multiple providers — Anthropic, OpenAI, Gemini, Ollama — without the loop itself filling up with provider-specific branches.
- I'm uncertain whether we can keep the MUD's stateful telnet session *out* of the harness, or whether the harness has to grow MUD-shaped tools.
- I'm uncertain whether context management matters at our scale, or whether it's a problem we only hit much later.

## Technical Hypotheses

- I think the agent loop will be the hard part, and everything around it — config, logging, packaging — will be routine.
- I think multi-provider support is mostly URLs, auth headers, and payload key names.
- I think a folder per step is the simplest way to teach this, because a reader can open one step and see the whole system.
- I think the MUD will need bespoke tools inside the harness, since it's the one thing our use-case actually cares about.

## Technical Observations

- **The loop is the small part.** `agent.rb` is under 200 lines, and most of that is the two circuit breakers and the wind-down call, not the loop itself. Everything around it — config resolution, backends, logging, REPL, TUI, gem packaging — is where the code went. My hypothesis was backwards.

- **Provider differences are not URLs, they are response shapes.** Each backend has to normalize into one content-block contract before the loop sees it. Anthropic returns `thinking` / `redacted_thinking` blocks whose signatures must round-trip unmodified. Gemini puts reasoning in parts flagged `thought` with a `thoughtSignature`. Ollama puts it on `message["thinking"]`. Even token usage disagrees:

```text
input_tokens        (Anthropic)
prompt_tokens       (OpenAI)
promptTokenCount    (Gemini)
prompt_eval_count   (Ollama)
```

- **A provider can move the endpoint out from under you.** `gpt-5.x` rejects `reasoning_effort` together with tools on `/v1/chat/completions` and tells you to use `/v1/responses`. That is not a URL change: messages become `input` items, the system prompt becomes a top-level `instructions` string, tool definitions lose their `function:` wrapper, and tool results round-trip as `function_call_output` matched by `call_id`.

- **Context management is real, and the naive version is wrong in a way that hides.** Before step 12 we were displaying `token_budget` (8,192) as the limit — that is the *output* `max_tokens`, not the context window — and showing a cumulative session sum as usage, which kept growing even after `/clear`. Both looked like working features.

- **The TUI cost us a C extension patch.** The `bubbletea` gem ships as a precompiled platform gem, and the pending-input fix we needed lives in its C extension, outside this repo, and is destroyed by every `bundle install`. We had to vendor the patched sources plus an apply script under `patches/bubbletea/` just to make the fix reproducible.

- **The MUD did not need bespoke tools in the harness.** Pushing the stateful session behind a `mud-manager --mcp` daemon put the one hard, concurrency-heavy piece — the socket, the reader thread, telnet IAC stripping, the login dance — in exactly one place, and left the harness generic. The client half was never MUD-specific either.

- **A folder per step is a full copy of the codebase, and copies drift.** This is the observation that cost us the most time. A fix made in step 09 does not exist in steps 10, 11, or 12. Concretely, the `~/.boukensharc` key=value parser had to be hand-ported into three later steps after the fact, and a key=value rc file made every one of them abort:

```text
boukensha: ~/.boukensharc points to # Which config dir boukensha ...
       but no lib/boukensha.rb was found there.
```

  By the end of the week, steps 10, 11 and 12 had diverged far enough that reconciling them needed *written merge plans* rather than a diff.

- **A merge plan is only as good as the tree it was written against.** The `context_delta` plan was written assuming steps 10 and 11 had already been rewritten into MCP hosts. In this repo they have not — that work shipped in the `mud_manager` gem's daemon and never landed here. Roughly half the plan had no source to copy from, and I only found out by checking every premise before executing. The half that did apply also turned up two live bugs the plan hadn't noticed: a bundled prompts path that resolved one directory too high, and a gemspec that never packaged the prompts at all — together meaning a missing user prompt override silently ran the agent with no system prompt.

- **Structured logs turned into a product.** Writing every run as `.jsonl` and pointing a small Sinatra app at it made the loop debuggable in a way `puts` never was — per-call provider, model, token counts, and estimated cost, grouped by iteration, with raw MUD ANSI rendered as colour.

## Technical Conclusions

- Writing our own agentic loop is affordable, and Preweek's conclusion holds. What is expensive is not the loop — it is the normalization layer underneath it and the operational surface around it.
- Multi-provider support should be treated as a normalization contract with tests, not as a set of backend classes that each "work." Every capability we add — reasoning, cost, usage — has to be normalized once per provider or it silently only works on Anthropic.
- Context management has to be designed in from the point the loop exists, not bolted on at step 12. The failure mode is not a crash, it is a plausible-looking number.
- The step-per-folder teaching layout is good for reading and bad for maintaining. We need either a forward-port discipline we actually follow, or steps generated from one source of truth. Right now every post-hoc fix is an N-way manual port, and we have already paid for that twice.
- MCP is the right seam between the harness and any stateful external system. It kept the MUD's hard part in one process and made the harness's client half generic enough to plug into servers we haven't written.
- We are carrying real, known debt into Week 2: the MCP-host migration is not in steps 10–12, step 12's own token accounting only reads Anthropic's usage keys (so compaction and the turn-token breaker quietly do nothing on other providers), and there are no tests in this tree at all.
- The specialized memory thread from Preweek — the room/exit graph instead of brittle turn-by-turn instructions — is still untouched. It stays open.

## Key Takeaway

Writing the agentic loop was the easy part. The cost lives in everything around it: normalizing providers that disagree about their own response shapes, managing a context window nobody manages for you, and keeping thirteen copies of the same codebase from silently drifting apart.
