"""Тестирование отсутствия устаревшего эндпоинта перезагрузки (stateless концепция)."""

from fastapi.testclient import TestClient

from src.backend.main import app


def test_api_reload_glossary_removed():
    """Проверка, что /api/v1/glossary/reload удалён и возвращает 404 (сервис stateless)."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/api/v1/glossary/reload", headers={"X-API-Key": "dev-token-change-me"})
    assert resp.status_code == 404

