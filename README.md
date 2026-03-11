# homebrew-tap

Homebrew tap for installing the `ktsearch` CLI.

## Install

Tap this repository:

```bash
brew tap jillesvangurp/tap https://github.com/jillesvangurp/homebrew-tap
```

Then install `ktsearch`:

```bash
brew install ktsearch
```

Bash and Zsh completions are installed automatically.

You can also install it in one step without tapping first:

```bash
brew install jillesvangurp/tap/ktsearch
```

## What gets installed

The formula installs the native `ktsearch` binary from the GitHub release assets for:

- macOS Apple Silicon
- macOS Intel
- Linux x86_64

It also installs generated shell completions for:

- Bash
- Zsh

The helper scripts shipped in the release archive are installed to:

```bash
$(brew --prefix)/share/ktsearch
```

## Updating the formula

When a new `ktsearch` release is published:

1. Update the version in `Formula/ktsearch.rb`.
2. Replace the download URLs and SHA-256 checksums for each platform.
3. Commit and push the changes to this tap repository.

You can do that manually with:

```bash
python3 scripts/update_ktsearch_tap.py --latest
```

## GitHub Actions automation

This repo includes [`.github/workflows/update-ktsearch-tap.yml`](/Users/jillesvangurp/git/homebrew-tap/.github/workflows/update-ktsearch-tap.yml), which:

- runs daily
- can also be triggered manually from the Actions tab
- checks the latest `jillesvangurp/kt-search` release
- updates `Formula/ktsearch.rb` if the version changed
- runs `brew style`
- commits and pushes the formula update automatically

The updater logic lives in [`scripts/update_ktsearch_tap.py`](/Users/jillesvangurp/git/homebrew-tap/scripts/update_ktsearch_tap.py).
