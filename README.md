# ModelList

> Current frontier model IDs. For AI agents.

A dead-simple JSON endpoint that AI coding agents can fetch to get accurate, up-to-date model IDs from major AI labs.

## The Problem

AI coding agents (Claude Code, Cursor, Codex) have training cutoffs. When building LLM pipelines:
- They default to outdated model IDs
- They don't recognize newer models
- Users waste time convincing agents that new models exist

## The Solution

One URL. Current model IDs. No auth required.

```
GET /api/models.json
```

## Usage

### For AI Agents

Add this to your prompt:
```
Before writing code that uses LLM APIs, fetch /api/models.json to get current model IDs.
```

### In Code

```python
import requests

models = requests.get("https://your-domain.com/api/models.json").json()

# Use the current flagship model
model_id = models["models"]["anthropic"]["flagship"]
# Returns: "claude-opus-4-5-20251101"
```

```javascript
const models = await fetch('/api/models.json').then(r => r.json());
console.log(models.models.openai.flagship);
// Returns: "gpt-4o"
```

## Response Format

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
      "flagship": "gpt-4o",
      "fast": "gpt-4o-mini",
      "reasoning": "o3"
    }
  }
}
```

## Model Tiers

| Tier | Meaning |
|------|---------|
| `flagship` | Best overall capability |
| `fast` | Optimized for speed/cost |
| `instant` | Fastest, lighter tasks |
| `reasoning` | Extended thinking models |
| `code` | Code-specialized models |

## Providers

- Anthropic
- OpenAI
- Google
- xAI
- Mistral
- Meta

## Development

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev

# Deploy
vercel --prod
```

## Updates

Model IDs are updated manually within 24-48 hours of new releases.

## License

MIT
