# Kratos MCP Server

MCP (Model Context Protocol) server for the Kratos deployment platform. Exposes 77 tools and 7 resources for managing Kubernetes deployments, preview environments, package publishing, and infrastructure operations via AI assistants.

## What It Does

The Kratos MCP server enables AI tools like Claude to interact with the Kratos platform through the Model Context Protocol. It provides:

- **Asset management** — list, create, update, and delete deployment assets
- **Deployments** — deploy, rollback, and monitor deployments across environments
- **Preview environments** — create and manage ephemeral preview deployments
- **Package publishing** — publish to npm, PyPI, Crates, and Conan registries
- **Kubernetes operations** — view pod logs, K8s events, scale deployments
- **Health and metrics** — monitor service health, CPU/memory usage, and readiness
- **GitHub integration** — list repos, branches, commits, and refresh caches
- **Infrastructure** — manage machine pools, cluster nodes, and Harbor registry

## Architecture

- `client.py` — async HTTP client (httpx) for all Kratos API endpoints
- `server.py` — FastMCP server exposing tools and resources
