#!/usr/bin/env bash
# Switch the winningtemp MCP server between running from local source
# and the latest GitHub release binary.
#
# Usage:
#   scripts/switch-mcp.sh local     # run from source (uses .venv/bin/python + server.py)
#   scripts/switch-mcp.sh release   # download latest release binary from GitHub
#   scripts/switch-mcp.sh status    # show which binary Claude Desktop is currently configured to use

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_PYTHON="$REPO_ROOT/.venv/bin/python"
LOCAL_SERVER="$REPO_ROOT/server.py"
RELEASE_BIN="$HOME/.local/bin/winningtemp-mcp"
CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
SERVER_NAME="winningtemp"

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ missing dependency: $1" >&2; exit 1; }
}

set_command() {
  local new_cmd="$1"
  local new_args="${2:-null}"
  require jq
  [ -f "$CONFIG" ] || { echo "❌ Claude Desktop config not found at $CONFIG" >&2; exit 1; }

  local tmp
  tmp="$(mktemp)"
  jq --arg name "$SERVER_NAME" --arg cmd "$new_cmd" --argjson args "$new_args" \
    '.mcpServers[$name].command = $cmd | .mcpServers[$name].args = $args' "$CONFIG" >"$tmp"
  mv "$tmp" "$CONFIG"
  echo "✓ Claude Desktop config updated → $new_cmd"
  echo "⚠️  Fully quit (⌘Q) and relaunch Claude Desktop for the change to take effect."
}

cmd_local() {
  [ -f "$LOCAL_PYTHON" ] || { echo "❌ .venv not found — run: python3.12 -m venv .venv && source .venv/bin/activate && pip install 'mcp[cli]' httpx python-dotenv" >&2; exit 1; }
  echo "✓ Using local source: $LOCAL_SERVER"
  set_command "$LOCAL_PYTHON" "[\"$LOCAL_SERVER\"]"
}

cmd_release() {
  require gh
  local arch
  arch=$([ "$(uname -m)" = "arm64" ] && echo "arm64" || echo "amd64")

  mkdir -p "$(dirname "$RELEASE_BIN")"
  echo "→ Downloading latest darwin-${arch} release …"
  gh release download \
    --repo mpya-digital/winningtemp-mcp \
    --pattern "winningtemp-mcp-darwin-${arch}" \
    --output "$RELEASE_BIN" \
    --clobber

  chmod +x "$RELEASE_BIN"
  xattr -d com.apple.quarantine "$RELEASE_BIN" 2>/dev/null || true
  codesign --force --sign - "$RELEASE_BIN"

  echo "✓ Installed $("$RELEASE_BIN" --version)"
  set_command "$RELEASE_BIN" "null"
}

cmd_status() {
  require jq
  [ -f "$CONFIG" ] || { echo "❌ Claude Desktop config not found at $CONFIG" >&2; exit 1; }
  local current
  current=$(jq -r --arg name "$SERVER_NAME" '.mcpServers[$name].command // "<not configured>"' "$CONFIG")
  echo "current: $current"
  case "$current" in
    "$LOCAL_PYTHON") echo "mode:    local (running from source)" ;;
    "$RELEASE_BIN")  echo "mode:    release (GitHub binary)" ;;
    *)               echo "mode:    custom / unknown" ;;
  esac
}

case "${1:-}" in
  local)   cmd_local ;;
  release) cmd_release ;;
  status)  cmd_status ;;
  *)
    echo "usage: $0 {local|release|status}" >&2
    exit 2
    ;;
esac
