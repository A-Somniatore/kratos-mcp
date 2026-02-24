"""Kratos MCP Server - expose Kratos deployment platform tools via MCP."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from .client import KratosClient

# Initialize MCP server
mcp = FastMCP(
    "kratos",
    instructions=(
        "This server provides access to the Kratos deployment platform. "
        "You can manage assets (deployable applications), trigger deployments, "
        "view logs, check health, manage environment variables, preview environments, "
        "publish packages, manage schedules, and more. "
        "All assets are linked to GitHub repositories and deployed to Kubernetes via GitOps."
    ),
)

# Global client instance
_client: KratosClient | None = None


def _get_client() -> KratosClient:
    global _client
    if _client is None:
        base_url = os.environ.get("KRATOS_API_URL", "https://kratos.somniatore.com")
        token = os.environ.get("KRATOS_API_TOKEN")
        _client = KratosClient(base_url=base_url, token=token)
    return _client


def _fmt(data: Any) -> str:
    """Format API response as readable JSON."""
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2, default=str)


def _err(e: Exception) -> str:
    """Format an error into a user-friendly message."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            detail = e.response.json().get("detail", e.response.text)
        except Exception:
            detail = e.response.text
        return f"API error ({status}): {detail}"
    if isinstance(e, httpx.ConnectError):
        return f"Connection failed: Could not reach Kratos API. Is it running? ({e})"
    if isinstance(e, httpx.TimeoutException):
        return f"Request timed out: The operation took too long. ({e})"
    return f"Error: {e}"


# ── MCP Resources ────────────────────────────────────────────────────────────


@mcp.resource("kratos://assets")
async def resource_assets() -> str:
    """List of all assets managed by Kratos."""
    try:
        client = _get_client()
        result = await client.list_assets(limit=100)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://assets/{asset_id}")
