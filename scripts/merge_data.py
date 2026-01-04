#!/usr/bin/env python3
"""
Merge benchmark data from benchmarks_raw.json into models.json.

Usage:
    python scripts/merge_data.py [--dry-run]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_FILE = PROJECT_ROOT / "public" / "api" / "models.json"
BENCHMARKS_FILE = PROJECT_ROOT / "data" / "benchmarks_raw.json"

# Map our model IDs to leaderboard search patterns
MODEL_TO_PATTERNS = {
    # Anthropic
    "claude-opus-4-5-20251101": ["claude-4.5-opus", "claude-opus-4.5", "claude 4.5 opus"],
    "claude-sonnet-4-5-20250929": ["claude-4.5-sonnet", "claude-sonnet-4.5", "claude 4.5 sonnet"],
    "claude-haiku-4-5-20251001": ["claude-4.5-haiku", "claude-haiku-4.5", "claude 4.5 haiku"],

    # OpenAI
    "gpt-5.2": ["gpt-5.2", "gpt5.2"],
    "gpt-5-mini": ["gpt-5-mini", "gpt5-mini"],
    "gpt-5-nano": ["gpt-5-nano", "gpt5-nano"],
    "o3": ["o3", "o3-2025"],
    "o4-mini": ["o4-mini", "o4mini"],
    "gpt-5.2-codex": ["gpt-5.2-codex", "codex-5.2"],
    "gpt-5.1-codex-max": ["gpt-5.1-codex-max", "codex-max"],
    "gpt-5.1-codex-mini": ["gpt-5.1-codex-mini", "codex-mini"],
    "gpt-4.1": ["gpt-4.1", "gpt4.1"],

    # Google
    "gemini-3-pro-preview": ["gemini-3-pro", "gemini-3.0-pro"],
    "gemini-3-flash-preview": ["gemini-3-flash", "gemini-3.0-flash"],
    "gemini-2.5-pro": ["gemini-2.5-pro"],
    "gemini-2.5-flash": ["gemini-2.5-flash"],
    "gemini-2.5-flash-lite": ["gemini-2.5-flash-lite", "gemini-flash-lite"],

    # xAI
    "grok-4-0709": ["grok-4", "grok4"],
    "grok-4-1-fast-non-reasoning": ["grok-4-1-fast", "grok-4.1-fast"],
    "grok-4-1-fast-reasoning": ["grok-4-1-reasoning", "grok-4.1-reasoning"],
    "grok-code-fast-1": ["grok-code", "grok-code-fast"],

    # Mistral
    "mistral-large-latest": ["mistral-large", "mistral large 3"],
    "mistral-small-latest": ["mistral-small", "mistral small 3"],
    "codestral-latest": ["codestral"],

    # Meta
    "llama-3.3-70b": ["llama-3.3-70b", "llama-3.3"],
    "llama-3.2-3b": ["llama-3.2-3b", "llama-3.2"],
}


def find_benchmark(data: dict, patterns: list[str], key: str = None) -> float | int | None:
    """
    Search for a model in benchmark data using patterns.
    Returns the benchmark value or None.
    """
    if not data:
        return None

    for pattern in patterns:
        pattern_lower = pattern.lower()
        for model_name, value in data.items():
            if pattern_lower in model_name.lower():
                if key and isinstance(value, dict):
                    return value.get(key)
                return value

    return None


def merge_benchmarks(models: dict, benchmarks: dict, dry_run: bool = False) -> dict:
    """
    Merge benchmark data into models.json structure.
    Returns the updated models dict.
    """
    arena_elo = benchmarks.get("arena_elo", {})
    aa_data = benchmarks.get("artificial_analysis", {})
    arc_agi = benchmarks.get("arc_agi", {})

    changes = []

    for provider, tiers in models.items():
        if provider.startswith("_"):
            continue
        if not isinstance(tiers, dict):
            continue

        for tier, model in tiers.items():
            if tier.startswith("_"):
                continue
            if not isinstance(model, dict):
                continue
            if "id" not in model:
                continue

            model_id = model["id"]
            patterns = MODEL_TO_PATTERNS.get(model_id, [model_id])

            # Find benchmarks
            new_benchmarks = {}

            elo = find_benchmark(arena_elo, patterns)
            if elo:
                new_benchmarks["arena_elo"] = elo

            mmlu = find_benchmark(aa_data, patterns, "mmlu_pro")
            if mmlu:
                new_benchmarks["mmlu_pro"] = round(mmlu, 3) if mmlu < 1 else mmlu

            gpqa = find_benchmark(aa_data, patterns, "gpqa")
            if gpqa:
                new_benchmarks["gpqa"] = round(gpqa, 3) if gpqa < 1 else gpqa

            humaneval = find_benchmark(aa_data, patterns, "humaneval")
            if humaneval:
                new_benchmarks["humaneval"] = round(humaneval, 3) if humaneval < 1 else humaneval

            arc = find_benchmark(arc_agi, patterns)
            if arc:
                new_benchmarks["arc_agi"] = round(arc, 3)

            if new_benchmarks:
                old_benchmarks = model.get("benchmarks", {})
                if new_benchmarks != old_benchmarks:
                    changes.append(f"{provider}.{tier}: {new_benchmarks}")
                    if not dry_run:
                        model["benchmarks"] = new_benchmarks

    if changes:
        print(f"Found {len(changes)} benchmark updates:")
        for change in changes:
            print(f"  {change}")
    else:
        print("No benchmark changes found")

    return models


def main():
    parser = argparse.ArgumentParser(description="Merge benchmark data into models.json")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    if not BENCHMARKS_FILE.exists():
        print(f"Error: {BENCHMARKS_FILE} not found. Run fetch_benchmarks.py first.")
        sys.exit(1)

    # Load files
    with open(MODELS_FILE) as f:
        models = json.load(f)

    with open(BENCHMARKS_FILE) as f:
        benchmarks = json.load(f)

    print(f"Benchmarks fetched: {benchmarks.get('_fetched', 'unknown')}")
    print("=" * 50)

    # Merge
    models = merge_benchmarks(models, benchmarks, dry_run=args.dry_run)

    if not args.dry_run:
        # Update metadata
        models["_meta"]["benchmark_sync"] = datetime.now().strftime("%Y-%m-%d")

        # Write back
        with open(MODELS_FILE, "w") as f:
            json.dump(models, f, indent=2)

        print("=" * 50)
        print(f"Updated {MODELS_FILE}")
    else:
        print("=" * 50)
        print("(dry run - no changes written)")


if __name__ == "__main__":
    main()
