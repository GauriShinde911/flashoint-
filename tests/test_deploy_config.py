"""
tests/test_deploy_config.py — STEP 10 Unit Tests for Deployment Configurations
==============================================================================
Validates render.yaml, firebase.json, .firebaserc, and .github/workflows/ingest_cron.yml.
"""

import os
import json
import yaml
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestRenderDeploymentConfig:

    def test_render_yaml_exists(self):
        render_path = os.path.join(ROOT_DIR, "render.yaml")
        assert os.path.exists(render_path), "render.yaml must exist in root"

    def test_render_yaml_valid(self):
        render_path = os.path.join(ROOT_DIR, "render.yaml")
        with open(render_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "services" in data
        assert len(data["services"]) > 0

        service = data["services"][0]
        assert service["type"] == "web"
        assert service["runtime"] == "python"
        assert "uvicorn backend.app.main:app" in service["startCommand"]
        assert "scripts/ingest.py" in service["buildCommand"]

        env_keys = [e["key"] for e in service["envVars"]]
        assert "USE_MOCK_GEMINI" in env_keys
        assert "STORAGE_BACKEND" in env_keys


class TestFirebaseDeploymentConfig:

    def test_firebase_json_exists(self):
        path = os.path.join(ROOT_DIR, "firebase.json")
        assert os.path.exists(path), "firebase.json must exist in root"

    def test_firebase_json_structure(self):
        path = os.path.join(ROOT_DIR, "firebase.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "hosting" in data
        hosting = data["hosting"]
        assert hosting["public"] == "frontend"
        assert any(r.get("destination") == "/index.html" for r in hosting.get("rewrites", []))

    def test_firebaserc_exists_and_valid(self):
        path = os.path.join(ROOT_DIR, ".firebaserc")
        assert os.path.exists(path), ".firebaserc must exist in root"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "projects" in data
        assert "default" in data["projects"]


class TestGitHubActionsWorkflow:

    def test_ingest_cron_workflow_exists(self):
        path = os.path.join(ROOT_DIR, ".github", "workflows", "ingest_cron.yml")
        assert os.path.exists(path), "ingest_cron.yml must exist"

    def test_ingest_cron_workflow_valid_yaml(self):
        path = os.path.join(ROOT_DIR, ".github", "workflows", "ingest_cron.yml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "name" in data
        # Check on trigger contains schedule and push
        triggers = data.get("on") or data.get(True) or {}
        assert "schedule" in triggers or "push" in triggers
        # Check job commands
        jobs = data.get("jobs", {})
        assert "ingest-and-test" in jobs
        steps = jobs["ingest-and-test"]["steps"]
        step_runs = [s.get("run", "") for s in steps if "run" in s]
        assert any("ingest.py" in r for r in step_runs)
        assert any("pytest" in r for r in step_runs)
