#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ASSET_PATTERNS = {
    "darwin-arm64": re.compile(r"^ktsearch-(?P<version>.+)-darwin-arm64\.tar\.gz$"),
    "darwin-x64": re.compile(r"^ktsearch-(?P<version>.+)-darwin-x64\.tar\.gz$"),
    "linux-x64": re.compile(r"^ktsearch-(?P<version>.+)-linux-x64\.tar\.gz$"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the ktsearch Homebrew tap formula from a GitHub release."
    )
    parser.add_argument(
        "--tap-repo",
        default=".",
        help="Path to the tap repository; defaults to the current directory",
    )
    parser.add_argument(
        "--formula",
        default="Formula/ktsearch.rb",
        help="Formula path relative to the tap repo",
    )
    parser.add_argument(
        "--source-repo",
        default="jillesvangurp/kt-search",
        help="GitHub source repository in owner/name form",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="Release tag/version to use, e.g. 2.8.7")
    group.add_argument("--latest", action="store_true", help="Use the latest GitHub release")
    return parser.parse_args()


def fetch_json(url: str) -> dict:
    try:
        result = subprocess.run(
            [
                "curl",
                "-fsSL",
                "-H",
                "Accept: application/vnd.github+json",
                "-H",
                "User-Agent: homebrew-tap-release-update",
                url,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or "curl failed"
        raise SystemExit(f"GitHub API request failed: {stderr}") from exc
    return json.loads(result.stdout)


def release_url(source_repo: str, tag: str | None, latest: bool) -> str:
    base = f"https://api.github.com/repos/{source_repo}/releases"
    if latest:
        return f"{base}/latest"
    return f"{base}/tags/{tag}"


def collect_assets(release: dict) -> tuple[str, dict[str, dict[str, str]]]:
    version = release["tag_name"].removeprefix("v")
    assets: dict[str, dict[str, str]] = {}

    for asset in release.get("assets", []):
        name = asset.get("name", "")
        for platform, pattern in ASSET_PATTERNS.items():
            match = pattern.match(name)
            if not match:
                continue
            digest = asset.get("digest", "")
            if not digest.startswith("sha256:"):
                raise SystemExit(f"Asset {name} is missing a sha256 digest in the release metadata")
            assets[platform] = {
                "url": asset["browser_download_url"],
                "sha256": digest.split(":", 1)[1],
                "version": match.group("version"),
            }

    missing = [platform for platform in ASSET_PATTERNS if platform not in assets]
    if missing:
        raise SystemExit(f"Missing expected release assets: {', '.join(missing)}")

    mismatched = [
        platform for platform, data in assets.items() if data["version"].removeprefix("v") != version
    ]
    if mismatched:
        pairs = ", ".join(f"{platform}={assets[platform]['version']}" for platform in mismatched)
        raise SystemExit(f"Release tag/version mismatch for assets: {pairs}")

    return version, assets


def replace_once(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Expected to replace exactly once for pattern: {pattern}")
    return updated


def update_formula(formula_path: Path, version: str, assets: dict[str, dict[str, str]]) -> tuple[str, str]:
    original = formula_path.read_text()
    updated = original

    updated = replace_once(updated, r'^\s*version "[^"]+"$', f'  version "{version}"')
    updated = replace_once(
        updated,
        r'^\s*url "https://github\.com/jillesvangurp/kt-search/releases/download/[^"]+/ktsearch-[^"]+-darwin-arm64\.tar\.gz"\n\s*sha256 "[0-9a-f]{64}"$',
        f'      url "{assets["darwin-arm64"]["url"]}"\n      sha256 "{assets["darwin-arm64"]["sha256"]}"',
    )
    updated = replace_once(
        updated,
        r'^\s*url "https://github\.com/jillesvangurp/kt-search/releases/download/[^"]+/ktsearch-[^"]+-darwin-x64\.tar\.gz"\n\s*sha256 "[0-9a-f]{64}"$',
        f'      url "{assets["darwin-x64"]["url"]}"\n      sha256 "{assets["darwin-x64"]["sha256"]}"',
    )
    updated = replace_once(
        updated,
        r'^\s*url "https://github\.com/jillesvangurp/kt-search/releases/download/[^"]+/ktsearch-[^"]+-linux-x64\.tar\.gz"\n\s*sha256 "[0-9a-f]{64}"$',
        f'      url "{assets["linux-x64"]["url"]}"\n      sha256 "{assets["linux-x64"]["sha256"]}"',
    )

    if updated == original:
        return original, updated

    formula_path.write_text(updated)
    return original, updated


def extract_version(formula_text: str) -> str:
    match = re.search(r'^\s*version "([^"]+)"$', formula_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit("Could not find version in formula")
    return match.group(1)


def main() -> int:
    args = parse_args()
    tap_repo = Path(args.tap_repo).expanduser().resolve()
    formula_path = tap_repo / args.formula

    if not formula_path.exists():
        raise SystemExit(f"Formula not found: {formula_path}")

    release = fetch_json(release_url(args.source_repo, args.tag, args.latest))
    version, assets = collect_assets(release)
    original_text, updated_text = update_formula(formula_path, version, assets)
    old_version = extract_version(original_text)
    new_version = extract_version(updated_text)

    print(f"Checked {formula_path}")
    print(f"Version: {old_version} -> {new_version}")
    for platform in ("darwin-arm64", "darwin-x64", "linux-x64"):
        data = assets[platform]
        print(f"{platform}:")
        print(f"  url: {data['url']}")
        print(f"  sha256: {data['sha256']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
