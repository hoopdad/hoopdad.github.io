#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$REPO_ROOT/docs"

if ! command -v ruby >/dev/null 2>&1; then
  echo "Ruby is not installed. Install Ruby first, then re-run this script."
  exit 1
fi

if ! command -v gem >/dev/null 2>&1; then
  echo "RubyGems is not available. Install RubyGems first, then re-run this script."
  exit 1
fi

export GEM_HOME="$HOME/.gem"
export GEM_PATH="$HOME/.gem"
export PATH="$HOME/.gem/bin:$PATH"

gem install --user-install bundler --no-document

cd "$DOCS_DIR"
bundle config set --local path "vendor/bundle"
bundle config set --local disable_shared_gems true
bundle install

echo "Jekyll dependencies installed locally for this repo."
echo "Run: ./drafts-view.sh"
