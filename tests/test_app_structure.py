import importlib

import app


def test_page_modules_import_cleanly():
    for module_name in (
        "pages.fiber_explorer",
        "pages.attenuation_laboratory",
        "pages.signal_propagation",
    ):
        module = importlib.import_module(module_name)
        assert hasattr(module, "render")


def test_navigation_registry_contains_all_pages():
    assert set(app.PAGE_RENDERERS.keys()) == {
        "Fiber Explorer",
        "Attenuation Laboratory",
        "Signal Propagation",
    }


def test_main_renders_selected_page(monkeypatch):
    calls = {}

    monkeypatch.setattr(app.st, "set_page_config", lambda **kwargs: calls.setdefault("config", kwargs))

    class Sidebar:
        @staticmethod
        def radio(*_args, **_kwargs):
            return "Signal Propagation"

    monkeypatch.setattr(app.st, "sidebar", Sidebar())
    monkeypatch.setattr(
        app,
        "PAGE_RENDERERS",
        {"Signal Propagation": lambda: calls.setdefault("rendered", True)},
    )

    app.main()

    assert calls["config"]["page_title"] == "FiberLab"
    assert calls["rendered"] is True
