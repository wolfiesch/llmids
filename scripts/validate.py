#!/usr/bin/env python3
"""
Validate models.json against expected schema and ranges.

Checks:
- Required fields present
- Pricing is numeric and reasonable
- Benchmark scores in valid ranges
- Context windows are valid
- Modalities are from allowed set
- Staleness warnings
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_FILE = PROJECT_ROOT / "public" / "api" / "models.json"

ALLOWED_MODALITIES = {"text", "vision", "audio_in", "audio_out", "video", "tools"}
REQUIRED_MODEL_FIELDS = {"id", "input", "output", "context", "modalities"}
REQUIRED_CONTEXT_FIELDS = {"in", "out"}

# Reasonable ranges
PRICE_MAX = 100.0  # $100/MTok max
ELO_MIN, ELO_MAX = 800, 2500
ACCURACY_MIN, ACCURACY_MAX = 0.0, 1.0
CONTEXT_MIN, CONTEXT_MAX = 1000, 10_000_000


class ValidationError(Exception):
    pass


def validate_model(provider: str, tier: str, model: dict) -> list[str]:
    """Validate a single model entry. Returns list of errors."""
    errors = []
    path = f"{provider}.{tier}"

    # Check required fields
    for field in REQUIRED_MODEL_FIELDS:
        if field not in model:
            errors.append(f"{path}: missing required field '{field}'")

    if "id" not in model:
        return errors  # Can't continue without ID

    model_id = model["id"]

    # Validate pricing (null allowed for open-weights)
    for price_field in ["input", "output"]:
        val = model.get(price_field)
        if val is not None:
            if not isinstance(val, (int, float)):
                errors.append(f"{path}.{price_field}: must be numeric, got {type(val).__name__}")
            elif val < 0:
                errors.append(f"{path}.{price_field}: negative price {val}")
            elif val > PRICE_MAX:
                errors.append(f"{path}.{price_field}: suspiciously high price ${val}/MTok")

    # Validate context
    context = model.get("context", {})
    if context:
        for ctx_field in REQUIRED_CONTEXT_FIELDS:
            if ctx_field not in context:
                errors.append(f"{path}.context: missing '{ctx_field}'")
            else:
                val = context[ctx_field]
                if not isinstance(val, int):
                    errors.append(f"{path}.context.{ctx_field}: must be int, got {type(val).__name__}")
                elif not (CONTEXT_MIN <= val <= CONTEXT_MAX):
                    errors.append(f"{path}.context.{ctx_field}: {val} outside range [{CONTEXT_MIN}, {CONTEXT_MAX}]")

    # Validate modalities
    modalities = model.get("modalities", [])
    if modalities:
        if not isinstance(modalities, list):
            errors.append(f"{path}.modalities: must be array")
        else:
            for mod in modalities:
                if mod not in ALLOWED_MODALITIES:
                    errors.append(f"{path}.modalities: unknown modality '{mod}'")
            if "text" not in modalities:
                errors.append(f"{path}.modalities: should include 'text'")

    # Validate benchmarks (if present)
    benchmarks = model.get("benchmarks", {})
    if benchmarks:
        # Arena Elo
        elo = benchmarks.get("arena_elo")
        if elo is not None:
            if not isinstance(elo, (int, float)):
                errors.append(f"{path}.benchmarks.arena_elo: must be numeric")
            elif not (ELO_MIN <= elo <= ELO_MAX):
                errors.append(f"{path}.benchmarks.arena_elo: {elo} outside range [{ELO_MIN}, {ELO_MAX}]")

        # Accuracy metrics (0-1)
        for metric in ["mmlu_pro", "gpqa", "humaneval", "arc_agi"]:
            val = benchmarks.get(metric)
            if val is not None:
                if not isinstance(val, (int, float)):
                    errors.append(f"{path}.benchmarks.{metric}: must be numeric")
                elif not (ACCURACY_MIN <= val <= ACCURACY_MAX):
                    errors.append(f"{path}.benchmarks.{metric}: {val} outside range [0, 1]")

    return errors


def validate_meta(meta: dict) -> list[str]:
    """Validate _meta block. Returns list of errors/warnings."""
    issues = []

    if "version" not in meta:
        issues.append("_meta: missing 'version'")

    if "updated" not in meta:
        issues.append("_meta: missing 'updated'")
    else:
        try:
            updated = datetime.strptime(meta["updated"], "%Y-%m-%d")
            days_old = (datetime.now() - updated).days
            if days_old > 7:
                issues.append(f"WARNING: data is {days_old} days old (updated: {meta['updated']})")
        except ValueError:
            issues.append(f"_meta.updated: invalid date format '{meta['updated']}' (expected YYYY-MM-DD)")

    return issues


def main():
    if not MODELS_FILE.exists():
        print(f"Error: {MODELS_FILE} not found")
        sys.exit(1)

    try:
        with open(MODELS_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)

    all_errors = []
    all_warnings = []
    model_count = 0

    # Validate _meta
    meta = data.get("_meta", {})
    for issue in validate_meta(meta):
        if issue.startswith("WARNING:"):
            all_warnings.append(issue)
        else:
            all_errors.append(issue)

    # Validate each provider/model
    for provider, tiers in data.items():
        if provider.startswith("_"):
            continue
        if not isinstance(tiers, dict):
            continue

        for tier, model in tiers.items():
            if tier.startswith("_"):
                continue
            if not isinstance(model, dict):
                continue

            model_count += 1
            errors = validate_model(provider, tier, model)
            all_errors.extend(errors)

    # Report
    print(f"Validated {model_count} models in {MODELS_FILE.name}")
    print("=" * 50)

    if all_warnings:
        print(f"\n{len(all_warnings)} warning(s):")
        for w in all_warnings:
            print(f"  ⚠️  {w}")

    if all_errors:
        print(f"\n{len(all_errors)} error(s):")
        for e in all_errors:
            print(f"  ❌ {e}")
        print("\nValidation FAILED")
        sys.exit(1)
    else:
        print("\n✅ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
