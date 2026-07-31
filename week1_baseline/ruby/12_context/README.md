# Step 12 — Context Management

When you call an LLM directly you are responsible for the context window. There is no auto-compacting. This step adds proper token tracking, visual warnings, and automatic compaction so the agent never silently blows past the limit.

## What's new

### Accurate context tracking

`Context` now maintains two distinct token counts:

| Attribute | What it measures |
|-----------|-----------------|
| `context_window` | The model's maximum input token capacity (default 200,000 for Anthropic) |
| `current_tokens` | Tokens actually used in the most recent API call (`usage.input_tokens` from the response) |

Previously `token_budget` (8,192) was displayed as the limit — that was the *output* `max_tokens`, not the context window. And the cumulative session token sum was shown as usage, which grew without bound even after `/clear`. Both are fixed.

The Agent updates `current_tokens` after every API response (including mid-turn tool-use calls), so the display always reflects what the next call will actually send.

### Context colour coding

The progress and status lines now colour the context indicator based on how full the window is:

| Usage | Colour | Meaning |
|-------|--------|---------|
| < 70% | Grey | Normal |
| 70–84% | Yellow | Approaching limit |
| ≥ 85% | Red | Compaction imminent |

A `⚠` symbol also appears in the status bar at 85%+.

### Auto-compaction

At the start of each agent turn, if `current_tokens / context_window ≥ 0.85`, the Agent automatically compacts the context before making any API call:

```
[context compacted — 12 messages dropped to free space]
```

Compaction drops the oldest 40% of messages (keeping at least 2) and resets `current_tokens` to 0. The first API call after compaction will report the true new size.

### `Context#compact_messages!`

```ruby
dropped = context.compact_messages!(target_fraction: 0.60)
# => 12  (number of messages dropped)
```

### `/compact` command

Manual compaction from the REPL or TUI:

```
boukensha> /compact
(compacted context — 12 messages dropped)
```

### `Logger#compaction` event

```json
{"phase":"compaction","before":172000,"dropped":12,"context_window":200000}
```

Emitted whenever auto- or manual compaction runs. The TUI subscribes to this event to display the compaction notice in the conversation view.

### `Boukensha.run` / `Boukensha.repl` — `context_window:` keyword

`token_budget:` is replaced by `context_window:`. You rarely pass it — it
defaults to the configured model's real window, looked up from
`Boukensha::Models`:

```ruby
Boukensha.repl(context_window: 128_000)  # override, e.g. to force early compaction
```

### `Boukensha::Models` — model → context window

The window is a *model* fact, not a user setting, and it has to be known before
any backend object exists (the `Context` is sized first). `Models::TABLE` is
derived at load time from every backend's own `MODELS` constant, so adding a
model to a backend is enough — there is no second table to keep in sync:

```ruby
Boukensha::Models.context_window("claude-haiku-4-5")  # => 200_000
Boukensha::Models.context_window("gpt-5.5")           # => 1_000_000
Boukensha::Models.context_window("who-knows")         # => 32_000 (conservative default)
```

This matters more than it used to: with auto-compaction firing at 85% of the
window, an under-reported window means constant, needless compaction.

### `Boukensha::Tasks::Player` — settings resolution

Provider, model, and system prompt are resolved through the task class rather
than read out of `Config` directly:

```ruby
task_settings = cfg.tasks(:player)              # the tasks.player.* block
Tasks::Player.provider(task_settings)           # => "anthropic"
Tasks::Player.model(task_settings)              # => "claude-haiku-4-5"
Tasks::Player.system_prompt(task_settings,
  user_prompts_dir:    cfg.user_prompts_dir,    # <BOUKENSHA_DIR>/prompts/player/system.md
  default_prompts_dir: Config::PROMPTS_DIR)     # falls back to this step's prompts/system.md
```

`prompt_override.system: true` in `settings.yaml` opts the task into its own
prompt file; without the bundled-default fallback the agent would silently run
with no system prompt at all when that file is missing.

### `Logger#response` — execution metadata

Every `response` event now carries what the call cost and where it ran:

```json
{"phase":"response","text":"...","provider":"anthropic","model":"claude-haiku-4-5",
 "usage_unit":"tokens","input_tokens":1000,"output_tokens":50,"cost_usd":0.00125}
```

Token counts are read across provider spellings (`input_tokens`,
`promptTokenCount`, `prompt_eval_count`, …), so cost logging works on every
backend, not just Anthropic.

## Run the demo

gem uninstall boukensha

gem build boukensha.gemspec
gem install boukensha-0.12.0.gem

```sh
ruby examples/example.rb

# via the global executable:
BOUKENSHA_DIR=~/Sites/Claude-Code-Camp/.boukensha BOUKENSHA_PATH=~/Sites/Claude-Code-Camp/week1_baseline/12_context boukensha
