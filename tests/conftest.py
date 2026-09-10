"""Shared pytest isolation for persistence-backed tests."""

import pytest


@pytest.fixture(autouse=True)
def isolate_runtime_persistence(tmp_path, monkeypatch):
    """Keep every test's cwd-relative runtime stores independent."""
    monkeypatch.chdir(tmp_path)
