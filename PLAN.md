# ModelList - Frontier Model Registry

> A dead-simple, public JSON endpoint for AI agents to fetch current model IDs

## Problem Statement

AI coding agents (Claude Code, OpenAI Codex, etc.) have training cutoffs that lag behind model releases. When building LLM pipelines via these agents:
- They default to outdated model IDs
- They argue when given newer model names they don't recognize
- Users waste time convincing agents that new models exist

**Solution**: A minimal, public, no-auth URL that agents can fetch to get accurate, current model IDs.

## Design Principles

1. **Minimal** - Just model IDs and an updated timestamp. No benchmarks, no pricing, no token counts.
2. **Agent-friendly** - Clean JSON that parses in one shot. Short, memorable URL.
3. **No auth** - Public endpoint, no API keys required.
4. **Fast** - Static file on CDN. Sub-100ms response.
5. **Accurate** - Manually curated to ensure correctness. Updated within 24-48h of new releases.

## API Design

### Primary Endpoint
```
GET https://{domain}/api/models.json
```

### Response Schema
```json
{
  "updated": "2025-12-28T10:00:00Z",
  "models": {
    "anthropic": {
      "flagship": "claude-opus-4-5-20251101",
      "fast": "claude-sonnet-4-20250514",
      "instant": "claude-haiku-3-5-20241022"
    },
    "openai": {
      "flagship": "gpt-4.1-2025-04-14",
      "fast": "gpt-4.1-mini-2025-04-14",
      "reasoning": "o3-2025-04-16"
    },
    "google": {
      "flagship": "gemini-2.5-pro",
      "fast": "gemini-2.5-flash"
    },
    "xai": {
      "flagship": "grok-3",
      "fast": "grok-3-fast"
    },
    "meta": {
      "flagship": "llama-4-maverick",
      "open": "llama-4-scout"
    }
  }
}
```

### Model Tiers (Semantic Categories)
| Tier | Meaning |
|------|---------|
| `flagship` | Best overall capability, highest intelligence |
| `fast` | Optimized for speed/cost, still very capable |
| `instant` | Fastest response, lighter tasks |
| `reasoning` | Extended thinking / chain-of-thought models |
| `open` | Open-weight models |

## Domain Candidates

| Domain | Status | Notes |
|--------|--------|-------|
| `modelids.com` | ✅ AVAILABLE | Best .com option, clear meaning |
| `modelid.dev` | ✅ AVAILABLE (no DNS) | Short, dev-friendly |
| `llmid.dev` | ✅ AVAILABLE (no DNS) | Very short |
| `modellist.dev` | ✅ AVAILABLE (no DNS) | Matches project name |
| `llmlist.dev` | ✅ AVAILABLE (no DNS) | Alternative |
| `models.fyi` | ❌ TAKEN | Has DNS records |
| `llmlist.com` | ❌ TAKEN | - |
| `frontiermodels.com` | ❌ TAKEN | - |
| `currentmodels.com` | ❌ TAKEN | - |

**Recommendation**: `modelids.com` - short, clear, .com credibility

## Tech Stack

- **Framework**: None (static JSON file)
- **Hosting**: Vercel or Cloudflare Pages (free tier, global CDN)
- **Updates**: Manual edit + git push (could automate later)
- **Domain**: TBD - purchase shortest available option

## Project Structure

```
ModelList/
├── public/
│   └── api/
│       └── models.json      # The actual data
├── index.html               # Simple landing page (optional)
├── vercel.json              # Deployment config
├── PLAN.md                  # This file
└── README.md                # Public documentation
```

## Implementation Steps

### Phase 1: Core (MVP)
- [x] Create plan document
- [x] Scaffold project structure
- [x] Create models.json with current model IDs
- [x] Create minimal landing page
- [x] Create vercel.json with CORS headers
- [ ] Deploy to Vercel
- [ ] Test endpoint

### Phase 2: Domain & Polish
- [ ] Research domain availability
- [ ] Purchase domain
- [ ] Configure custom domain on Vercel
- [ ] Add CORS headers for browser fetch
- [ ] Create README for public repo

### Phase 3: Maintenance & Growth (Future)
- [ ] Set up RSS/notification for model releases from major labs
- [ ] Consider adding more providers (Mistral, Cohere, etc.)
- [ ] Optional: Add `/api/models/{provider}.json` per-provider endpoints
- [ ] Optional: Historical versions endpoint

## Usage Examples

### For AI Agents
```
"Before writing code that uses LLM APIs, fetch https://models.fyi/api/models.json
to get the current model IDs."
```

### In Code
```python
import requests
models = requests.get("https://models.fyi/api/models.json").json()
client = Anthropic()
response = client.messages.create(
    model=models["models"]["anthropic"]["flagship"],
    # ...
)
```

## Changelog

| Date | Update |
|------|--------|
| 12/28/2025 02:11 AM PST | Initial plan created |
| 12/28/2025 02:15 AM PST | Scaffolded project: models.json, index.html, vercel.json, README.md, git initialized |
| 12/28/2025 02:33 AM PST | Deployed to Vercel at model-list.vercel.app |
| 12/28/2025 02:37 AM PST | Domain research: modelids.com available, updated model IDs from official docs |

