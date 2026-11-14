# FiberLab Guardian — Security Notes

## 1. Purpose

FiberLab Guardian inspects candidate code changes, validates module contracts, prepares an isolated integration workspace, and runs permitted quality checks.

It is designed as a project-level code inspection and integration assistant. It is not a hardened security sandbox.

## 2. Implemented Protections

The integration engine currently implements the following protections:

- Rejects absolute candidate paths.
- Rejects candidate paths containing `..` traversal components.
- Checks candidate path components for symbolic links.
- Resolves candidate paths and verifies that they remain within the candidate root.
- Checks the destination path for an existing symbolic link before path resolution.
- Creates integration workspaces separately from the original project.
- Excludes Git metadata, virtual environments, caches, and other configured directories from workspace copies.

## 3. Known Limitations

### 3.1 Time-of-Check to Time-of-Use (TOCTOU)

Candidate path validation, containment checks, and file copying are separate filesystem operations.

A concurrent local process could modify a validated candidate or destination path between these operations. This may allow filesystem access outside the intended roots.

**Status:** Known and accepted limitation for the current project scope.

**Severity:** Medium.

**Mitigation:** Guardian should only operate on trusted local workspaces. Stronger descriptor-relative filesystem operations and race-resistant copying may be considered in a future security-hardening phase.

### 3.2 No OS-Level Execution Sandbox

The integration workspace is a separate project copy, not an operating-system security boundary.

Subprocess timeouts limit execution duration but do not prevent filesystem access, network access, or other potentially unsafe operations.

Guardian must not execute untrusted pull-request code in the normal inspection workflow.

## 4. Pull Request Inspection Policy

- Download candidate files from the exact pull-request commit.
- Perform static inspection before integration.
- Do not execute untrusted pull-request code.
- Disable quality-check execution for untrusted PR candidates.
- Require human review before accepting or merging changes.

## 5. Future Security Improvements

Potential future improvements include:

- Race-resistant filesystem operations.
- OS-level sandboxing for untrusted code execution.
- More comprehensive filesystem permission checks.
- Additional security-focused automated tests.

## 6. Security Review Disclaimer

Guardian reports are automated engineering assessments. A passing report does not guarantee that code is free from vulnerabilities, constitute security certification, or approve a pull request for merging.

Human review remains mandatory.