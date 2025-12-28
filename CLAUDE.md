# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

ModelList is a static JSON endpoint that provides current frontier AI model IDs for AI coding agents. No build system, no dependencies - just static files served via Vercel CDN.

## Development

```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Run locally
vercel dev

# Deploy to production
vercel --prod
```

Local server runs at `http://localhost:3000`. Test the endpoint at `/api/models.json`.

## Project Structure

```
public/
├── api/
│   └── models.json   # The data - edit this when updating model IDs
└── index.html        # Landing page
vercel.json           # CORS headers, URL rewrites, cache settings
```

## Updating Models

Edit `public/api/models.json` directly. Update the `updated` timestamp when making changes.

Model tiers:
- `flagship` - Best overall capability
- `fast` - Speed/cost optimized
- `instant` - Fastest, lighter tasks
- `reasoning` - Extended thinking models
- `code` - Code-specialized models

## URL Routes

Configured in `vercel.json`:
- `/api/models.json` - Primary endpoint
- `/models.json` - Alias (rewrites to above)
- `/models` - Alias (rewrites to above)

CORS is enabled for all origins (`*`) on `/api/*` routes.
