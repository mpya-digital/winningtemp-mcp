# Architecture

## Overview

```
┌─────────────────────────────────────────┐
│           Claude Desktop App            │
│                                         │
│  User asks: "What's our eNPS score?"   │
│         ↓                               │
│    MCP tool call (stdio)                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         winningtemp-mcp server          │
│              (server.py)                │
│                                         │
│  1. Check token cache                   │
│  2. Auth if expired → POST /auth        │
│  3. Call Winningtemp API endpoint       │
│  4. Unwrap paginated response           │
│  5. Return data to Claude               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Winningtemp REST API            │
│      https://api.winningtemp.com        │
│                                         │
│  Auth:      POST /auth                  │
│  Benchmark: GET  /benchmark/v1/*        │
│  Teams:     GET  /teams/v2/*            │
│  Users:     GET  /users/v2/*            │
│  Segments:  GET  /segments/v1/*         │
│  Praises:   GET  /praises/v1            │
└─────────────────────────────────────────┘
```

## Token management

The server caches the Bearer token in memory and refreshes it 60 seconds before expiry (`expires_in - 60`). No token is ever written to disk.

## Transport

The server runs over **stdio** — Claude Desktop spawns the process and communicates over stdin/stdout. Stdout is reserved for the MCP protocol; all debug output goes to stderr.

## Deployment modes

| Mode | Command | When to use |
|---|---|---|
| Local source | `python server.py` | Development / debugging |
| Release binary | `~/.local/bin/winningtemp-mcp` | All other team members |

Switch between modes with `scripts/switch-mcp.sh local` or `scripts/switch-mcp.sh release`.

## Known limitations

- **Temperature API** (`/temperature/*`) returns 404 — not enabled on current Winningtemp plan. Contact Winningtemp support to enable.
- No persistent cache — each Claude session fetches fresh data from the API.
- No proactive alerts — Claude only fetches data when asked. For scheduled alerts, a separate agent/cron job is needed.
