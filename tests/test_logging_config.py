import logging

from app.logging_config import configure_logging
from app.settings import settings


def test_configure_logging_applies_level_from_settings(monkeypatch):
    monkeypatch.setattr(settings, "log_level", "warning")

    configure_logging()

    assert logging.getLogger().level == logging.WARNING
    assert logging.getLogger("uvicorn.access").propagate is False
