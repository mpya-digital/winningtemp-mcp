# winningtemp-mcp

MCP server connecting Claude to the Winningtemp API for live employee engagement analysis, automated reporting, and drop alerts.

## Project purpose

This server exposes Winningtemp data as tools that Claude can call. Once connected, Claude can analyze engagement trends, generate dashboards, compare against benchmarks, and power scheduled agents that post reports or alerts to Slack/Notion.

## Setup

**Requirements:** Python 3.10+

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]" httpx python-dotenv
```

**Credentials** — create a `.env` file (never commit this):
```
WT_CLIENT_ID=your-client-id
WT_CLIENT_SECRET=your-client-secret
```

**Connect to Claude Code:**
```bash
claude mcp add --transport stdio winningtemp \
  -- /path/to/.venv/bin/python /path/to/server.py
```

## Winningtemp API

- **Base URL:** `https://api.winningtemp.com`
- **Auth:** POST `/auth` with `ClientId` and `ClientSecret` headers → returns a Bearer token
- **Token usage:** `Authorization: Bearer <token>` on all subsequent requests

### Key endpoints

| Resource | Path | Notes |
|---|---|---|
| Temperature index | `GET /temperature/v?/index` | Core engagement score |
| Temperature overview | `GET /temperature/v?/overview` | Org-wide summary |
| Age distribution | `GET /temperature/v?/ageDistribution` | Demographic breakdown |
| Benchmark | `GET /benchmark/v1` | Internal benchmark |
| Benchmark (global) | `GET /benchmark/v1/global` | Industry comparison |
| eNPS | `GET /benchmark/v1/enps` | Employee Net Promoter Score |
| Teams | `GET /teams/v2` | List/filter teams |
| Team members | `GET /teams/v2/{teamId}/members` | Members of a team |
| Users | `GET /users/v2` | All users |
| Segments | `GET /segments/v1/{segmentId}` | Org segments |
| Praises | `GET /praises/v1?fromDate=` | Recognition data from a date |

## Architecture

```
Winningtemp API
      ↓
  server.py  (MCP tools)
      ↓
  Claude Code
      ↓
  Scheduled agents → Slack / Notion
```

## Available tools

- `list_teams()` — org structure
- `get_team(team_id)` — details for a specific team
- `get_team_members(team_id)` — members of a team
- `list_users()` — all users
- `get_user(user_id)` — details for a specific user
- `get_user_teams(user_id)` — teams a user belongs to
- `get_benchmark(start, end)` — internal benchmark comparison
- `get_global_benchmark(start, end)` — industry benchmark
- `get_enps(start, end)` — eNPS trend
- `get_category_benchmark(start, end)` — benchmark by survey category
- `get_smart_index(start, end)` — Winningtemp Smart Index
- `get_praises(from_date)` — recognition activity
- `get_segment(segment_id)` — org segment details

> **Note:** Temperature API endpoints (`/temperature/*`) return 404 for this account — this feature is not enabled on the current Winningtemp plan. Contact Winningtemp support to enable it.

## Important notes

- Never use `print()` in server.py — stdout is reserved for the MCP protocol. Use `sys.stderr` for debug output.
- Token from `/auth` expires — implement re-auth logic when a 401 is returned.
- Winningtemp may rate-limit — consider caching responses where freshness is not critical.
