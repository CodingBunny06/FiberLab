"""FiberLab Guardian dashboard."""

import os
import tempfile
from pathlib import Path

import streamlit as st

from components.page_layout import render_page_header
from guardian.candidate_downloader import CandidateDownloadError
from guardian.github_client import GitHubAPIError
from guardian.github_commenter import (
    GitHubCommentError,
    format_guardian_comment,
    publish_guardian_comment,
)
from guardian.github_integration import inspect_pull_request
from guardian.reporter import format_report, generate_report


def render_report_findings(report) -> None:
    """Render Guardian diagnostic findings."""

    if not report.diagnostics:
        st.info("No diagnostic findings were generated.")
        return

    status_icons = {
        "PASS": "✅",
        "FAIL": "❌",
        "PENDING": "⏳",
    }

    for diagnostic in report.diagnostics:
        icon = status_icons.get(diagnostic.status, "ℹ️")

        with st.expander(
            f"{icon} {diagnostic.file} — {diagnostic.status}",
            expanded=diagnostic.status == "FAIL",
        ):
            st.write(f"**Severity:** {diagnostic.severity}")
            st.write(f"**Finding:** {diagnostic.message}")
            st.write(f"**Recommendation:** {diagnostic.recommendation}")


def render_report_summary(report) -> None:
    """Render the Guardian report status and summary metrics."""

    if report.overall_status == "PASS":
        st.success("Overall Status: PASS")
    elif report.overall_status == "FAIL":
        st.error("Overall Status: FAIL")
    else:
        st.warning("Overall Status: PENDING")

    passed_column, failed_column, pending_column = st.columns(3)

    passed_column.metric("Passed", report.passed)
    failed_column.metric("Failed", report.failed)
    pending_column.metric("Pending", report.pending)


def render_local_inspection() -> None:
    """Render the local project inspection workflow."""

    st.subheader("Local Project Inspection")

    st.write(
        "Run Guardian against the current FiberLab project to check "
        "module contracts, imports, syntax, and code structure."
    )

    st.info(
        "Local inspection only. Guardian does not execute downloaded "
        "pull-request code or modify project files."
    )

    if st.button(
        "Run Guardian Inspection",
        type="primary",
        use_container_width=True,
        key="guardian_local_inspection",
    ):
        project_root = Path(__file__).resolve().parents[1]

        with st.spinner("Inspecting FiberLab project..."):
            try:
                report = generate_report(project_root)

                st.session_state["guardian_report"] = report
                st.session_state["guardian_report_text"] = format_report(report)
                st.session_state["guardian_error"] = None

            except (OSError, ValueError, RuntimeError) as error:
                st.session_state["guardian_error"] = str(error)
                st.session_state.pop("guardian_report", None)
                st.session_state.pop("guardian_report_text", None)

    error_message = st.session_state.get("guardian_error")

    if error_message:
        st.error(f"Guardian inspection failed: {error_message}")

    report = st.session_state.get("guardian_report")

    if report is None:
        st.caption("Run a local inspection to see its results.")
        return

    st.divider()
    st.subheader("Local Inspection Results")

    render_report_summary(report)

    st.subheader("Diagnostic Findings")
    render_report_findings(report)

    st.subheader("Full Guardian Report")

    report_text = st.session_state["guardian_report_text"]

    st.download_button(
        label="Download Inspection Report",
        data=report_text,
        file_name="fiberlab_guardian_report.txt",
        mime="text/plain",
        use_container_width=True,
        key="guardian_local_download",
    )

    with st.expander("View full text report"):
        st.code(report_text, language="text")


