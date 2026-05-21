# Installing the Winningtemp MCP server

End-user install guide for macOS. Binaries are built automatically from this repo's `main` branch — every merge produces a fresh release.

## Prerequisites

- macOS, either Apple Silicon (M-series) or Intel
- [GitHub CLI](https://cli.github.com/) — `brew install gh`
- [Claude Code](https://claude.ai/code) installed
- Winningtemp ClientId + ClientSecret (ask your Winningtemp admin, or generate in **Settings → Apps / Developer API**)

## One-time GitHub authentication

The repo is private, so you need to be logged into the GitHub CLI as a user with read access. If you haven't already:

```bash
gh auth login
```

Pick **GitHub.com** → **HTTPS** → **Login with a web browser**. Follow the prompts.

Verify with:

```bash
gh auth status
```

## Install (or update) the binary

### Which binary do I need?

| Your Mac | Chip | Binary |
|---|---|---|
| Most Macs sold from late 2020 onwards | Apple Silicon (M1, M2, M3, M4…) | `winningtemp-mcp-darwin-arm64` |
| Older Macs (pre-late-2020) | Intel | `winningtemp-mcp-darwin-amd64` |

**Not sure which you have?** Run `uname -m` — `arm64` is Apple Silicon, `x86_64` is Intel.

### Run the install command

```bash
# Auto-detect arch
ARCH=$([ "$(uname -m)" = "arm64" ] && echo "arm64" || echo "amd64")

# Make sure the install dir exists
mkdir -p ~/.local/bin

# Download the latest binary
gh release download \
  --repo mpya-digital/winningtemp-mcp \
  --pattern "winningtemp-mcp-darwin-${ARCH}" \
  --output ~/.local/bin/winningtemp-mcp \
  --clobber

# Make it executable and remove the macOS quarantine flag
chmod +x ~/.local/bin/winningtemp-mcp
xattr -d com.apple.quarantine ~/.local/bin/winningtemp-mcp 2>/dev/null || true

# Re-sign ad-hoc to clear com.apple.provenance (added by recent macOS to
# downloaded binaries — without this Gatekeeper silently kills the process)
codesign --force --sign - ~/.local/bin/winningtemp-mcp

# Confirm it works
~/.local/bin/winningtemp-mcp --version
```

You should see something like `winningtemp-mcp v0.0.5 (commit a1b2c3d)`.

> **Why `xattr` and `codesign`?** macOS marks downloaded binaries with a quarantine attribute. On recent versions it also adds a `com.apple.provenance` attribute that `xattr` can't remove — Gatekeeper silently kills the binary on launch (exit 137). Re-signing ad-hoc clears that state. Proper code-signing requires an Apple Developer ID (~€90/yr); this is the standard workaround for internal tools.

> **`~/.local/bin` not on your PATH?** Add this to `~/.zshrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Then reload: `source ~/.zshrc`

## Connect to Claude Code

Run this once to register the server (replace the credential values with your own):

```bash
claude mcp add --transport stdio winningtemp \
  --env WT_CLIENT_ID=your-client-id \
  --env WT_CLIENT_SECRET=your-client-secret \
  -- ~/.local/bin/winningtemp-mcp
```

> **Don't share your credentials.** Use your own ClientId and ClientSecret. Never commit them to a repo.

## Verify the connection

In Claude Code, run:

```
/mcp
```

You should see `winningtemp` listed as a connected server with 15 tools available.

## Test it

Try asking Claude:

- *"List all teams from Winningtemp"*
- *"Get the temperature index for the last 30 days"*
- *"What's our current eNPS score?"*

## Updating to a newer version

Re-run the install command above — it overwrites the binary in place. Restart Claude Code to pick up the new version.

See all releases at: https://github.com/mpya-digital/winningtemp-mcp/releases

Check your current version:

```bash
~/.local/bin/winningtemp-mcp --version
```

## Troubleshooting

**`gh: command not found`** — install with `brew install gh`.

**`gh: failed to download asset: 404`** — your GitHub user might not have access to the repo. Ask the team lead to add you to `mpya-digital`.

**`zsh: bad CPU type in executable`** — wrong arch downloaded. Re-run the install command — the auto-detect line handles this.

**Claude Code says "Could not connect to MCP server"** — check the path is correct and the binary has execute permissions:
```bash
ls -l ~/.local/bin/winningtemp-mcp
~/.local/bin/winningtemp-mcp --version
```

**"Apple cannot verify the developer..."** — re-run the `xattr` and `codesign` steps.

**Binary exits immediately with code 137** — Gatekeeper killed it due to `com.apple.provenance`. Re-sign:
```bash
codesign --force --sign - ~/.local/bin/winningtemp-mcp
```

**Authentication errors from Winningtemp** — double-check your `WT_CLIENT_ID` and `WT_CLIENT_SECRET`. If you lost the secret, generate a new pair in Winningtemp **Settings → Apps / Developer API**.

## Uninstall

```bash
rm ~/.local/bin/winningtemp-mcp
claude mcp remove winningtemp
```
