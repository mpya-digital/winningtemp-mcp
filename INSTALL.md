# Installation & Setup

## Prerequisites

- Python 3.10 or higher (3.12 recommended)
- [Claude Code](https://claude.ai/code) installed
- Admin access to your Winningtemp account

---

## 1. Clone the repo

```bash
git clone https://github.com/mpya-digital/winningtemp-mcp.git
cd winningtemp-mcp
```

---

## 2. Create a Python virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install "mcp[cli]" httpx python-dotenv
```

---

## 4. Add your Winningtemp credentials

Get your ClientId and ClientSecret from Winningtemp:
1. Log in as an admin
2. Go to **Settings → Apps / Developer API**
3. Click **Generate** — copy the secret immediately, it won't be shown again

Then create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
WT_CLIENT_ID=your-client-id-here
WT_CLIENT_SECRET=your-client-secret-here
```

> ⚠️ Never commit `.env` to git — it is already listed in `.gitignore`.

---

## 5. Connect to Claude Code

Run this once to register the MCP server:

```bash
claude mcp add --transport stdio winningtemp \
  -- /path/to/winningtemp-mcp/.venv/bin/python \
     /path/to/winningtemp-mcp/server.py
```

Replace `/path/to/winningtemp-mcp` with the absolute path to where you cloned the repo. Example for macOS:

```bash
claude mcp add --transport stdio winningtemp \
  -- /Users/yourname/Documents/Projects/winningtemp-mcp/.venv/bin/python \
     /Users/yourname/Documents/Projects/winningtemp-mcp/server.py
```

---

## 6. Verify the connection

In Claude Code, run:

```
/mcp
```

You should see `winningtemp` listed as a connected server with 15 tools available.

---

## 7. Test it

Try asking Claude:

- *"List all teams from Winningtemp"*
- *"Get the temperature index for the last 30 days"*
- *"What's our current eNPS score?"*

---

## Available tools

| Tool | What it does |
|---|---|
| `get_temperature_index` | Engagement scores over a date range |
| `get_temperature_overview` | Org-wide summary with category breakdowns |
| `get_temperature_age_distribution` | Scores by age group |
| `get_benchmark` | Internal benchmark index |
| `get_global_benchmark` | Industry benchmark comparison |
| `get_enps` | Employee Net Promoter Score |
| `get_category_benchmark` | Benchmark by survey category |
| `get_smart_index` | Winningtemp Smart Index score |
| `list_teams` | All teams in the org |
| `get_team` | Details for a specific team |
| `get_team_members` | Members of a specific team |
| `list_users` | All users in the org |
| `get_user` | Details for a specific user |
| `get_user_teams` | Teams a user belongs to |
| `get_praises` | Recognition/praise data from a date |

---

## Troubleshooting

**Server not showing in `/mcp`**
- Make sure you used the absolute path to both `python` and `server.py`
- Confirm the `.venv` is activated and dependencies are installed

**Authentication errors**
- Double-check `WT_CLIENT_ID` and `WT_CLIENT_SECRET` in your `.env`
- If you lost the secret, generate a new pair in Winningtemp Settings

**`mcp[cli]` install fails**
- Confirm you are using Python 3.10+: `python3 --version`
- Upgrade pip first: `pip install --upgrade pip`
