#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update one or more Homebrew formulae from GitHub release metadata."
    )
    parser.add_argument(
        "--tap-repo",
        default=".",
        help="Path to the tap repository; defaults to the current directory",
    )
    parser.add_argument(
        "--config-dir",
        default="formulae",
        help="Path to the formula config directory relative to the tap repo",
    )
    parser.add_argument(
        "--formula",
        action="append",
        dest="formulae",
        help="Specific formula name to update; repeat to update more than one",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="Release tag/version to use for the selected formula")
    group.add_argument("--latest", action="store_true", help="Use the latest GitHub release")
    return parser.parse_args()


def fetch_json(url: str) -> dict:
    headers = [
        "Accept: application/vnd.github+json",
        "User-Agent: homebrew-tap-formula-update",
    ]
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers.extend(
            [
                f"Authorization: Bearer {github_token}",
                "X-GitHub-Api-Version: 2022-11-28",
            ]
        )

    try:
        result = subprocess.run(
            [
                "curl",
                "-fsSL",
                *[item for header in headers for item in ("-H", header)],
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


def load_configs(config_dir: Path, selected_formulae: list[str] | None) -> list[dict]:
    configs = []
    for config_path in sorted(config_dir.glob("*.json")):
        config = json.loads(config_path.read_text())
        config["_path"] = str(config_path)
        configs.append(config)

    if not configs:
        raise SystemExit(f"No formula configs found in {config_dir}")

    if selected_formulae:
        wanted = set(selected_formulae)
        filtered = [config for config in configs if config["formula"] in wanted]
        missing = sorted(wanted - {config["formula"] for config in filtered})
        if missing:
            raise SystemExit(f"Unknown formula config(s): {', '.join(missing)}")
        return filtered

    return configs


def asset_pattern(template: str) -> re.Pattern[str]:
    escaped = re.escape(template)
    return re.compile("^" + escaped.replace(re.escape("{version}"), r"(?P<version>.+)") + "$")


def collect_assets(release: dict, asset_templates: dict[str, str]) -> tuple[str, dict[str, dict[str, str]]]:
    version = release["tag_name"].removeprefix("v")
    patterns = {platform: asset_pattern(template) for platform, template in asset_templates.items()}
    assets: dict[str, dict[str, str]] = {}

    for asset in release.get("assets", []):
        name = asset.get("name", "")
        for platform, pattern in patterns.items():
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

    missing = [platform for platform in asset_templates if platform not in assets]
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


def filename_regex(template: str) -> str:
    escaped = re.escape(template)
    return escaped.replace(re.escape("{version}"), r'[^"]+')


def update_formula(formula_path: Path, version: str, assets: dict[str, dict[str, str]], templates: dict[str, str]) -> tuple[str, str]:
    original = formula_path.read_text()
    updated = replace_once(original, r'^\s*version "[^"]+"$', f'  version "{version}"')

    for platform, template in templates.items():
        pattern = (
            rf'^\s*url "https://github\.com/[^/]+/[^/]+/releases/download/[^"]+/{filename_regex(template)}"\n'
            rf'\s*sha256 "[0-9a-f]{{64}}"$'
        )
        replacement = f'      url "{assets[platform]["url"]}"\n      sha256 "{assets[platform]["sha256"]}"'
        updated = replace_once(updated, pattern, replacement)

    if updated != original:
        formula_path.write_text(updated)

    return original, updated


def extract_version(formula_text: str) -> str:
    match = re.search(r'^\s*version "([^"]+)"$', formula_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit("Could not find version in formula")
    return match.group(1)


def update_one(tap_repo: Path, config: dict, tag: str | None, latest: bool) -> tuple[str, str, str]:
    formula_path = tap_repo / config["formula_path"]
    if not formula_path.exists():
        raise SystemExit(f"Formula not found: {formula_path}")

    release = fetch_json(release_url(config["source_repo"], tag, latest))
    version, assets = collect_assets(release, config["asset_templates"])
    original_text, updated_text = update_formula(formula_path, version, assets, config["asset_templates"])
    old_version = extract_version(original_text)
    new_version = extract_version(updated_text)

    print(f"Checked {config['formula']} ({formula_path})")
    print(f"Version: {old_version} -> {new_version}")
    for platform in config["asset_templates"]:
        data = assets[platform]
        print(f"{platform}:")
        print(f"  url: {data['url']}")
        print(f"  sha256: {data['sha256']}")

    return config["formula"], old_version, new_version


def main() -> int:
    args = parse_args()
    tap_repo = Path(args.tap_repo).expanduser().resolve()
    config_dir = tap_repo / args.config_dir
    configs = load_configs(config_dir, args.formulae)

    if args.tag and len(configs) != 1:
        raise SystemExit("--tag can only be used when updating exactly one formula")

    for config in configs:
        update_one(tap_repo, config, args.tag, args.latest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
