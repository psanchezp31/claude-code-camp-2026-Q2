require_relative "backends/anthropic"
require_relative "backends/gemini"
require_relative "backends/ollama"
require_relative "backends/ollama_cloud"
require_relative "backends/openai"

module Boukensha
  # Static model → capability table.
  #
  # `context_window` is a known *model* fact — the physical input ceiling — not a
  # value the user sets. The agent looks it up from its configured model id; the
  # user never configures it in settings.yaml. Unknown models fall back to a
  # conservative default so an unrecognised id can't silently assume a huge window.
  #
  # The table is *derived* from every backend's own MODELS constant rather than
  # hand-maintained. That matters because the lookup happens before any backend
  # object exists (Boukensha.run sizes the Context first), so it can't delegate to
  # backend.context_window — and a hand-copied table silently drifts, leaving
  # non-Anthropic models on the 32k default and triggering constant, needless
  # auto-compaction.
  module Models
    BACKENDS = [
      Backends::Anthropic,
      Backends::OpenAI,
      Backends::Gemini,
      Backends::Ollama,
      Backends::OllamaCloud
    ].freeze

    # Earlier backends win a duplicate model id — none exist today, and the
    # ordering above makes the outcome deterministic if one ever does.
    TABLE = BACKENDS.each_with_object({}) do |backend, table|
      backend::MODELS.each do |id, spec|
        table[id] ||= { context_window: spec[:context_window] }
      end
    end.freeze

    DEFAULT_CONTEXT_WINDOW = 32_000

    def self.context_window(model)
      TABLE.dig(model.to_s, :context_window) || DEFAULT_CONTEXT_WINDOW
    end
  end
end
