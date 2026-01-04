# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

llmids.dev is a static JSON endpoint that provides current frontier AI model IDs, specifications, pricing, and benchmark scores for AI coding agents. No build system - just static files served via Vercel CDN, with Python scripts for semi-automated benchmark updates.

**Live URL**: https://llmids.dev

## Development

```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Run locally
vercel dev

# Deploy to production
vercel --prod

# Install Python dependencies (for scrapers)
pip install -r requirements.txt
```

## Project Structure

```
public/
└── api/
    └── models.json       # The data - main JSON file
scripts/
├── fetch_benchmarks.py   # Scrape benchmarks from leaderboards
├── merge_data.py         # Merge benchmarks into models.json
└── validate.py           # Validate JSON schema
data/                     # Scraped data (gitignored)
vercel.json               # CORS headers, URL rewrites, cache settings
```

## URL Routes

Root URL serves JSON directly:
- `https://llmids.dev` → JSON
- `https://llmids.dev/models` → JSON (alias)
- `https://llmids.dev/api/models.json` → JSON (canonical)

## Schema v2.0

Each model includes:

```json
{
  "id": "claude-opus-4-5-20251101",
  "input": 5.00,
  "output": 25.00,
  "context": {"in": 200000, "out": 32000},
  "modalities": ["text", "vision", "tools"],
  "benchmarks": {
    "arena_elo": 1380,
    "mmlu_pro": 0.78,
    "gpqa": 0.72,
    "humaneval": 0.92,
    "arc_agi": 0.38
  },
  "released": "2025-11-01",
  "cutoff": "2025-04",
  "docs": "https://docs.anthropic.com/en/docs/about-claude/models"
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Official API model ID |
| `input` | float/null | USD per 1M input tokens |
| `output` | float/null | USD per 1M output tokens |
| `context.in` | int | Max input tokens |
| `context.out` | int | Max output tokens |
| `modalities` | array | Supported: text, vision, audio_in, audio_out, video, tools |
| `benchmarks` | object | Benchmark scores (see below) |
| `released` | string | Release date (YYYY-MM or YYYY-MM-DD) |
| `cutoff` | string | Knowledge cutoff (YYYY-MM) |
| `docs` | string | Official documentation URL |

### Benchmark Fields

| Benchmark | Range | Source |
|-----------|-------|--------|
| `arena_elo` | 800-2000 | lmarena.ai |
| `mmlu_pro` | 0-1 | artificialanalysis.ai |
| `gpqa` | 0-1 | artificialanalysis.ai |
| `humaneval` | 0-1 | artificialanalysis.ai |
| `arc_agi` | 0-1 | arcprize.org |

### Model Tiers

- `flagship` - Best overall capability
- `fast` - Speed/cost optimized
- `instant` / `lite` - Fastest, lighter tasks
- `reasoning` - Extended thinking models
- `code` - Code-specialized models
- `stable` - Production-ready stable versions

## Updating Data

### Weekly Benchmark Update

```bash
# 1. Scrape latest benchmarks
python scripts/fetch_benchmarks.py

# 2. Merge into models.json
python scripts/merge_data.py

# 3. Validate
python scripts/validate.py

# 4. Deploy
vercel --prod

# 5. Verify
curl https://llmids.dev | jq '.anthropic.flagship.benchmarks'
```

### On New Model Release

1. Edit `public/api/models.json` directly
2. Add core fields: id, pricing, context, modalities
3. Update `_meta.updated` date
4. Run `python scripts/validate.py`
5. Deploy: `vercel --prod`

Benchmarks will be picked up in the next weekly sync once models appear on leaderboards.

## Official Sources

### Pricing & Specs

| Provider | URL |
|----------|-----|
| Anthropic | https://claude.com/pricing |
| OpenAI | https://openai.com/api/pricing/ |
| Google | https://ai.google.dev/gemini-api/docs/pricing |
| xAI | https://docs.x.ai/docs/models |
| Mistral | https://mistral.ai/products/ai-studio#pricing |
| Meta | https://llama.meta.com/ |

### Benchmarks

| Source | URL |
|--------|-----|
| Arena Elo | https://lmarena.ai/leaderboard |
| MMLU/GPQA/HumanEval | https://artificialanalysis.ai/models |
| ARC-AGI | https://arcprize.org/leaderboard |

## Domains

All domains point to same deployment:
- llmids.dev (primary)
- latestmodel.dev
- llmhub.fyi
- llmlist.dev
