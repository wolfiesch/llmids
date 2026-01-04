#!/usr/bin/env python3
"""
Fetch benchmark data from multiple sources.
Outputs: data/benchmarks_raw.json

Sources:
- lmarena.ai (Chatbot Arena Elo ratings)
- artificialanalysis.ai (MMLU-Pro, GPQA, HumanEval)
- arcprize.org (ARC-AGI scores)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "benchmarks_raw.json"

# Model ID mappings (leaderboard name -> our model ID patterns)
MODEL_MAPPINGS = {
    # Anthropic
    "claude-3-5-sonnet": "claude-sonnet",
    "claude-3-opus": "claude-opus",
    "claude-3-5-haiku": "claude-haiku",
    "claude-4": "claude",
    # OpenAI
    "gpt-4o": "gpt-4",
    "gpt-5": "gpt-5",
    "o3": "o3",
    "o4": "o4",
    # Google
    "gemini-2": "gemini-2",
    "gemini-3": "gemini-3",
    "gemini-pro": "gemini",
    "gemini-flash": "gemini",
    # xAI
    "grok-2": "grok",
    "grok-3": "grok",
    "grok-4": "grok-4",
    # Mistral
    "mistral-large": "mistral-large",
    "mistral-small": "mistral-small",
    "codestral": "codestral",
    # Meta
    "llama-3": "llama-3",
}


def fetch_arena_elo() -> dict[str, int]:
    """
    Fetch Elo ratings from LMSYS Chatbot Arena leaderboard.
    Returns: {model_name: elo_score}
    """
    print("[Arena] Fetching Elo ratings from lmarena.ai...")

    try:
        # The arena uses a HuggingFace Space, try the API
        url = "https://lmarena.ai/api/leaderboard"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; llmids-scraper/1.0)"}

        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            results = {}
            for entry in data.get("data", []):
                name = entry.get("model", "").lower()
                elo = entry.get("elo")
                if name and elo:
                    results[name] = int(elo)
            print(f"[Arena] Found {len(results)} models")
            return results
    except Exception as e:
        print(f"[Arena] API failed: {e}")

    # Fallback: try scraping the HTML page
    try:
        url = "https://lmarena.ai/leaderboard"
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = {}
        # Look for table rows with model data
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                name = cells[0].get_text(strip=True).lower()
                try:
                    elo = int(cells[1].get_text(strip=True).replace(",", ""))
                    results[name] = elo
                except ValueError:
                    continue

        print(f"[Arena] Scraped {len(results)} models from HTML")
        return results
    except Exception as e:
        print(f"[Arena] HTML scrape failed: {e}")
        return {}


def fetch_artificial_analysis() -> dict[str, dict]:
    """
    Fetch benchmark scores from Artificial Analysis.
    Returns: {model_name: {mmlu_pro, gpqa, humaneval}}
    """
    print("[AA] Fetching from artificialanalysis.ai...")

    try:
        # Try their API endpoint
        url = "https://artificialanalysis.ai/api/models"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; llmids-scraper/1.0)"}

        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            results = {}
            for model in data.get("models", []):
                name = model.get("id", "").lower()
                benchmarks = model.get("benchmarks", {})
                if name and benchmarks:
                    results[name] = {
                        "mmlu_pro": benchmarks.get("mmlu_pro"),
                        "gpqa": benchmarks.get("gpqa"),
                        "humaneval": benchmarks.get("humaneval"),
                    }
            print(f"[AA] Found {len(results)} models")
            return results
    except Exception as e:
        print(f"[AA] API failed: {e}")

    # Fallback: try HuggingFace dataset mirror
    try:
        url = "https://huggingface.co/datasets/ArtificialAnalysis/results/raw/main/data.json"
        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            results = {}
            for model in data:
                name = model.get("model", "").lower()
                results[name] = {
                    "mmlu_pro": model.get("mmlu_pro"),
                    "gpqa": model.get("gpqa"),
                    "humaneval": model.get("humaneval"),
                }
            print(f"[AA] Found {len(results)} models from HF mirror")
            return results
    except Exception as e:
        print(f"[AA] HF mirror failed: {e}")

    return {}


def fetch_arc_agi() -> dict[str, float]:
    """
    Fetch ARC-AGI scores from arcprize.org leaderboard.
    Returns: {model_name: arc_agi_score}
    """
    print("[ARC] Fetching from arcprize.org...")

    try:
        url = "https://arcprize.org/api/leaderboard"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; llmids-scraper/1.0)"}

        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            results = {}
            for entry in data.get("entries", []):
                name = entry.get("model", "").lower()
                score = entry.get("score")
                if name and score is not None:
                    results[name] = float(score)
            print(f"[ARC] Found {len(results)} models")
            return results
    except Exception as e:
        print(f"[ARC] API failed: {e}")

    # Fallback: try scraping the HTML
    try:
        url = "https://arcprize.org/leaderboard"
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = {}
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name = cells[0].get_text(strip=True).lower()
                try:
                    score = float(cells[-1].get_text(strip=True).replace("%", "")) / 100
                    results[name] = score
                except ValueError:
                    continue

        print(f"[ARC] Scraped {len(results)} models from HTML")
        return results
    except Exception as e:
        print(f"[ARC] HTML scrape failed: {e}")
        return {}


def normalize_model_name(name: str) -> str | None:
    """
    Try to match a leaderboard model name to our model IDs.
    Returns the normalized name or None if no match.
    """
    name_lower = name.lower().replace("_", "-").replace(" ", "-")

    for pattern, normalized in MODEL_MAPPINGS.items():
        if pattern in name_lower:
            return normalized

    return None


def main():
    """Fetch all benchmarks and save to data/benchmarks_raw.json"""
    DATA_DIR.mkdir(exist_ok=True)

    print(f"Fetching benchmarks at {datetime.now().isoformat()}")
    print("=" * 50)

    # Fetch from all sources
    arena_elo = fetch_arena_elo()
    aa_benchmarks = fetch_artificial_analysis()
    arc_agi = fetch_arc_agi()

    # Combine into output structure
    output = {
        "_fetched": datetime.now().isoformat(),
        "_sources": {
            "arena_elo": "lmarena.ai",
            "mmlu_pro": "artificialanalysis.ai",
            "gpqa": "artificialanalysis.ai",
            "humaneval": "artificialanalysis.ai",
            "arc_agi": "arcprize.org",
        },
        "arena_elo": arena_elo,
        "artificial_analysis": aa_benchmarks,
        "arc_agi": arc_agi,
    }

    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 50)
    print(f"Saved to {OUTPUT_FILE}")

    # Summary
    print(f"\nSummary:")
    print(f"  Arena Elo: {len(arena_elo)} models")
    print(f"  Artificial Analysis: {len(aa_benchmarks)} models")
    print(f"  ARC-AGI: {len(arc_agi)} models")


if __name__ == "__main__":
    main()
