# 🔌 10 Plugins Every AI Developer Needs — Complete Setup Guide
### **By @baqar.dev | Sayed Baqar Abbas | AI & Dev**

> [!NOTE]
> This guide covers how to install & connect all 10 essential MCP (Model Context Protocol) plugins across **three AI agents**: Claude Code, OpenAI Codex CLI, and Google Antigravity. Follow step-by-step — no step skipped.

---

## 📋 Table of Contents

1. [Prerequisites (Install These First)](#-prerequisites)
2. [Understanding Config Files (Where Each Agent Stores Settings)](#-where-each-agent-stores-its-config)
3. [Plugin 1 — Serena](#1-serena)
4. [Plugin 2 — Context7](#2-context7)
5. [Plugin 3 — Playwright MCP](#3-playwright-mcp)
6. [Plugin 4 — GitHub MCP](#4-github-mcp)
7. [Plugin 5 — Filesystem MCP](#5-filesystem-mcp)
8. [Plugin 6 — PostgreSQL MCP](#6-postgresql-mcp)
9. [Plugin 7 — Sequential Thinking](#7-sequential-thinking)
10. [Plugin 8 — Memory Bank](#8-memory-bank)
11. [Plugin 9 — Puppeteer MCP](#9-puppeteer-mcp)
12. [Plugin 10 — Docker MCP](#10-docker-mcp)
13. [Master Config Reference (Copy-Paste Ready)](#-master-config-reference)
14. [Recommended Starter Packs](#-recommended-starter-packs)
15. [Troubleshooting](#-troubleshooting)

---

## 🛠 Prerequisites

Install these **before** setting up any plugin:

| Tool | Why You Need It | Install Command |
|:---|:---|:---|
| **Node.js v18+** | Runs all `npx`-based MCP servers | [Download from nodejs.org](https://nodejs.org) |
| **Python 3.10+** | Required for Serena | [Download from python.org](https://python.org) |
| **uv** (Python package runner) | Runs Serena MCP | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Git** | Required for GitHub MCP + Serena | [Download from git-scm.com](https://git-scm.com) |
| **Docker Desktop** | Required for Docker MCP | [Download from docker.com](https://docker.com) |

### Install the Three Agents

| Agent | Install |
|:---|:---|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` then run `claude` in terminal |
| **OpenAI Codex CLI** | `npm install -g @openai/codex` then run `codex` in terminal |
| **Google Antigravity** | Download from [antigravity.google](https://antigravity.google) or install the VS Code/IDE extension |

---

## 📁 Where Each Agent Stores Its Config

> [!IMPORTANT]
> Each agent reads MCP server configs from a **different file** and in a **different format**. This is the #1 thing people get wrong.

### Claude Code (JSON format)
- **Config file:** `~/.claude.json` (global) or use CLI commands
- **Add via CLI (easiest):**
  ```bash
  claude mcp add <server-name> -- <command> [args...]
  ```
- **List servers:** `claude mcp list`
- **Remove:** `claude mcp remove <server-name>`

### OpenAI Codex CLI (TOML format — NOT JSON!)
- **Config file:** `~/.codex/config.toml` (global) or `.codex/config.toml` (per project)
- **Add via CLI (easiest):**
  ```bash
  codex mcp add <server-name> -- <command> [args...]
  ```
- **List servers:** `codex mcp list`

> [!WARNING]
> Codex uses **TOML**, not JSON. Files named `mcp.json` will be **ignored** by Codex CLI.

### Google Antigravity (JSON format)
- **Option 1 — UI:** Settings → Customizations → Installed MCP Servers → Add MCP
- **Option 2 — Config file:** Edit `~/.gemini/config/mcp.json` (global) or `.agents/mcp.json` (per project)
- **Format:** Same JSON structure as Claude Desktop

---

## 1. Serena

> **What it does:** Gives AI deep understanding of your codebase — files, dependencies, symbols, project structure. Semantic code navigation instead of raw file reading.

### 🔧 Prerequisites
- Python 3.10+
- `uv` package manager installed (see prerequisites above)
- Git

---

### Setup for Claude Code
```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context ide-assistant
```
**With project path (recommended):**
```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context ide-assistant --project /path/to/your/project
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context ide-assistant
```
Or manually edit `~/.codex/config.toml`:
```toml
[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--context", "ide-assistant"]
enabled = true
```

### Setup for Google Antigravity
Settings → Customizations → Add MCP → Add manually, or edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--context", "ide-assistant"
      ]
    }
  }
}
```

> [!TIP]
> Add `--project /path/to/your/code` in the args to point Serena at your active workspace for best results.

---

## 2. Context7

> **What it does:** Provides AI with the latest, version-specific framework and library documentation in real-time. Stops AI from hallucinating outdated API methods.

### 🔧 Prerequisites
- Node.js 18+
- (Optional) Free API key from [context7.com/dashboard](https://context7.com/dashboard) for higher rate limits

---

### Setup for Claude Code
**Quickest method (auto-setup):**
```bash
npx ctx7 setup --claude
```
**Or manual CLI:**
```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp@latest
```
Or manually edit `~/.codex/config.toml`:
```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]
enabled = true
```
*With API key:*
```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]
enabled = true

[mcp_servers.context7.env]
CONTEXT7_API_KEY = "your_api_key_here"
```

### Setup for Google Antigravity
Settings → Add MCP, or edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {
        "CONTEXT7_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> [!TIP]
> Once connected, just add `use context7` in your prompts and the AI will automatically pull current docs instead of relying on training data.

---

## 3. Playwright MCP

> **What it does:** Lets AI interact with real websites — click buttons, fill forms, take screenshots, and automate browser testing.

### 🔧 Prerequisites
- Node.js 18+
- Run `npx playwright install` once to download browser binaries

---

### Setup for Claude Code
```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add playwright -- npx -y @playwright/mcp@latest
```
Or manually in `~/.codex/config.toml`:
```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

> [!TIP]
> **First-time only:** Run `npx playwright install` in your terminal before using. This downloads the Chromium, Firefox, and WebKit browsers that Playwright needs.

---

## 4. GitHub MCP

> **What it does:** Allows AI to read repositories, issues, pull requests, and code directly from GitHub. Create PRs, manage issues, search code — all through your AI agent.

### 🔧 Prerequisites
- Node.js 18+
- **GitHub Personal Access Token (PAT):**
  1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
  2. Click **"Generate new token (classic)"**
  3. Select scopes: `repo`, `read:org`, `gist`
  4. Copy the token (starts with `ghp_`)

---

### Setup for Claude Code
```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_YOUR_TOKEN_HERE -- npx -y @modelcontextprotocol/server-github
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN=ghp_YOUR_TOKEN_HERE -- npx -y @modelcontextprotocol/server-github
```
Or manually in `~/.codex/config.toml`:
```toml
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
enabled = true

[mcp_servers.github.env]
GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_YOUR_TOKEN_HERE"
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

> [!CAUTION]
> **Never share your GitHub token publicly.** Don't commit config files with tokens to Git. Use environment variables or `.env` files instead.

---

## 5. Filesystem MCP

> **What it does:** Gives AI controlled access to read, write, search, and manage your local project files and folders. Sandboxed to directories you specify.

### 🔧 Prerequisites
- Node.js 18+

---

### Setup for Claude Code
```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /absolute/path/to/your/project
```
**Multiple folders:**
```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project1 /path/to/project2
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /absolute/path/to/your/project
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/your/project"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/absolute/path/to/your/project"
      ]
    }
  }
}
```

> [!WARNING]
> The AI can **only** access folders you list in the `args`. This is a security sandbox — don't give it access to your entire home directory.

---

## 6. PostgreSQL MCP

> **What it does:** Allows AI to inspect database schemas, write SQL queries, and analyze your PostgreSQL databases using natural language.

### 🔧 Prerequisites
- Node.js 18+
- A running PostgreSQL database
- Your database connection string: `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`

---

### Setup for Claude Code
```bash
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://myuser:mypass@localhost:5432/mydb"
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://myuser:mypass@localhost:5432/mydb"
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.postgres]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres", "postgresql://myuser:mypass@localhost:5432/mydb"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://myuser:mypass@localhost:5432/mydb"
      ]
    }
  }
}
```

> [!CAUTION]
> **Security first:** The default server runs in **read-only mode**. Never expose production database credentials in shared config files. Use environment variables for passwords.

---

## 7. Sequential Thinking

> **What it does:** Helps AI break complex problems into structured, step-by-step reasoning chains. Great for debugging, architecture decisions, and multi-step planning.

### 🔧 Prerequisites
- Node.js 18+

---

### Setup for Claude Code
```bash
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.sequential-thinking]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-sequential-thinking"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

> [!TIP]
> Use it by telling your AI: *"Use sequential thinking to analyze this problem step by step."* The AI will automatically break down complex reasoning into traceable steps.

---

## 8. Memory Bank

> **What it does:** Stores project-specific context (architecture decisions, coding patterns, conventions) so your AI remembers everything across sessions. No more re-explaining your project.

### 🔧 Prerequisites
- Node.js 18+
- Create a folder for memory storage: `mkdir ~/memory-bank` (or any path you want)

---

### Setup for Claude Code
```bash
claude mcp add memory-bank -e MEMORY_BANK_ROOT=$HOME/memory-bank -- npx -y @alioshr/memory-bank-mcp
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add memory-bank --env MEMORY_BANK_ROOT=$HOME/memory-bank -- npx -y @alioshr/memory-bank-mcp
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.memory-bank]
command = "npx"
args = ["-y", "@alioshr/memory-bank-mcp"]
enabled = true

[mcp_servers.memory-bank.env]
MEMORY_BANK_ROOT = "/Users/yourname/memory-bank"
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "npx",
      "args": ["-y", "@alioshr/memory-bank-mcp"],
      "env": {
        "MEMORY_BANK_ROOT": "/Users/yourname/memory-bank"
      }
    }
  }
}
```

> [!TIP]
> **For per-project memory:** Use a project-level path like `./memory-bank` in your repo instead of a global path. This way each project gets its own memory context.

---

## 9. Puppeteer MCP

> **What it does:** Enables browser automation, web scraping, screenshots, form filling, and UI testing — all controlled by your AI agent through a real Chrome browser.

### 🔧 Prerequisites
- Node.js 18+
- Chrome/Chromium browser installed

---

### Setup for Claude Code
```bash
claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.puppeteer]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-puppeteer"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

> [!NOTE]
> **Puppeteer vs Playwright:** Both do browser automation. Puppeteer = Chrome only, simpler API. Playwright = Chrome + Firefox + Safari, more features. Pick one based on your needs — you don't need both.

---

## 10. Docker MCP

> **What it does:** Allows AI to inspect containers, read logs, manage services, and control your Docker development environments — all through natural language.

### 🔧 Prerequisites
- Docker Desktop installed and running
- Node.js 18+

---

### Setup for Claude Code

**Option A — Docker MCP Toolkit (Recommended):**
1. Open Docker Desktop → Settings → Beta Features
2. Enable **"Docker MCP Toolkit"** → Click Apply
3. Go to MCP Toolkit tab → Connect to Claude

**Option B — Manual CLI:**
```bash
claude mcp add docker -- docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock mcp/docker
```

### Setup for OpenAI Codex CLI
```bash
codex mcp add docker -- docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock mcp/docker
```
Or in `~/.codex/config.toml`:
```toml
[mcp_servers.docker]
command = "docker"
args = ["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/docker"]
enabled = true
```

### Setup for Google Antigravity
Edit `~/.gemini/config/mcp.json`:
```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "mcp/docker"
      ]
    }
  }
}
```

> [!WARNING]
> Mounting `/var/run/docker.sock` gives the MCP server full access to your Docker engine. Only use this in development, never in production.

---

## 📋 Master Config Reference

Here's the complete config for all 10 plugins, ready to copy-paste:

### For Claude Code (run each command in terminal)
```bash
# 1. Serena
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context ide-assistant

# 2. Context7
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest

# 3. Playwright
claude mcp add playwright -- npx -y @playwright/mcp@latest

# 4. GitHub
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_YOUR_TOKEN -- npx -y @modelcontextprotocol/server-github

# 5. Filesystem
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project

# 6. PostgreSQL
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://user:pass@localhost:5432/dbname"

# 7. Sequential Thinking
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# 8. Memory Bank
claude mcp add memory-bank -e MEMORY_BANK_ROOT=$HOME/memory-bank -- npx -y @alioshr/memory-bank-mcp

# 9. Puppeteer
claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer

# 10. Docker
claude mcp add docker -- docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock mcp/docker

# ✅ Verify all servers
claude mcp list
```

---

### For OpenAI Codex CLI (run each command in terminal)
```bash
# 1. Serena
codex mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context ide-assistant

# 2. Context7
codex mcp add context7 -- npx -y @upstash/context7-mcp@latest

# 3. Playwright
codex mcp add playwright -- npx -y @playwright/mcp@latest

# 4. GitHub
codex mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN=ghp_YOUR_TOKEN -- npx -y @modelcontextprotocol/server-github

# 5. Filesystem
codex mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project

# 6. PostgreSQL
codex mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://user:pass@localhost:5432/dbname"

# 7. Sequential Thinking
codex mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# 8. Memory Bank
codex mcp add memory-bank --env MEMORY_BANK_ROOT=$HOME/memory-bank -- npx -y @alioshr/memory-bank-mcp

# 9. Puppeteer
codex mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer

# 10. Docker
codex mcp add docker -- docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock mcp/docker

# ✅ Verify all servers
codex mcp list
```

---

### For Google Antigravity (single JSON config file)

Edit `~/.gemini/config/mcp.json` and paste this complete config:

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--context", "ide-assistant"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {
        "CONTEXT7_API_KEY": "YOUR_API_KEY"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/your/project"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/dbname"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory-bank": {
      "command": "npx",
      "args": ["-y", "@alioshr/memory-bank-mcp"],
      "env": {
        "MEMORY_BANK_ROOT": "/Users/yourname/memory-bank"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "docker": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/docker"]
    }
  }
}
```

---

## 🎯 Recommended Starter Packs

Don't install all 10 at once — pick a pack based on your workflow:

### 🟢 Beginner Pack (Start Here)
| # | Plugin | Why |
|:---:|:---|:---|
| 1 | Filesystem MCP | Let AI access your files |
| 2 | Context7 | Stop AI hallucinations |
| 3 | Sequential Thinking | Better AI reasoning |

### 🔵 Web Developer Pack
| # | Plugin | Why |
|:---:|:---|:---|
| 1 | Filesystem MCP | File access |
| 2 | Context7 | Framework docs |
| 3 | Playwright MCP | Browser testing |
| 4 | GitHub MCP | PR/issue management |
| 5 | PostgreSQL MCP | Database queries |

### 🟣 Full Stack Power User
| # | Plugin | Why |
|:---:|:---|:---|
| 1-10 | All 10 plugins | Maximum AI capability |

> [!TIP]
> **Don't overload.** Adding too many MCP servers at once can slow down your AI agent because each server adds to the context window. Start with 3-4, then add more as needed.

---

## 🔧 Troubleshooting

### Common Issues & Fixes

| Problem | Fix |
|:---|:---|
| **"npx: command not found"** | Install Node.js 18+ from [nodejs.org](https://nodejs.org) |
| **"uvx: command not found"** | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Server shows "disconnected"** | Restart your agent (close & reopen terminal / restart app) |
| **Claude Code doesn't see the server** | Run `claude mcp list` to verify. Try removing and re-adding the server |
| **Codex ignores my config** | Make sure you're editing `config.toml`, not `mcp.json` — Codex only reads TOML |
| **GitHub MCP authentication error** | Regenerate your PAT token and make sure `repo` scope is enabled |
| **Playwright fails to launch browser** | Run `npx playwright install` first to download browser binaries |
| **Docker MCP can't connect** | Make sure Docker Desktop is running. Check if `/var/run/docker.sock` exists |
| **PostgreSQL connection refused** | Verify your database is running and the connection string is correct |
| **"Permission denied" errors on Windows** | Use full path to `npx.cmd`: `C:\\Program Files\\nodejs\\npx.cmd` instead of `npx` |

### Verify Everything Is Working

**Claude Code:**
```bash
claude mcp list
```

**Codex CLI:**
```bash
codex mcp list
```

**Antigravity:**
Settings → Customizations → Check "Installed MCP Servers" section — each server should show a green status indicator.

---

### 💡 Pro Tips

1. **Use project-level configs** for team projects — put `.claude/settings.json` or `.codex/config.toml` in your repo root
2. **Keep tokens in environment variables** — never hardcode them in config files that get committed to Git
3. **Restart your agent after adding servers** — changes don't apply until you restart
4. **Check for updates** — `npx -y` always pulls the latest version automatically
5. **Monitor context window** — if your AI seems slow or confused, try disabling MCP servers you're not actively using

---

> **Made with ❤️ by @baqar.dev**
> Save this guide. Share it with your dev friends.
> Follow for more AI + dev content daily.
