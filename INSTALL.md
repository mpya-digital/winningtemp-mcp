# Installing the Winningtemp MCP connector

This guide gets you the Winningtemp connector in your **Claude desktop app** so you can ask Claude live questions about your company's engagement data.

## Prerequisites

- macOS
- [GitHub CLI](https://cli.github.com/) — install with `brew install gh`
- The Claude desktop app installed
- Winningtemp ClientId + ClientSecret — get these from **Winningtemp → Settings → Apps / Developer API → Generate**. Copy the secret immediately, it won't be shown again.

---

## Step 1 — One-time GitHub authentication

The repo is private, so you need to be logged into the GitHub CLI. If you haven't already:

```bash
gh auth login
```

Pick **GitHub.com** → **HTTPS** → **Login with a web browser** and follow the prompts.

---

## Step 2 — Download the binary

Open Terminal and run:

```bash
# Auto-detect your Mac architecture
ARCH=$([ "$(uname -m)" = "arm64" ] && echo "arm64" || echo "amd64")

# Create the install directory
mkdir -p ~/.local/bin

# Download the latest release
gh release download \
  --repo mpya-digital/winningtemp-mcp \
  --pattern "winningtemp-mcp-darwin-${ARCH}" \
  --output ~/.local/bin/winningtemp-mcp \
  --clobber

# Make it executable and clear macOS quarantine
chmod +x ~/.local/bin/winningtemp-mcp
xattr -d com.apple.quarantine ~/.local/bin/winningtemp-mcp 2>/dev/null || true
codesign --force --sign - ~/.local/bin/winningtemp-mcp

# Verify it works
~/.local/bin/winningtemp-mcp --version
```

You should see something like `winningtemp-mcp v0.0.5 (commit a1b2c3d)`.

---

## Step 3 — Add it to the Claude desktop config

Open this file in any text editor:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

> **Tip:** You can open it directly from Terminal:
> ```bash
> open ~/Library/Application\ Support/Claude/claude_desktop_config.json
> ```

Add the `winningtemp` block inside `"mcpServers"`. If the file already has other servers, add it alongside them:

```json
{
  "mcpServers": {
    "winningtemp": {
      "command": "/Users/YOUR_USERNAME/.local/bin/winningtemp-mcp",
      "env": {
        "WT_CLIENT_ID": "your-client-id",
        "WT_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

Replace:
- `YOUR_USERNAME` with your macOS username (run `whoami` in Terminal if unsure)
- `your-client-id` and `your-client-secret` with your Winningtemp credentials

> **Never share your credentials or commit this file to a repo.**

---

## Step 4 — Restart Claude

Fully quit the Claude desktop app (**⌘Q**) and relaunch it.

You should now see **winningtemp** listed under **Desktop** in the Connectors panel.

---

## Step 5 — Test it

Start a new chat and ask:

- *"List all our active teams from Winningtemp"*
- *"What's our temperature index for the last 30 days?"*
- *"What's our current eNPS score?"*

---

## Updating to a newer version

Re-run the download command from Step 2 — it overwrites the binary in place. Restart Claude to pick up the new version.

See all releases: https://github.com/mpya-digital/winningtemp-mcp/releases

Check your current version:
```bash
~/.local/bin/winningtemp-mcp --version
```

---

## Troubleshooting

**`gh: command not found`**
Install with `brew install gh`.

**`gh: failed to download asset: 404`**
Your GitHub account doesn't have access to the repo. Ask the team lead to add you to `mpya-digital`.

**Winningtemp doesn't appear in the Connectors panel**
- Check the path in the config is correct — replace `YOUR_USERNAME` with your actual username
- Make sure you fully quit (⌘Q) and relaunched Claude
- Verify the binary works: `~/.local/bin/winningtemp-mcp --version`

**"Apple cannot verify the developer…"**
Re-run the `xattr` and `codesign` lines from Step 2.

**Binary exits with code 137**
Gatekeeper killed it. Re-sign:
```bash
codesign --force --sign - ~/.local/bin/winningtemp-mcp
```

**Authentication errors from Winningtemp**
Double-check `WT_CLIENT_ID` and `WT_CLIENT_SECRET` in your config. If you lost the secret, generate a new pair in Winningtemp **Settings → Apps / Developer API**.

---

## Uninstall

```bash
rm ~/.local/bin/winningtemp-mcp
```

Then remove the `winningtemp` block from `claude_desktop_config.json` and restart Claude.