async def resource_asset(asset_id: str) -> str:
    """Detailed information about a specific asset."""
    try:
        client = _get_client()
        result = await client.get_asset(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://health")
async def resource_health() -> str:
    """Current health status of the Kratos platform."""
    try:
        client = _get_client()
        result = await client.health_detailed()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://deployments")
async def resource_deployments() -> str:
    """Recent deployments across all assets."""
    try:
        client = _get_client()
        result = await client.list_deployments(limit=20)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://previews")
async def resource_previews() -> str:
    """Active preview environments."""
    try:
        client = _get_client()
        result = await client.list_previews()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://settings")
async def resource_settings() -> str:
    """Kratos platform settings."""
    try:
        client = _get_client()
        result = await client.get_settings()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.resource("kratos://version")
async def resource_version() -> str:
    """Kratos API version and metadata."""
    try:
        client = _get_client()
        result = await client.get_api_metadata()
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Health & System Tools ────────────────────────────────────────────────────


@mcp.tool()
async def check_health() -> str:
    """Check Kratos platform health. Returns basic health status."""
    try:
        client = _get_client()
        result = await client.health()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def check_health_detailed() -> str:
    """Get detailed health of all Kratos dependencies (DB, Redis, K8s, Harbor, GitHub)."""
    try:
        client = _get_client()
        result = await client.health_detailed()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def check_services_health() -> str:
    """Check health of all connected services (Kubernetes, Harbor, GitHub, etc)."""
    try:
        client = _get_client()
        result = await client.services_health()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_system_version() -> str:
    """Get Kratos API version and system information."""
    try:
        client = _get_client()
        result = await client.get_system_version()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_api_metadata() -> str:
    """Get API metadata including version, uptime, and environment."""
    try:
        client = _get_client()
        result = await client.get_api_metadata()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_analytics_dashboard() -> str:
    """Get deployment analytics dashboard with stats and trends."""
    try:
        client = _get_client()
        result = await client.get_analytics_dashboard()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_deployment_trends() -> str:
    """Get deployment frequency trends over time."""
    try:
        client = _get_client()
        result = await client.get_deployment_trends()
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Asset Tools ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_assets(limit: int = 50) -> str:
    """List all deployed assets (applications) in Kratos.

    Args:
        limit: Maximum number of assets to return (default 50)
    """
    try:
        client = _get_client()
        result = await client.list_assets(limit=limit)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset(asset_id: str) -> str:
    """Get detailed information about a specific asset.

    Args:
        asset_id: The UUID of the asset
    """
    try:
        client = _get_client()
        result = await client.get_asset(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def create_asset(
    name: str, repo_url: str, branch: str = "main", description: str = ""
) -> str:
    """Create a new asset (deployable application) in Kratos.

    Args:
        name: Name for the asset (e.g., "my-app")
        repo_url: GitHub repository URL
        branch: Default branch (default "main")
        description: Optional description
    """
    try:
        client = _get_client()
        data = {
            "name": name,
            "repoUrl": repo_url,
            "branch": branch,
            "description": description,
        }
        result = await client.create_asset(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def update_asset(asset_id: str, name: str | None = None, description: str | None = None, branch: str | None = None) -> str:
    """Update an existing asset's configuration.

    Args:
        asset_id: The UUID of the asset
        name: New name (optional)
        description: New description (optional)
        branch: New default branch (optional)
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if branch is not None:
            data["branch"] = branch
        result = await client.update_asset(asset_id, data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def delete_asset(asset_id: str) -> str:
    """Delete an asset and all its deployments. This is destructive and cannot be undone.

    Args:
        asset_id: The UUID of the asset to delete
    """
    try:
        client = _get_client()
        result = await client.delete_asset(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def sync_asset(asset_id: str) -> str:
    """Sync an asset's configuration from its GitHub repository (re-reads kratos.json, Dockerfile, etc).

    Args:
        asset_id: The UUID of the asset to sync
    """
    try:
        client = _get_client()
        result = await client.sync_asset(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset_suggestions(asset_id: str) -> str:
    """Get setup suggestions for an asset (missing config, recommended actions).

    Args:
        asset_id: The UUID of the asset
    """
    try:
        client = _get_client()
        result = await client.get_asset_suggestions(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Deployment Tools ─────────────────────────────────────────────────────────


@mcp.tool()
async def deploy_asset(
    asset_id: str,
    environments: list[str] | None = None,
    branch: str | None = None,
    commit_hash: str | None = None,
    version: str | None = None,
    notes: str | None = None,
) -> str:
    """Deploy an asset to one or more environments. Triggers a container build and GitOps deployment.

    Args:
        asset_id: The UUID of the asset to deploy
        environments: Target environments (e.g., ["production"], ["development"])
        branch: Git branch to deploy from (default: asset's default branch)
        commit_hash: Specific commit to deploy (default: latest on branch)
        version: Version label for this deployment
        notes: Deployment notes
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {}
        if environments:
            data["environments"] = environments
        if branch:
            data["branch"] = branch
        if commit_hash:
            data["commitHash"] = commit_hash
        if version:
            data["version"] = version
        if notes:
            data["notes"] = notes
        result = await client.deploy_asset(asset_id, data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def rollback_asset(
    asset_id: str,
    commit_hash: str,
    environments: list[str] | None = None,
    version: str | None = None,
) -> str:
    """Rollback an asset to a previous commit. Triggers a rebuild from that commit.

    Args:
        asset_id: The UUID of the asset to rollback
        commit_hash: The commit hash to rollback to
        environments: Target environments (default: all)
        version: Version label for this rollback
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"commitHash": commit_hash}
        if environments:
            data["environments"] = environments
        if version:
            data["version"] = version
        result = await client.rollback_asset(asset_id, data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_deployments(limit: int = 20) -> str:
    """List recent deployments across all assets.

    Args:
        limit: Maximum number of deployments to return (default 20)
    """
    try:
        client = _get_client()
        result = await client.list_deployments(limit=limit)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_deployment_status(deployment_id: str) -> str:
    """Get the current status of a deployment (building, pushing, deploying, ready, failed).

    Args:
        deployment_id: The deployment UUID
    """
    try:
        client = _get_client()
        result = await client.get_deployment(deployment_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def cancel_deployment(deployment_id: str) -> str:
    """Cancel a running deployment.

    Args:
        deployment_id: The deployment UUID to cancel
    """
    try:
        client = _get_client()
        result = await client.cancel_deployment(deployment_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Logs Tools ───────────────────────────────────────────────────────────────


@mcp.tool()
async def get_deployment_logs(deployment_id: str, tail: int = 100) -> str:
    """Get logs for a specific deployment (build + deploy logs).

    Args:
        deployment_id: The deployment UUID
        tail: Number of log lines to return (default 100)
    """
    try:
        client = _get_client()
        result = await client.get_deployment_logs(deployment_id, tail=tail)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset_deployment_logs(asset_id: str, limit: int = 10) -> str:
    """Get recent deployment logs for a specific asset.

    Args:
        asset_id: The asset UUID
        limit: Number of log entries to return (default 10)
    """
    try:
        client = _get_client()
        result = await client.get_deployment_logs_by_asset(asset_id, limit=limit)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_build_status(job_name: str) -> str:
    """Get the status of a Kaniko build job.

    Args:
        job_name: The Kubernetes job name (e.g., "build-my-app-abc123")
    """
    try:
        client = _get_client()
        result = await client.get_build_status(job_name)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_build_logs(job_name: str) -> str:
    """Get build logs for a Kaniko build job.

    Args:
        job_name: The Kubernetes job name (e.g., "build-my-app-abc123")
    """
    try:
        client = _get_client()
        result = await client.get_build_logs(job_name)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Environment Config Tools ────────────────────────────────────────────────


@mcp.tool()
async def get_env_config(asset_id: str) -> str:
    """Get environment variable configuration for an asset across all environments.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_env_config(asset_id)
        if result is None:
            return "No environment configuration found for this asset."
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def set_env_variable(
    asset_id: str,
    key: str,
    value: str,
    environment: str = "production",
    is_secret: bool = False,
) -> str:
    """Set an environment variable for an asset in a specific environment.

    Args:
        asset_id: The asset UUID
        key: Variable name (e.g., "DATABASE_URL")
        value: Variable value
        environment: Target environment ("production", "development", "staging")
        is_secret: Whether this is a secret value (will be masked in UI)
    """
    try:
        client = _get_client()
        data = {
            "environment": environment,
            "value": value,
            "isSet": True,
            "isSecret": is_secret,
        }
        result = await client.set_env_variable(asset_id, key, data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def sync_env_config(asset_id: str) -> str:
    """Sync environment configuration from GitHub (re-reads .env.example files).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.sync_env_config(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def validate_env_vars(variables: dict[str, str], environment: str = "production") -> str:
    """Validate environment variables against known patterns and requirements.

    Args:
        variables: Dict of variable name -> value to validate
        environment: Target environment for validation context
    """
    try:
        client = _get_client()
        result = await client.validate_env_vars(
            {"variables": variables, "environment": environment}
        )
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Health & Metrics Tools ───────────────────────────────────────────────────


@mcp.tool()
async def get_asset_health(asset_id: str) -> str:
    """Get health status for a specific asset (pod status, readiness, resource usage).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_asset_health(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset_metrics(asset_id: str) -> str:
    """Get CPU and memory metrics for an asset's pods.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_asset_metrics(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset_readiness(asset_id: str) -> str:
    """Check if an asset is ready for deployment (validates Dockerfile, config, health endpoint).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_asset_readiness(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Kubernetes Tools ─────────────────────────────────────────────────────────


@mcp.tool()
async def get_k8s_status(namespace: str, deployment_name: str) -> str:
    """Get Kubernetes deployment status (replicas, conditions, pods).

    Args:
        namespace: Kubernetes namespace (e.g., "app-my-app-prod")
        deployment_name: Deployment name
    """
    try:
        client = _get_client()
        result = await client.get_k8s_status(namespace, deployment_name)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_pod_logs(namespace: str, deployment_name: str, tail: int = 100) -> str:
    """Get runtime logs from pods in a Kubernetes deployment.

    Args:
        namespace: Kubernetes namespace
        deployment_name: Deployment name
        tail: Number of log lines (default 100)
    """
    try:
        client = _get_client()
        result = await client.get_k8s_logs(namespace, deployment_name, tail=tail)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_k8s_events(namespace: str, deployment_name: str) -> str:
    """Get Kubernetes events for a deployment (useful for debugging failures).

    Args:
        namespace: Kubernetes namespace
        deployment_name: Deployment name
    """
    try:
        client = _get_client()
        result = await client.get_k8s_events(namespace, deployment_name)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def scale_deployment(namespace: str, deployment_name: str, replicas: int) -> str:
    """Scale a Kubernetes deployment to a specific number of replicas.

    Args:
        namespace: Kubernetes namespace
        deployment_name: Deployment name
        replicas: Target replica count
    """
    try:
        client = _get_client()
        result = await client.scale_deployment(namespace, deployment_name, replicas)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Diff & Impact Tools ─────────────────────────────────────────────────────


@mcp.tool()
async def get_env_diff(asset_id: str) -> str:
    """Get environment variable differences across environments for an asset.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_diff(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_deployment_impact(asset_id: str) -> str:
    """Assess the impact of deploying changes for an asset (affected resources, risks).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_impact(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Preview Environment Tools ───────────────────────────────────────────────


@mcp.tool()
async def list_previews() -> str:
    """List all active preview environments."""
    try:
        client = _get_client()
        result = await client.list_previews()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def create_preview(
    repo_url: str,
    branch: str,
    subdomain: str,
    port: int = 8080,
    health_path: str = "/health",
    env_vars: dict[str, str] | None = None,
    secret_vars: dict[str, str] | None = None,
) -> str:
    """Create a preview environment for a branch/PR. Auto-expires after 1 hour.

    Preview URL will be: https://<subdomain>.preview.somniatore.com (internal/VPN only)

    Args:
        repo_url: GitHub repository URL
        branch: Branch to deploy
        subdomain: Subdomain for the preview URL
        port: Container port (default 8080)
        health_path: Health check path (default "/health")
        env_vars: Environment variables for the container
        secret_vars: Secret environment variables for the container
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {
            "repoUrl": repo_url,
            "branch": branch,
            "subdomain": subdomain,
            "port": port,
            "healthPath": health_path,
        }
        if env_vars:
            data["envVars"] = env_vars
        if secret_vars:
            data["secretVars"] = secret_vars
        result = await client.create_preview(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_preview(deployment_id: str) -> str:
    """Get the status of a preview environment.

    Args:
        deployment_id: The preview deployment UUID
    """
    try:
        client = _get_client()
        result = await client.get_preview(deployment_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_preview_logs(deployment_id: str) -> str:
    """Get logs from a preview environment.

    Args:
        deployment_id: The preview deployment UUID
    """
    try:
        client = _get_client()
        result = await client.get_preview_logs(deployment_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def delete_preview(deployment_id: str) -> str:
    """Delete a preview environment and clean up all resources.

    Args:
        deployment_id: The preview deployment UUID
    """
    try:
        client = _get_client()
        result = await client.delete_preview(deployment_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Package Publishing Tools ────────────────────────────────────────────────


@mcp.tool()
async def get_package_workspace(asset_id: str) -> str:
    """Get package workspace info for an asset (detected package managers, publishable packages).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_package_workspace(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def publish_package(
    asset_id: str,
    registry: str,
    package_name: str | None = None,
    version: str | None = None,
) -> str:
    """Publish a package to a registry (npm, PyPI, Crates.io, Conan).

    Args:
        asset_id: The asset UUID
        registry: Target registry ("npm", "pypi", "crates", "conan")
        package_name: Package name (optional, auto-detected from project)
        version: Version to publish (optional, auto-detected)
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"assetId": asset_id, "registry": registry}
        if package_name:
            data["packageName"] = package_name
        if version:
            data["version"] = version
        result = await client.publish_package(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_publish_status(publish_id: str) -> str:
    """Get the status of a package publish operation.

    Args:
        publish_id: The publish operation UUID
    """
    try:
        client = _get_client()
        result = await client.get_publish_status(publish_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_publish_history(asset_id: str) -> str:
    """Get package publish history for an asset.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_publish_history(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Schedule Tools ──────────────────────────────────────────────────────────


@mcp.tool()
async def list_schedule_presets() -> str:
    """List available CronJob schedule presets (every_15_minutes, daily_midnight, etc)."""
    try:
        client = _get_client()
        result = await client.list_schedule_presets()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def preview_schedule(cron_expression: str, count: int = 5) -> str:
    """Preview the next N runs of a cron schedule.

    Args:
        cron_expression: Cron expression (e.g., "0 */6 * * *")
        count: Number of upcoming runs to show (default 5)
    """
    try:
        client = _get_client()
        result = await client.preview_schedule(
            {"cronExpression": cron_expression, "count": count}
        )
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_asset_schedule(asset_id: str) -> str:
    """Get the CronJob schedule configured for an asset.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_asset_schedule(asset_id)
        if result is None:
            return "No schedule configured for this asset."
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def update_asset_schedule(
    asset_id: str,
    cron_expression: str | None = None,
    preset_id: str | None = None,
    enabled: bool = True,
) -> str:
    """Update the CronJob schedule for an asset.

    Args:
        asset_id: The asset UUID
        cron_expression: Cron expression (e.g., "0 2 * * *")
        preset_id: Use a preset instead of raw cron (e.g., "daily_2am")
        enabled: Whether the schedule is active (default True)
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"enabled": enabled}
        if cron_expression:
            data["cronExpression"] = cron_expression
        if preset_id:
            data["presetId"] = preset_id
        result = await client.update_asset_schedule(asset_id, data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Dockerfile Tools ────────────────────────────────────────────────────────


@mcp.tool()
async def get_dockerfile(asset_id: str) -> str:
    """Get the current Dockerfile for an asset.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_dockerfile(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def generate_dockerfile(asset_id: str, framework: str | None = None) -> str:
    """Generate a Dockerfile for an asset based on its detected framework.

    Args:
        asset_id: The asset UUID
        framework: Override framework detection (e.g., "nextjs", "fastapi", "rust")
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"assetId": asset_id}
        if framework:
            data["framework"] = framework
        result = await client.generate_dockerfile(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def push_dockerfile(asset_id: str, content: str, message: str | None = None) -> str:
    """Push a Dockerfile to an asset's GitHub repository.

    Args:
        asset_id: The asset UUID
        content: Dockerfile content
        message: Commit message (optional)
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"assetId": asset_id, "content": content}
        if message:
            data["message"] = message
        result = await client.push_dockerfile(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_dockerfile_history(asset_id: str) -> str:
    """Get Dockerfile push history for an asset.

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.get_dockerfile_history(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Nginx Tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def list_nginx_templates() -> str:
    """List available nginx configuration templates for static sites."""
    try:
        client = _get_client()
        result = await client.list_nginx_templates()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def generate_nginx_config(
    framework: str, spa: bool = True, custom_routes: list[str] | None = None
) -> str:
    """Generate an nginx configuration for a static site/SPA.

    Args:
        framework: Frontend framework ("react", "nextjs", "vue", "angular", "static")
        spa: Whether this is a single-page application (default True)
        custom_routes: Optional list of custom route patterns
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {"framework": framework, "spa": spa}
        if custom_routes:
            data["customRoutes"] = custom_routes
        result = await client.generate_nginx_config(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def validate_nginx_config(config: str) -> str:
    """Validate an nginx configuration for syntax errors.

    Args:
        config: Nginx configuration content to validate
    """
    try:
        client = _get_client()
        result = await client.validate_nginx_config({"config": config})
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Hermes CMS Tools ───────────────────────────────────────────────────────


@mcp.tool()
async def check_hermes_status() -> str:
    """Check Hermes CMS connection status."""
    try:
        client = _get_client()
        result = await client.get_hermes_status()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_hermes_assets() -> str:
    """List assets in Hermes CMS."""
    try:
        client = _get_client()
        result = await client.list_hermes_assets()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_hermes_asset(asset_id: str) -> str:
    """Get a Hermes CMS asset by ID.

    Args:
        asset_id: The Hermes asset ID
    """
    try:
        client = _get_client()
        result = await client.get_hermes_asset(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Deployment Runs Tools ───────────────────────────────────────────────────


@mcp.tool()
async def create_deployment_plan(asset_id: str) -> str:
    """Create a deployment plan for an asset (dry-run that shows what would change).

    Args:
        asset_id: The asset UUID
    """
    try:
        client = _get_client()
        result = await client.create_deployment_plan(asset_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_runs(limit: int = 20) -> str:
    """List deployment plan execution history.

    Args:
        limit: Maximum number of runs to return (default 20)
    """
    try:
        client = _get_client()
        result = await client.list_runs(limit=limit)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_run(run_id: str) -> str:
    """Get details of a specific deployment run.

    Args:
        run_id: The run UUID
    """
    try:
        client = _get_client()
        result = await client.get_run(run_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── GitHub Tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def check_github_status() -> str:
    """Check GitHub API connection status."""
    try:
        client = _get_client()
        result = await client.get_github_status()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_github_repos() -> str:
    """List GitHub repositories accessible to Kratos."""
    try:
        client = _get_client()
        result = await client.list_github_repos()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def refresh_github_repos() -> str:
    """Refresh the cached list of GitHub repositories."""
    try:
        client = _get_client()
        result = await client.refresh_github_repos()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_github_branches(owner: str, repo: str) -> str:
    """List branches for a GitHub repository.

    Args:
        owner: Repository owner (e.g., "A-Somniatore")
        repo: Repository name (e.g., "kratos-api")
    """
    try:
        client = _get_client()
        result = await client.get_github_branches(owner, repo)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_github_commits(owner: str, repo: str, branch: str | None = None) -> str:
    """List recent commits for a GitHub repository.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Filter by branch (optional)
    """
    try:
        client = _get_client()
        result = await client.get_github_commits(owner, repo, branch=branch)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Harbor Tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def list_container_images() -> str:
    """List container image repositories in Harbor registry."""
    try:
        client = _get_client()
        result = await client.list_harbor_repos()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_container_artifacts(repository: str) -> str:
    """List image artifacts (tags, digests) for a Harbor repository.

    Args:
        repository: Repository name (e.g., "kratos/api")
    """
    try:
        client = _get_client()
        result = await client.list_harbor_artifacts(repository)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def cleanup_harbor() -> str:
    """Clean up old/unused container images from Harbor registry."""
    try:
        client = _get_client()
        result = await client.cleanup_harbor()
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Infrastructure Tools ────────────────────────────────────────────────────


@mcp.tool()
async def list_machine_pools() -> str:
    """List machine pools (named groups of K8s nodes for targeted deployment)."""
    try:
        client = _get_client()
        result = await client.list_machine_pools()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_machine_pool(pool_id: str) -> str:
    """Get details of a specific machine pool.

    Args:
        pool_id: The machine pool UUID
    """
    try:
        client = _get_client()
        result = await client.get_machine_pool(pool_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def create_machine_pool(
    name: str,
    node_selector: dict[str, str],
    description: str = "",
) -> str:
    """Create a machine pool for targeting specific K8s nodes.

    Args:
        name: Pool name (e.g., "gpu-nodes")
        node_selector: Node selector labels (e.g., {"kratos.io/pool": "gpu"})
        description: Optional description
    """
    try:
        client = _get_client()
        data: dict[str, Any] = {
            "name": name,
            "nodeSelector": node_selector,
            "description": description,
        }
        result = await client.create_machine_pool(data)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def delete_machine_pool(pool_id: str) -> str:
    """Delete a machine pool.

    Args:
        pool_id: The machine pool UUID
    """
    try:
        client = _get_client()
        result = await client.delete_machine_pool(pool_id)
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_cluster_nodes() -> str:
    """List Kubernetes cluster nodes with labels, taints, and capacity."""
    try:
        client = _get_client()
        result = await client.list_cluster_nodes()
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Settings Tools ──────────────────────────────────────────────────────────


@mcp.tool()
async def get_settings() -> str:
    """Get Kratos platform settings."""
    try:
        client = _get_client()
        result = await client.get_settings()
        return _fmt(result)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def update_settings(settings: dict[str, Any]) -> str:
    """Update Kratos platform settings.

    Args:
        settings: Settings key-value pairs to update
    """
    try:
        client = _get_client()
        result = await client.update_settings(settings)
        return _fmt(result)
    except Exception as e:
        return _err(e)


# ── Entry Point ──────────────────────────────────────────────────────────────


def main():
    mcp.run()


if __name__ == "__main__":
    main()
