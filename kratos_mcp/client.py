"""Async HTTP client for the Kratos API."""

from __future__ import annotations

from typing import Any

import httpx


class KratosClient:
    """Async client for interacting with the Kratos deployment API."""

    def __init__(self, base_url: str, token: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kratos-mcp/0.1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    async def close(self):
        await self._client.aclose()

    # ── Health ───────────────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        r = await self._client.get("/healthz")
        r.raise_for_status()
        return r.json()

    async def health_detailed(self) -> dict[str, Any]:
        r = await self._client.get("/healthz/detailed")
        r.raise_for_status()
        return r.json()

    async def services_health(self) -> dict[str, Any]:
        r = await self._client.get("/health/services")
        r.raise_for_status()
        return r.json()

    # ── Assets ───────────────────────────────────────────────────────────────

    async def list_assets(self, limit: int = 50) -> dict[str, Any]:
        r = await self._client.get("/api/v1/assets/", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    async def get_asset(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}")
        r.raise_for_status()
        return r.json()

    async def create_asset(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/assets/", json=data)
        r.raise_for_status()
        return r.json()

    async def delete_asset(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.delete(f"/api/v1/assets/{asset_id}")
        r.raise_for_status()
        return r.json()

    async def sync_asset(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.post(f"/api/v1/assets/{asset_id}/sync")
        r.raise_for_status()
        return r.json()

    # ── Deployment ───────────────────────────────────────────────────────────

    async def deploy_asset(self, asset_id: str, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post(f"/api/v1/assets/{asset_id}/deploy", json=data, timeout=300)
        r.raise_for_status()
        return r.json()

    async def rollback_asset(self, asset_id: str, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post(f"/api/v1/assets/{asset_id}/rollback", json=data, timeout=300)
        r.raise_for_status()
        return r.json()

    async def list_deployments(self, limit: int = 20) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/deployments/", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    async def get_deployment(self, deployment_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/deployments/{deployment_id}")
        r.raise_for_status()
        return r.json()

    async def cancel_deployment(self, deployment_id: str) -> dict[str, Any]:
        r = await self._client.post(f"/api/v1/deployments/{deployment_id}/cancel")
        r.raise_for_status()
        return r.json()

    # ── Deployment Logs ──────────────────────────────────────────────────────

    async def get_deployment_logs(
        self, deployment_id: str, tail: int = 100
    ) -> dict[str, Any] | str:
        r = await self._client.get(
            f"/api/v1/deployments/{deployment_id}/logs", params={"tail": tail}
        )
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return r.text

    async def list_deployment_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/deployments/logs", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    async def get_deployment_logs_by_asset(
        self, asset_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        r = await self._client.get(
            f"/api/v1/deployments/logs/asset/{asset_id}", params={"limit": limit}
        )
        r.raise_for_status()
        return r.json()

    # ── Environment Config ───────────────────────────────────────────────────

    async def get_env_config(self, asset_id: str) -> dict[str, Any] | None:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/env-config")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    async def set_env_variable(
        self, asset_id: str, key: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        r = await self._client.put(
            f"/api/v1/assets/{asset_id}/env-config/variables/{key}", json=data
        )
        r.raise_for_status()
        return r.json()

    # ── Asset Health & Metrics ───────────────────────────────────────────────

    async def get_asset_health(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/health")
        r.raise_for_status()
        return r.json()

    async def get_asset_metrics(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/metrics")
        r.raise_for_status()
        return r.json()

    async def get_asset_readiness(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/readiness")
        r.raise_for_status()
        return r.json()

    # ── Kubernetes ───────────────────────────────────────────────────────────

    async def get_k8s_status(self, namespace: str, name: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/deployments/k8s/{namespace}/{name}")
        r.raise_for_status()
        return r.json()

    async def get_k8s_logs(
        self, namespace: str, name: str, tail: int = 100
    ) -> dict[str, Any] | str:
        r = await self._client.get(
            f"/api/v1/deployments/k8s/{namespace}/{name}/logs", params={"tail": tail}
        )
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return r.text

    async def get_k8s_events(self, namespace: str, name: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/deployments/k8s/{namespace}/{name}/events")
        r.raise_for_status()
        return r.json()

    async def scale_deployment(
        self, namespace: str, name: str, replicas: int
    ) -> dict[str, Any]:
        r = await self._client.post(
            f"/api/v1/deployments/k8s/{namespace}/{name}/scale",
            json={"replicas": replicas},
        )
        r.raise_for_status()
        return r.json()

    # ── Build ────────────────────────────────────────────────────────────────

    async def get_build_status(self, job_name: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/deployments/builds/{job_name}")
        r.raise_for_status()
        return r.json()

    async def get_build_logs(self, job_name: str) -> dict[str, Any] | str:
        r = await self._client.get(f"/api/v1/deployments/builds/{job_name}/logs")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return r.text

    # ── Diff & Impact ────────────────────────────────────────────────────────

    async def get_diff(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/diff")
        r.raise_for_status()
        return r.json()

    async def get_impact(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/impact")
        r.raise_for_status()
        return r.json()

    # ── Analytics ────────────────────────────────────────────────────────────

    async def get_analytics_dashboard(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/analytics/dashboard")
        r.raise_for_status()
        return r.json()

    async def get_deployment_trends(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/analytics/deployments/trends")
        r.raise_for_status()
        return r.json()

    # ── GitHub ───────────────────────────────────────────────────────────────

    async def get_github_status(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/github/status")
        r.raise_for_status()
        return r.json()

    async def list_github_repos(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/github/repos")
        r.raise_for_status()
        return r.json()

    # ── Harbor ───────────────────────────────────────────────────────────────

    async def list_harbor_repos(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/harbor/repositories")
        r.raise_for_status()
        return r.json()

    # ── Machine Pools ────────────────────────────────────────────────────────

    async def list_machine_pools(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/machine-pools/")
        r.raise_for_status()
        return r.json()

    async def list_cluster_nodes(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/machine-pools/nodes")
        r.raise_for_status()
        return r.json()

    # ── Preview Environments ──────────────────────────────────────────────────

    async def list_previews(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/preview/")
        r.raise_for_status()
        return r.json()

    async def create_preview(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/preview/", json=data, timeout=300)
        r.raise_for_status()
        return r.json()

    async def get_preview(self, deployment_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/preview/{deployment_id}")
        r.raise_for_status()
        return r.json()

    async def get_preview_logs(self, deployment_id: str) -> dict[str, Any] | str:
        r = await self._client.get(f"/api/v1/preview/{deployment_id}/logs")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return r.text

    async def delete_preview(self, deployment_id: str) -> dict[str, Any]:
        r = await self._client.delete(f"/api/v1/preview/{deployment_id}")
        r.raise_for_status()
        return r.json()

    # ── Packages ──────────────────────────────────────────────────────────────

    async def get_package_workspace(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/packages/{asset_id}/workspace")
        r.raise_for_status()
        return r.json()

    async def publish_package(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/packages/publish", json=data, timeout=300)
        r.raise_for_status()
        return r.json()

    async def get_publish_status(self, publish_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/packages/{publish_id}/status")
        r.raise_for_status()
        return r.json()

    async def get_publish_history(self, asset_id: str) -> list[dict[str, Any]]:
        r = await self._client.get(f"/api/v1/packages/{asset_id}/history")
        r.raise_for_status()
        return r.json()

    # ── Schedule ──────────────────────────────────────────────────────────────

    async def list_schedule_presets(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/schedule/presets")
        r.raise_for_status()
        return r.json()

    async def preview_schedule(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/schedule/preview", json=data)
        r.raise_for_status()
        return r.json()

    async def get_asset_schedule(self, asset_id: str) -> dict[str, Any] | None:
        r = await self._client.get(f"/api/v1/schedule/assets/{asset_id}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    async def update_asset_schedule(
        self, asset_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        r = await self._client.patch(f"/api/v1/schedule/assets/{asset_id}", json=data)
        r.raise_for_status()
        return r.json()

    # ── Dockerfile ────────────────────────────────────────────────────────────

    async def get_dockerfile(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/dockerfile/{asset_id}")
        r.raise_for_status()
        return r.json()

    async def generate_dockerfile(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/dockerfile/generate", json=data)
        r.raise_for_status()
        return r.json()

    async def push_dockerfile(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/dockerfile/push", json=data)
        r.raise_for_status()
        return r.json()

    async def get_dockerfile_history(self, asset_id: str) -> list[dict[str, Any]]:
        r = await self._client.get(f"/api/v1/dockerfile/history/{asset_id}")
        r.raise_for_status()
        return r.json()

    # ── Nginx ─────────────────────────────────────────────────────────────────

    async def list_nginx_templates(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/nginx/templates")
        r.raise_for_status()
        return r.json()

    async def generate_nginx_config(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/nginx/generate", json=data)
        r.raise_for_status()
        return r.json()

    async def validate_nginx_config(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/nginx/validate", json=data)
        r.raise_for_status()
        return r.json()

    # ── Hermes ────────────────────────────────────────────────────────────────

    async def get_hermes_status(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/hermes/status")
        r.raise_for_status()
        return r.json()

    async def list_hermes_assets(self) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/hermes/assets")
        r.raise_for_status()
        return r.json()

    async def get_hermes_asset(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/hermes/assets/{asset_id}")
        r.raise_for_status()
        return r.json()

    # ── Runs ──────────────────────────────────────────────────────────────────

    async def create_deployment_plan(
        self, asset_id: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        r = await self._client.post(
            f"/api/v1/runs/assets/{asset_id}/plan", json=data or {}
        )
        r.raise_for_status()
        return r.json()

    async def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        r = await self._client.get("/api/v1/runs/runs", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    async def get_run(self, run_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/runs/runs/{run_id}")
        r.raise_for_status()
        return r.json()

    # ── GitHub (extended) ─────────────────────────────────────────────────────

    async def get_github_branches(
        self, owner: str, repo: str
    ) -> list[dict[str, Any]]:
        r = await self._client.get(f"/api/v1/github/repos/{owner}/{repo}/branches")
        r.raise_for_status()
        return r.json()

    async def get_github_commits(
        self, owner: str, repo: str, branch: str | None = None
    ) -> list[dict[str, Any]]:
        params = {}
        if branch:
            params["branch"] = branch
        r = await self._client.get(
            f"/api/v1/github/repos/{owner}/{repo}/commits", params=params
        )
        r.raise_for_status()
        return r.json()

    async def refresh_github_repos(self) -> dict[str, Any]:
        r = await self._client.post("/api/v1/github/repos/refresh")
        r.raise_for_status()
        return r.json()

    # ── Harbor (extended) ─────────────────────────────────────────────────────

    async def list_harbor_artifacts(self, repository: str) -> list[dict[str, Any]]:
        r = await self._client.get(
            f"/api/v1/harbor/repositories/{repository}/artifacts"
        )
        r.raise_for_status()
        return r.json()

    async def cleanup_harbor(self) -> dict[str, Any]:
        r = await self._client.post("/api/v1/harbor/cleanup")
        r.raise_for_status()
        return r.json()

    # ── Environment (utilities) ───────────────────────────────────────────────

    async def sync_env_config(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.post(f"/api/v1/assets/{asset_id}/env-config/sync")
        r.raise_for_status()
        return r.json()

    async def validate_env_vars(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/env/validate", json=data)
        r.raise_for_status()
        return r.json()

    # ── Machine Pools (extended) ──────────────────────────────────────────────

    async def create_machine_pool(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/api/v1/machine-pools/", json=data)
        r.raise_for_status()
        return r.json()

    async def get_machine_pool(self, pool_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/machine-pools/{pool_id}")
        r.raise_for_status()
        return r.json()

    async def update_machine_pool(
        self, pool_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        r = await self._client.put(f"/api/v1/machine-pools/{pool_id}", json=data)
        r.raise_for_status()
        return r.json()

    async def delete_machine_pool(self, pool_id: str) -> dict[str, Any]:
        r = await self._client.delete(f"/api/v1/machine-pools/{pool_id}")
        r.raise_for_status()
        return r.json()

    async def assign_pool_assets(
        self, pool_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        r = await self._client.post(
            f"/api/v1/machine-pools/{pool_id}/assets", json=data
        )
        r.raise_for_status()
        return r.json()

    # ── Asset (extended) ──────────────────────────────────────────────────────

    async def update_asset(
        self, asset_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        r = await self._client.put(f"/api/v1/assets/{asset_id}", json=data)
        r.raise_for_status()
        return r.json()

    async def get_asset_suggestions(self, asset_id: str) -> dict[str, Any]:
        r = await self._client.get(f"/api/v1/assets/{asset_id}/suggestions")
        r.raise_for_status()
        return r.json()

    # ── System ────────────────────────────────────────────────────────────────

    async def get_system_version(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/system/version")
        r.raise_for_status()
        return r.json()

    async def get_api_metadata(self) -> dict[str, Any]:
        r = await self._client.get("/meta")
        r.raise_for_status()
        return r.json()

    # ── Settings ──────────────────────────────────────────────────────────────

    async def get_settings(self) -> dict[str, Any]:
        r = await self._client.get("/api/v1/settings/")
        r.raise_for_status()
        return r.json()

    async def update_settings(self, data: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.put("/api/v1/settings/", json=data)
        r.raise_for_status()
        return r.json()
