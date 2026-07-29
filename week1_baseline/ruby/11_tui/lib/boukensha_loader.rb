# BoukenshaLoader resolves which step folder to load from, then boots the REPL.
#
# Two independent settings, each resolved the same way — environment variable
# first, then ~/.boukensharc, then a built-in default:
#
#   BOUKENSHA_PATH  which *step* lib to load  (default: the lib bundled in this
#                   gem — step 10, the latest release)
#   BOUKENSHA_DIR   config dir holding settings.yaml, .env and prompts/
#                   (default: ~/.boukensha)
#
# ~/.boukensharc is a key=value file; blank lines and # comments are ignored:
#
#   BOUKENSHA_PATH=~/Sites/boukensha/10_standard_tool_library
#   BOUKENSHA_DIR=~/projects/mybot/.boukensha
#
# For backwards compatibility, a file containing a single bare path is still
# read as BOUKENSHA_PATH.
#
# MUD connection details come from settings.yaml (mud: block) by default.
# The legacy MUD_NAME / MUD_HOST / MUD_PORT / MUD_PASSWORD env vars are still
# honoured and take precedence over config when set.
#
# Examples:
#   boukensha                                                              # uses bundled lib + ~/.boukensha
#   BOUKENSHA_PATH=~/Sites/boukensha/04_api_client boukensha              # loads step 4
#   BOUKENSHA_DIR=~/projects/mybot/.boukensha boukensha                   # custom config dir
#   echo BOUKENSHA_DIR=~/projects/mybot/.boukensha > ~/.boukensharc  # ...or permanently
module BoukenshaLoader
  # Absolute path to this gem's own bundled boukensha lib.
  BUNDLED_LIB = File.expand_path("../boukensha.rb", __FILE__)

  # The rc location is itself overridable, which keeps it testable.
  RC_FILE = File.expand_path(ENV["BOUKENSHA_RC"] || "~/.boukensharc")

  # The only keys that mean anything in the rc file.
  RC_KEYS = %w[BOUKENSHA_PATH BOUKENSHA_DIR].freeze

  # Parsed rc file, memoised so unknown keys are only warned about once.
  def self.rc
    @rc ||= parse_rc
  end

  def self.parse_rc
    return {} unless File.exist?(RC_FILE)

    lines = File.readlines(RC_FILE, chomp: true)
                .map(&:strip)
                .reject { |line| line.empty? || line.start_with?("#") }
    return {} if lines.empty?

    # Legacy format: a single bare path, meaning BOUKENSHA_PATH.
    return { "BOUKENSHA_PATH" => lines.first } unless lines.any? { |line| line.include?("=") }

    lines.each_with_object({}) do |line, out|
      key, value = line.split("=", 2)
      key   = key.to_s.strip.upcase
      value = value.to_s.strip.gsub(/\A["']|["']\z/, "")
      next if value.empty?

      unless RC_KEYS.include?(key)
        warn "boukensha: ignoring unknown key '#{key}' in #{RC_FILE}"
        next
      end

      out[key] = value
    end
  end

  # Environment variable wins over the rc file.
  def self.setting(key)
    value = ENV[key]
    value.nil? || value.empty? ? rc[key] : value
  end

  # Where a setting came from, so error messages can point at the right place.
  def self.origin(key)
    value = ENV[key]
    value.nil? || value.empty? ? RC_FILE : "the #{key} environment variable"
  end

  def self.resolve
    path = setting("BOUKENSHA_PATH")

    if path
      dir  = File.expand_path(path)
      main = File.join(dir, "lib", "boukensha.rb")
      return main if File.exist?(main)

      abort <<~MSG
        boukensha: BOUKENSHA_PATH points to #{dir}
               but no lib/boukensha.rb was found there.
               Make sure it names a step folder, e.g.:
                 BOUKENSHA_PATH=~/Sites/boukensha/10_standard_tool_library
               Currently set in #{origin('BOUKENSHA_PATH')}.
      MSG
    end

    # Bundled default.
    BUNDLED_LIB
  end

  # Config reads ENV["BOUKENSHA_DIR"] when it is instantiated (inside
  # Boukensha.repl), so publishing the resolved value into ENV is all it takes.
  #
  # A missing directory is fatal rather than silently falling back: an empty
  # config yields confusing "tasks.player.model is required" errors much later.
  def self.apply_config_dir
    dir = setting("BOUKENSHA_DIR")
    return if dir.nil? || dir.empty?

    expanded = File.expand_path(dir)
    unless File.directory?(expanded)
      abort <<~MSG
        boukensha: BOUKENSHA_DIR points to #{expanded}
               but that directory does not exist.
               Fix it in #{origin('BOUKENSHA_DIR')}, or remove the setting to
               fall back to ~/.boukensha.
      MSG
    end

    ENV["BOUKENSHA_DIR"] = expanded
  end

  def self.load_and_start_repl
    apply_config_dir
    main = resolve
    step_dir = File.dirname(File.dirname(main))

    if ENV["BOUKENSHA_DEBUG"]
      puts "[boukensha] loading from: #{step_dir}"
      puts "[boukensha] config dir:   #{ENV.fetch('BOUKENSHA_DIR', '~/.boukensha (default)')}"
    end

    require main

    unless Boukensha.respond_to?(:repl)
      abort <<~MSG
        boukensha: the step at #{step_dir}
               does not support the interactive REPL (added in step 7).
               Run its examples directly, e.g.:
                 ruby #{step_dir}/examples/*.rb
               Or point BOUKENSHA_PATH at step 7 or later.
      MSG
    end

    # --no-tui falls back to the plain terminal REPL (no charm-ruby).
    no_tui = ARGV.delete("--no-tui")

    repl_opts = { tui: !no_tui }

    if ENV["MUD_NAME"]
      # Legacy env-var override still works and takes precedence over config.
      repl_opts[:working_dir] = false
      repl_opts[:mud] = {
        host:     ENV.fetch("MUD_HOST",     "localhost"),
        port:     ENV.fetch("MUD_PORT",     "4000").to_i,
        name:     ENV.fetch("MUD_NAME"),
        password: ENV.fetch("MUD_PASSWORD") { abort "boukensha: MUD_NAME is set but MUD_PASSWORD is missing." }
      }
    end
    # If MUD_NAME is not set, Boukensha.repl will fall back to config.mud_* values
    # automatically (via mud_opts_from_config inside Boukensha.repl).

    Boukensha.repl(**repl_opts)
  end
end
