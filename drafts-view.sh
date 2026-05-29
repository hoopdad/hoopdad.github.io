#!/usr/bin/env bash
set -euo pipefail

echo "see https://jekyllrb.com/docs/posts/"

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT/docs"

export GEM_HOME="$HOME/.gem"
export GEM_PATH="$HOME/.gem"
export PATH="$HOME/.gem/bin:$PATH"

bundle config set --local path "vendor/bundle" >/dev/null
bundle config set --local disable_shared_gems true >/dev/null
bundle check >/dev/null 2>&1 || bundle install

bundle exec jekyll serve -D
