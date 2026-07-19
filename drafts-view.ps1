#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "see https://jekyllrb.com/docs/posts/"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $RepoRoot "docs")

# Ensure Ruby/Bundler are on PATH. The RubyInstaller adds them for new shells,
# but if this session was started before install, locate a Ruby bin dir.
if (-not (Get-Command bundle -ErrorAction SilentlyContinue)) {
    $rubyBin = Get-ChildItem -Path "C:\" -Directory -Filter "Ruby*-x64" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        ForEach-Object { Join-Path $_.FullName "bin" } |
        Where-Object { Test-Path (Join-Path $_ "bundle.cmd") } |
        Select-Object -First 1
    if ($rubyBin) {
        $env:PATH = $rubyBin + [IO.Path]::PathSeparator + $env:PATH
    }
    else {
        throw "Ruby/Bundler not found. Install with: winget install RubyInstallerTeam.RubyWithDevKit.3.3"
    }
}

$env:GEM_HOME = Join-Path $HOME ".gem"
$env:GEM_PATH = Join-Path $HOME ".gem"
$env:PATH = (Join-Path $env:GEM_HOME "bin") + [IO.Path]::PathSeparator + $env:PATH

bundle config set --local path "vendor/bundle" | Out-Null
bundle config set --local disable_shared_gems true | Out-Null

bundle check *> $null
if ($LASTEXITCODE -ne 0) {
    bundle install
}

bundle exec jekyll serve -D
