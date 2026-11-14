"""Tests for FiberLab result display components."""

from unittest.mock import MagicMock

from components import result_display


def test_render_result_metrics_displays_empty_message(monkeypatch):
    info_mock = MagicMock()
    monkeypatch.setattr(result_display.st, "info", info_mock)

    result_display.render_result_metrics({})

    info_mock.assert_called_once_with("No simulation results available yet.")


def test_render_result_metrics_displays_values(monkeypatch):
    columns = [MagicMock(), MagicMock()]
    columns_mock = MagicMock(return_value=columns)
    metric_mock = MagicMock()

    monkeypatch.setattr(result_display.st, "columns", columns_mock)
    monkeypatch.setattr(result_display.st, "metric", metric_mock)

    results = {
        "Output Power": "12.5 mW",
        "Total Loss": "3.2 dB",
    }

    result_display.render_result_metrics(results)

    columns_mock.assert_called_once_with(2)

    assert metric_mock.call_count == 2
    assert metric_mock.call_args_list[0].kwargs == {
        "label": "Output Power",
        "value": "12.5 mW",
    }
    assert metric_mock.call_args_list[1].kwargs == {
        "label": "Total Loss",
        "value": "3.2 dB",
    }
