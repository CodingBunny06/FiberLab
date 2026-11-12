"""Tests for the FiberLab Guardian reporter."""

from guardian.reporter import format_report, generate_report


def test_report_detects_pending_modules(tmp_path):
    report = generate_report(tmp_path)

    assert report.overall_status == "PENDING"
    assert report.pending > 0


def test_report_counts_inspection_failures(tmp_path):
    report = generate_report(tmp_path)

    assert report.failed == 0


def test_report_contains_all_summary_sections(tmp_path):
    report = generate_report(tmp_path)
    output = format_report(report)

    assert "FIBERLAB GUARDIAN REPORT" in output
    assert "Overall Status:" in output
    assert "Passed:" in output
    assert "Failed:" in output
    assert "Pending:" in output


def test_report_contains_diagnostic_details(tmp_path):
    report = generate_report(tmp_path)
    output = format_report(report)

    assert "DIAGNOSTICS" in output
    assert "Recommendation:" in output
