# llmids.dev

> Current frontier model IDs, specs, and benchmarks. For AI agents.

A dead-simple JSON endpoint that AI coding agents can fetch to get accurate, up-to-date model information from major AI labs.

## The Problem

AI coding agents have training cutoffs. When building LLM pipelines:
- They default to outdated model IDs
- They don't know context window limits or pricing
- They can't compare model capabilities
- Users waste time providing this context manually

## The Solution

One URL. Current model data. No auth required.

```
GET https://llmids.dev
```

## What's Included

| Field | Example |
|-------|---------|
| Model ID | `claude-opus-4-5-20251101` |
| Pricing | `$5.00 / $25.00 per MTok` |
| Context window | `200K in / 32K out` |
| Modalities | `text, vision, tools` |
| Benchmarks | Arena Elo, MMLU, HumanEval, ARC-AGI |
| Release date | `2025-11-01` |
| Knowledge cutoff | `2025-04` |
| Docs URL | Link to official docs |

## Usage

### For AI Agents

Add to your system prompt:
```
Before writing code that uses LLM APIs, fetch https://llmids.dev to get current model IDs, pricing, and capabilities.
```

### In Code

```python
import requests

models = requests.get("https://llmids.dev").json()

# Get the current flagship Anthropic model
claude = models["anthropic"]["flagship"]
print(f"Model: {claude['id']}")           # claude-opus-4-5-20251101
print(f"Context: {claude['context']}")    # {'in': 200000, 'out': 32000}
print(f"Price: ${claude['input']}/MTok")  # $5.00/MTok
print(f"Modalities: {claude['modalities']}")  # ['text', 'vision', 'tools']
```

```javascript
const data = await fetch('https://llmids.dev').then(r => r.json());

// Compare flagship models by Arena Elo
const flagships = [
  { name: 'Claude Opus 4.5', ...data.anthropic.flagship },
  { name: 'GPT-5.2', ...data.openai.flagship },
  { name: 'Gemini 3 Pro', ...data.google.flagship },
];

flagships
  .filter(m => m.benchmarks?.arena_elo)
  .sort((a, b) => b.benchmarks.arena_elo - a.benchmarks.arena_elo)
  .forEach(m => console.log(`${m.name}: ${m.benchmarks.arena_elo} Elo`));
```

## Response Format

```json
{
  "_meta": {
    "version": "2.0.0",
    "updated": "2026-01-02",
    "benchmark_sync": "2026-01-01"
  },
  "anthropic": {
    "flagship": {
      "id": "claude-opus-4-5-20251101",
      "input": 5.00,
      "output": 25.00,
      "context": {"in": 200000, "out": 32000},
      "modalities": ["text", "vision", "tools"],
      "benchmarks": {
        "arena_elo": 1380,
        "mmlu_pro": 0.78,
        "humaneval": 0.92
      },
      "released": "2025-11-01",
      "cutoff": "2025-04",
      "docs": "https://docs.anthropic.com/..."
    }
  }
}
```

## Model Tiers

| Tier | Meaning |
|------|---------|
| `flagship` | Best overall capability |
| `fast` | Optimized for speed/cost |
| `instant` / `lite` | Fastest, lighter tasks |
| `reasoning` | Extended thinking models |
| `code` | Code-specialized models |

## Providers

- Anthropic (Claude)
- OpenAI (GPT, o-series, Codex)
- Google (Gemini)
- xAI (Grok)
- Mistral
- Meta (Llama - open weights)

## Modalities

| Flag | Meaning |
|------|---------|
| `text` | Text input/output |
| `vision` | Image input |
| `audio_in` | Audio input |
| `audio_out` | Audio/speech output |
| `video` | Video input |
| `tools` | Function calling |

## Benchmarks

| Metric | Range | Source |
|--------|-------|--------|
| `arena_elo` | ~800-2000 | lmarena.ai |
| `mmlu_pro` | 0-1 | artificialanalysis.ai |
| `gpqa` | 0-1 | artificialanalysis.ai |
| `humaneval` | 0-1 | artificialanalysis.ai |
| `arc_agi` | 0-1 | arcprize.org |

## Updates

- **Model IDs/pricing**: Updated within 24-48 hours of new releases
- **Benchmarks**: Synced weekly from leaderboards

## Development

```bash
npm i -g vercel
vercel dev      # Local
vercel --prod   # Deploy
```

## License

MIT
