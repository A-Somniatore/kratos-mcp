# Kratos MCP Server

MCP (Model Context Protocol) server for the Kratos deployment platform.

## Setup

Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "kratos": {
      "command": "python",
      "args": ["-m", "kratos_mcp.server"],
      "cwd": "/path/to/kratos-mcp",
      "env": {
        "KRATOS_API_URL": "https://kratos.somniatore.com"
      }
    }
  }
}
```

Or install and run directly:

```bash
pip install -e .
kratos-mcp
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KRATOS_API_URL` | `https://kratos.somniatore.com` | Kratos API base URL |
| `KRATOS_API_TOKEN` | *(none)* | Optional bearer token for auth |

## Architecture

- `client.py` - Async HTTP client (httpx) for all Kratos API endpoints
- `server.py` - FastMCP server exposing 77 tools and 7 resources

All tools include error handling that returns user-friendly messages instead of raw stack traces.

## Resources (7)

| URI | Description |
|-----|-------------|
| `kratos://assets` | List of all managed assets |
| `kratos://assets/{asset_id}` | Individual asset details |
| `kratos://health` | Platform health status |
| `kratos://deployments` | Recent deployments |
| `kratos://previews` | Active preview environments |
| `kratos://settings` | Platform settings |
| `kratos://version` | API version and metadata |

## Tools (77)

### Health & System (7)
- `check_health` - Basic health check
- `check_health_detailed` - Full dependency check
- `check_services_health` - All services health
- `get_system_version` - API version info
- `get_api_metadata` - API metadata (version, uptime, environment)
- `get_analytics_dashboard` - Deployment analytics
- `get_deployment_trends` - Deployment frequency trends

### Assets (7)
- `list_assets` - List all assets
- `get_asset` - Get asset details
- `create_asset` - Create new asset
- `update_asset` - Update asset configuration
- `delete_asset` - Delete asset
- `sync_asset` - Sync from GitHub
- `get_asset_suggestions` - Get setup suggestions

### Deployments (5)
- `deploy_asset` - Deploy to environment(s)
- `rollback_asset` - Rollback to previous commit
- `list_deployments` - List recent deployments
- `get_deployment_status` - Check deployment status
- `cancel_deployment` - Cancel running deployment

### Logs (4)
- `get_deployment_logs` - Build + deploy logs
- `get_asset_deployment_logs` - Recent logs for asset
- `get_build_status` - Build job status
- `get_build_logs` - Kaniko build logs

### Environment Config (4)
- `get_env_config` - Get env vars for asset
- `set_env_variable` - Set env var
- `sync_env_config` - Sync env config from GitHub
- `validate_env_vars` - Validate env variables

### Health & Metrics (3)
- `get_asset_health` - Asset health status
- `get_asset_metrics` - CPU/memory metrics
- `get_asset_readiness` - Deployment readiness

### Kubernetes (4)
- `get_k8s_status` - K8s deployment status
- `get_pod_logs` - Runtime pod logs
- `get_k8s_events` - K8s events
- `scale_deployment` - Scale replicas

### Diff & Impact (2)
- `get_env_diff` - Env var diff across environments
- `get_deployment_impact` - Impact assessment

### Preview Environments (5)
- `list_previews` - List active previews
- `create_preview` - Create preview (auto-expires 1h)
- `get_preview` - Get preview status
- `get_preview_logs` - Preview logs
- `delete_preview` - Delete preview

### Package Publishing (4)
- `get_package_workspace` - Workspace info
- `publish_package` - Publish to npm/PyPI/Crates/Conan
- `get_publish_status` - Publish status
- `get_publish_history` - Publish history

### Schedules (4)
- `list_schedule_presets` - Available cron presets
- `preview_schedule` - Preview next N cron runs
- `get_asset_schedule` - Get asset schedule
- `update_asset_schedule` - Update asset schedule

### Dockerfile (4)
- `get_dockerfile` - Get current Dockerfile
- `generate_dockerfile` - Generate Dockerfile
- `push_dockerfile` - Push Dockerfile to repo
- `get_dockerfile_history` - Push history

### Nginx (3)
- `list_nginx_templates` - Available nginx templates
- `generate_nginx_config` - Generate nginx config
- `validate_nginx_config` - Validate nginx config

### Hermes CMS (3)
- `check_hermes_status` - Hermes connection status
- `list_hermes_assets` - List Hermes assets
- `get_hermes_asset` - Get Hermes asset

### Deployment Runs (3)
- `create_deployment_plan` - Create deployment plan (dry-run)
- `list_runs` - List execution history
- `get_run` - Get run details

### GitHub (5)
- `check_github_status` - GitHub API status
- `list_github_repos` - List repos
- `refresh_github_repos` - Refresh repo cache
- `get_github_branches` - List branches
- `get_github_commits` - List commits

### Harbor (3)
- `list_container_images` - Harbor repos
- `list_container_artifacts` - Image artifacts/tags
- `cleanup_harbor` - Clean up old images

### Infrastructure (5)
- `list_machine_pools` - Machine pools
- `get_machine_pool` - Pool details
- `create_machine_pool` - Create pool
- `delete_machine_pool` - Delete pool
- `list_cluster_nodes` - K8s nodes

### Settings (2)
- `get_settings` - Get platform settings
- `update_settings` - Update settings

## Documentation

- All features must have their own markdown file in the `docs/` folder
- Keep docs up to date when modifying features
- Use `docs/README.md` as the main overview/index
