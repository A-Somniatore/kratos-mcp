# Kratos MCP Server

[MCP](https://modelcontextprotocol.io) server for the [Kratos](https://github.com/A-Somniatore/kratos-api) deployment platform. Exposes 77 tools and 7 resources for managing Kubernetes deployments, preview environments, package publishing, and more.

## Quick Start

### Install

```bash
pip install -e .
```

### Configure

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "kratos": {
      "command": "kratos-mcp",
      "env": {
        "KRATOS_API_URL": "https://kratos.somniatore.com"
      }
    }
  }
}
```

Or run with Python directly:

```json
{
  "mcpServers": {
    "kratos": {
      "command": "python",
      "args": ["-m", "kratos_mcp.server"],
      "env": {
        "KRATOS_API_URL": "https://kratos.somniatore.com"
      }
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KRATOS_API_URL` | `https://kratos.somniatore.com` | Kratos API base URL |
| `KRATOS_API_TOKEN` | — | Optional bearer token |

## What Can It Do?

- **Assets** — Create, deploy, rollback, and manage applications
- **Deployments** — Trigger builds, monitor status, view logs
- **Preview Environments** — Spin up ephemeral branch deployments
- **Environment Variables** — Manage config across environments
- **Package Publishing** — Publish to npm, PyPI, Crates.io, Conan
- **Kubernetes** — Scale deployments, view pod logs, check events
- **GitHub** — Browse repos, branches, commits
- **Harbor** — Manage container images
- **Schedules** — Configure CronJob schedules
- **Dockerfile** — Generate and push Dockerfiles
- **Machine Pools** — Target deployments to specific nodes

See [CLAUDE.md](./CLAUDE.md) for the full list of 77 tools and 7 resources.

## Development

```bash
# Install in dev mode
pip install -e .

# Run the server
kratos-mcp

# Or with Python
python -m kratos_mcp.server
```

## License

MIT