def render_github_inspection() -> None:
    """Render GitHub pull request inspection and reporting."""

    st.divider()
    st.subheader("GitHub Pull Request Inspection")

    st.write(
        "Inspect a pull request against the current FiberLab project. "
        "Guardian downloads the changed files and checks them in an "
        "isolated temporary integration workspace."
    )

    st.warning(
        "PR inspection is static only. Downloaded pull-request code "
        "is not executed. Publishing a report requires a separate "
        "explicit action."
    )

    repository = st.text_input(
        "GitHub Repository",
        value="CodingBunny06/FiberLab",
        help="Use the owner/repository format.",
        key="guardian_github_repository",
    ).strip()

    pr_number = st.number_input(
        "Pull Request Number",
        min_value=1,
        step=1,
        value=1,
        key="guardian_github_pr_number",
    )

    if st.button(
        "Inspect GitHub Pull Request",
        type="primary",
        use_container_width=True,
        key="guardian_inspect_pr",
    ):
        project_root = Path(__file__).resolve().parents[1]

        st.session_state.pop("guardian_pr_result", None)
        st.session_state.pop("guardian_pr_error", None)
        st.session_state.pop("guardian_pr_comment_url", None)
        st.session_state.pop("guardian_pr_publish_error", None)

        with st.spinner("Downloading and inspecting pull request..."):
            try:
                with tempfile.TemporaryDirectory(
                    prefix="fiberlab-guardian-"
                ) as temporary_directory:
                    temporary_root = Path(temporary_directory)

                    candidate_workspace = temporary_root / "candidate"
                    integration_workspace = temporary_root / "integration"

                    result = inspect_pull_request(
                        repository=repository,
                        pr_number=int(pr_number),
                        project_root=project_root,
                        candidate_workspace=candidate_workspace,
                        integration_workspace=integration_workspace,
                    )

                    comment = format_guardian_comment(result.report)

                    st.session_state["guardian_pr_result"] = result
                    st.session_state["guardian_pr_comment"] = comment
                    st.session_state["guardian_pr_repository"] = repository
                    st.session_state["guardian_pr_number"] = int(pr_number)

            except (
                CandidateDownloadError,
                GitHubAPIError,
                GitHubCommentError,
                OSError,
                ValueError,
                RuntimeError,
            ) as error:
                st.session_state["guardian_pr_error"] = str(error)

    error_message = st.session_state.get("guardian_pr_error")

    if error_message:
        st.error(f"GitHub PR inspection failed: {error_message}")

    result = st.session_state.get("guardian_pr_result")

    if result is None:
        st.caption("Inspect a pull request to see its results here.")
        return

    st.divider()
    st.subheader("Pull Request Details")

    pull_request = result.pull_request

    st.write(f"**Title:** {pull_request.title}")
    st.write(f"**PR Number:** #{pull_request.number}")
    st.write(f"**Source Branch:** `{pull_request.head_branch}`")
    st.write(f"**Target Branch:** `{pull_request.base_branch}`")
    st.write(f"**Commit:** `{pull_request.head_sha}`")

    st.subheader("Changed Files")

    changed_file_rows = [
        {
            "File": changed_file.path,
            "Status": changed_file.status,
            "Additions": changed_file.additions,
            "Deletions": changed_file.deletions,
            "Changes": changed_file.changes,
        }
        for changed_file in result.changed_files
    ]

    st.dataframe(
        changed_file_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("PR Inspection Results")

    render_report_summary(result.report)

    st.subheader("Diagnostic Findings")
    render_report_findings(result.report)

    st.divider()
    st.subheader("GitHub Comment Preview")

    comment = st.session_state["guardian_pr_comment"]

    with st.expander("Preview Markdown comment", expanded=True):
        st.code(comment, language="markdown")

    st.download_button(
        label="Download GitHub Comment",
        data=comment,
        file_name=f"fiberlab_guardian_pr_{pull_request.number}.md",
        mime="text/markdown",
        use_container_width=True,
        key="guardian_pr_comment_download",
    )

    st.divider()
    st.subheader("Publish Report to GitHub")

    st.info(
        "Publishing creates a new comment on the pull request. "
        "Guardian will not publish anything unless you click the button."
    )

    if st.button(
        "Publish Guardian Report to PR",
        type="primary",
        use_container_width=True,
        key="guardian_publish_pr",
    ):
        token = os.getenv("GITHUB_TOKEN")

        with st.spinner("Publishing Guardian report to GitHub..."):
            try:
                publish_result = publish_guardian_comment(
                    repository=st.session_state["guardian_pr_repository"],
                    pr_number=st.session_state["guardian_pr_number"],
                    report=result.report,
                    token=token,
                )

                st.session_state["guardian_pr_comment_url"] = publish_result.comment_url
                st.session_state["guardian_pr_publish_error"] = None

            except (GitHubCommentError, OSError, ValueError) as error:
                st.session_state.pop("guardian_pr_comment_url", None)
                st.session_state["guardian_pr_publish_error"] = str(error)

    publish_error = st.session_state.get("guardian_pr_publish_error")

    if publish_error:
        st.error(f"Comment publishing failed: {publish_error}")

    comment_url = st.session_state.get("guardian_pr_comment_url")

    if comment_url:
        st.success("Guardian report published successfully!")
        st.markdown(f"[Open published GitHub comment]({comment_url})")


def render() -> None:
    """Render the FiberLab Guardian dashboard."""

    render_page_header(
        title="FiberLab Guardian",
        caption="Automated Code Inspection & Diagnostics",
        description=(
            "Inspect FiberLab code, identify structural issues, "
            "and review automated diagnostic reports."
        ),
    )

    render_local_inspection()
    render_github_inspection()
