# homebrew-tap

Homebrew tap for installing CLI tools published by Jilles van Gurp.

## Install

Tap this repository using its full GitHub repo name:

```bash
brew tap jillesvangurp/homebrew-tap https://github.com/jillesvangurp/homebrew-tap
```

Then install a formula, for example `ktsearch`:

```bash
brew install jillesvangurp/homebrew-tap/ktsearch
```

Bash and Zsh completions are installed automatically.

If you prefer Homebrew's GitHub shorthand, the equivalent tap name is `jillesvangurp/tap`:

```bash
brew tap jillesvangurp/tap
brew install jillesvangurp/tap/ktsearch
```

Additional formulae can be added later under [`Formula/`](/Users/jillesvangurp/git/homebrew-tap/Formula) without changing how users tap the repository.

## Current formulae

- `ktsearch`

## Formula updates

Each formula can pull native binaries from its upstream GitHub releases. For `ktsearch`, the formula installs:

- macOS Apple Silicon
- macOS Intel
- Linux x86_64

It also installs generated shell completions for:

- Bash
- Zsh

For `ktsearch`, the helper scripts shipped in the release archive are installed to:

```bash
$(brew --prefix)/share/ktsearch
```

## Adding another formula

To add another tool later:

1. Add a new formula file under [`Formula/`](/Users/jillesvangurp/git/homebrew-tap/Formula).
2. Add a matching config file under [`formulae/`](/Users/jillesvangurp/git/homebrew-tap/formulae).
3. Make sure the upstream project publishes release assets with stable names and GitHub SHA-256 digests.
4. Commit and push the changes to this tap repository.

## Updating formulae

When a new release is published for a configured tool, update all formulae with:

```bash
python3 scripts/update_formulae.py --latest
```

To update only one formula:

```bash
python3 scripts/update_formulae.py --formula ktsearch --latest
```

To pin a specific tag for one formula:

```bash
python3 scripts/update_formulae.py --formula ktsearch --tag 2.8.7
```

## GitHub Actions automation

This repo includes [`.github/workflows/update-formulae.yml`](/Users/jillesvangurp/git/homebrew-tap/.github/workflows/update-formulae.yml), which:

- runs daily
- can also be triggered manually from the Actions tab
- checks the latest releases for every configured formula in [`formulae/`](/Users/jillesvangurp/git/homebrew-tap/formulae)
- updates matching files in [`Formula/`](/Users/jillesvangurp/git/homebrew-tap/Formula) if versions changed
- runs `brew style`
- commits and pushes the formula update automatically

The generic updater logic lives in [`scripts/update_formulae.py`](/Users/jillesvangurp/git/homebrew-tap/scripts/update_formulae.py). The compatibility wrapper for the existing `ktsearch` workflow lives in [`scripts/update_ktsearch_tap.py`](/Users/jillesvangurp/git/homebrew-tap/scripts/update_ktsearch_tap.py).
