# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

llmids.dev is a static JSON endpoint that provides current frontier AI model IDs and pricing for AI coding agents. No build system, no dependencies - just static files served via Vercel CDN.

**Live URL**: https://llmids.dev

## Development

```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Run locally
vercel dev

# Deploy to production
vercel --prod
```

## Project Structure

```
public/
└── api/
    └── models.json   # The data - edit this when updating
vercel.json           # CORS headers, URL rewrites, cache settings
```

## URL Routes

Root URL serves JSON directly:
- `https://llmids.dev` → JSON
- `https://llmids.dev/models` → JSON (alias)
- `https://llmids.dev/api/models.json` → JSON (canonical)

## Updating Models

Edit `public/api/models.json` directly. Update the `updated` field.

### Model Tiers
- `flagship` - Best overall capability
- `fast` - Speed/cost optimized
- `instant` / `lite` - Fastest, lighter tasks
- `reasoning` - Extended thinking models
- `code` - Code-specialized models
- `stable` - Production-ready stable versions

### Pricing Format
```json
{
  "id": "model-id-here",
  "input": 1.00,   // USD per 1M input tokens
  "output": 5.00   // USD per 1M output tokens
}
```

## Official Pricing Sources

**Use these URLs to verify/update model IDs and pricing:**

| Provider | Pricing URL |
|----------|-------------|
| OpenAI | https://openai.com/api/pricing/ |
| Anthropic | https://claude.com/pricing (API tab) |
| Google | https://ai.google.dev/gemini-api/docs/pricing |
| xAI | https://docs.x.ai/docs/models |
| Mistral | https://mistral.ai/products/ai-studio#pricing |
| Meta | https://llama.meta.com/ (open weights, varies by provider) |

### Update Checklist

When new models are released:
1. Visit each pricing URL above
2. Update model IDs in `public/api/models.json`
3. Update pricing (input/output per 1M tokens)
4. Update the `updated` date field
5. Deploy: `vercel --prod`
6. Verify: `curl https://llmids.dev | jq .`

## Domains

All domains point to same deployment:
- llmids.dev (primary)
- latestmodel.dev
- llmhub.fyi
- llmlist.dev
