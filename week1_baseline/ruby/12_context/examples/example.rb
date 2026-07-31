#!/usr/bin/env ruby
# frozen_string_literal: true
#
# Step 12 — Context Management (one-shot MUD demo)
#
# The one-shot (Boukensha.run) demo; the interactive TUI is launched separately
# via bin/boukensha. Provider, model, and system prompt all come from
# tasks.player.* in ~/.boukensha/settings.yaml; the context window is looked up
# from the model id (Boukensha::Models) and drives auto-compaction.
#
# Demonstrates Boukensha::Tools::Mud, which registers gameplay tools against
# a live CircleMUD connection. Connection credentials come from
# ~/.boukensha/settings.yaml (mud: host/port/username/password) by default.
# Set BOUKENSHA_DIR to point at a different config directory.
#
#   ruby examples/example.rb
#   BOUKENSHA_DIR=iterations/.boukensha ruby examples/example.rb

ENV["BOUKENSHA_DIR"] ||= File.expand_path("../../../../.boukensha", __dir__)

$LOAD_PATH.unshift File.expand_path("../lib", __dir__)
require "boukensha"

cfg = Boukensha.config
puts "Config: #{cfg}"
puts "API key set? #{!ENV['ANTHROPIC_API_KEY'].nil?}"
puts

Boukensha.run(
  task: "Connect to the MUD, look at your surroundings, check your score, " \
        "then look at the available exits and tell me what you see.",
  # system/model/api_key all come from config automatically
  working_dir: false   # no filesystem tools needed for MUD play
  # mud: comes from config (settings.yaml mud: block) automatically
)
