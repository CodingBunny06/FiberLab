import importlib
from pathlib import Path

from streamlit.testing.v1 import AppTest

import app


def test_page_modules_import_cleanly():
    for module_name in (
        "pages.home",
        "pages.fiber_explorer",
        "pages.de_broglie",
        "pages.attenuation_laboratory",
        "pages.signal_propagation",
    ):
        module = importlib.import_module(module_name)
        assert hasattr(module, "render")


def test_navigation_definitions_cover_all_pages():
    assert [definition["title"] for definition in app.PAGE_DEFINITIONS] == [
        "FiberLab",
        "Fiber Explorer",
        "De Broglie Matter Waves",
        "Attenuation Laboratory",
        "Signal Propagation",
        "Guardian",
    ]
    assert (
        sum(definition.get("default", False) for definition in app.PAGE_DEFINITIONS)
        == 1
    )


def test_main_uses_native_sidebar_navigation(monkeypatch):
    calls = {}

    monkeypatch.setattr(
        app.st,
        "set_page_config",
        lambda **kwargs: calls.setdefault("config", kwargs),
    )
    monkeypatch.setattr(
        app.st,
        "Page",
        lambda render, **kwargs: {"render": render, **kwargs},
    )
    monkeypatch.setattr(
        app.st,
        "navigation",
        lambda pages, **kwargs: (
            calls.update({"pages": pages, "navigation_kwargs": kwargs})
            or type(
                "Navigation", (), {"run": lambda self: calls.setdefault("ran", True)}
            )()
        ),
    )

    app.main()

    assert calls["config"]["page_title"] == "FiberLab"
    assert calls["navigation_kwargs"] == {"position": "sidebar"}
    assert [page["title"] for page in calls["pages"]] == [
        "FiberLab",
        "Fiber Explorer",
        "De Broglie Matter Waves",
        "Attenuation Laboratory",
        "Signal Propagation",
        "Guardian",
    ]
    assert calls["ran"] is True


def test_landing_page_renders():
    app_test = AppTest.from_file(Path(__file__).parents[1] / "app.py").run()

    assert not app_test.exception
    assert [element.value for element in app_test.title] == ["FiberLab"]
    assert any(
        "Explore the Laboratory" in element.value for element in app_test.markdown
    )


def test_simulator_pages_no_longer_render_placeholder_messages():
    root = Path(__file__).parents[1]
    for filename in (
        "fiber_explorer.py",
        "de_broglie.py",
        "attenuation_laboratory.py",
        "signal_propagation.py",
    ):
        source = (root / "pages" / filename).read_text(encoding="utf-8")
        assert "coming soon" not in source.lower()
