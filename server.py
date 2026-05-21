import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("winningtemp")

BASE_URL = "https://api.winningtemp.com"
_token: str | None = None
_token_expires_at: datetime = datetime.min


async def get_token() -> str:
    global _token, _token_expires_at
    if _token and datetime.now() < _token_expires_at:
        return _token

    client_id = os.getenv("WT_CLIENT_ID")
    client_secret = os.getenv("WT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("WT_CLIENT_ID and WT_CLIENT_SECRET must be set in .env")

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/auth",
            headers={"ClientId": client_id, "ClientSecret": client_secret, "accept": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
        _token = data["access_token"]
        _token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
        return _token


async def get(path: str, params: dict = {}) -> dict:
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            params={k: v for k, v in params.items() if v is not None},
        )
        r.raise_for_status()
        body = r.json()
        # Unwrap paginated responses: {"data": [...], "pagination": {...}}
        if isinstance(body, dict) and "data" in body:
            return body["data"]
        return body


# ── Temperature ──────────────────────────────────────────────────────────────

@mcp.tool()
async def get_temperature_index(start: str, end: str) -> str:
    """Get the engagement temperature index for the organisation over a date range.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/temperature/v2/index", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_temperature_overview(start: str, end: str) -> str:
    """Get an org-wide temperature overview including category breakdowns.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/temperature/v2/overview", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_temperature_age_distribution(start: str, end: str) -> str:
    """Get temperature scores broken down by age group.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/temperature/v2/ageDistribution", {"Start": start, "End": end})
    return str(data)


# ── Benchmark ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_benchmark(start: str, end: str) -> str:
    """Get the internal benchmark index for the organisation.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/benchmark/v1", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_global_benchmark(start: str, end: str) -> str:
    """Get the global industry benchmark to compare your org against.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/benchmark/v1/global", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_enps(start: str, end: str) -> str:
    """Get eNPS (employee Net Promoter Score) over a date range.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/benchmark/v1/enps", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_category_benchmark(start: str, end: str) -> str:
    """Get benchmark scores broken down by survey category.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/benchmark/v1/category", {"Start": start, "End": end})
    return str(data)


@mcp.tool()
async def get_smart_index(start: str, end: str) -> str:
    """Get the Winningtemp Smart Index score for the organisation.
    Args:
        start: Start date in ISO format (YYYY-MM-DD)
        end: End date in ISO format (YYYY-MM-DD)
    """
    data = await get("/benchmark/v1/smartIndex", {"Start": start, "End": end})
    return str(data)


# ── Teams ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_teams(team_type: str = None, category: str = None) -> str:
    """List all teams in the organisation.
    Args:
        team_type: Optional filter — 'Core' or 'Flex'
        category: Optional filter — e.g. 'Department', 'Office', 'Region', 'Country'
    """
    data = await get("/teams/v2", {"teamType": team_type, "category": category})
    return str(data)


@mcp.tool()
async def get_team(team_id: str) -> str:
    """Get details for a specific team.
    Args:
        team_id: The UUID of the team
    """
    data = await get(f"/teams/v2/{team_id}")
    return str(data)


@mcp.tool()
async def get_team_members(team_id: str) -> str:
    """List all members of a specific team.
    Args:
        team_id: The UUID of the team
    """
    data = await get(f"/teams/v2/{team_id}/members")
    return str(data)


# ── Users ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_users() -> str:
    """List all users in the organisation."""
    data = await get("/users/v2")
    return str(data)


@mcp.tool()
async def get_user(user_id: str) -> str:
    """Get details for a specific user.
    Args:
        user_id: The UUID of the user
    """
    data = await get(f"/users/v2/{user_id}")
    return str(data)


@mcp.tool()
async def get_user_teams(user_id: str) -> str:
    """Get all teams a user belongs to.
    Args:
        user_id: The UUID of the user
    """
    data = await get(f"/users/v2/{user_id}/teams")
    return str(data)


# ── Segments ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_segment(segment_id: str) -> str:
    """Get a specific segment.
    Args:
        segment_id: The UUID of the segment
    """
    data = await get(f"/segments/v1/{segment_id}")
    return str(data)


# ── Praises ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_praises(from_date: str) -> str:
    """Get all user praises (recognition) from a specific date onwards.
    Args:
        from_date: Start date in ISO format (YYYY-MM-DD)
    """
    data = await get("/praises/v1", {"fromDate": from_date})
    return str(data)


if __name__ == "__main__":
    print("Starting Winningtemp MCP server...", file=sys.stderr)
    mcp.run(transport="stdio")
