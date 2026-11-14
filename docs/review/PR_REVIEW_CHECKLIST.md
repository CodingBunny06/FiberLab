# FiberLab Pull Request Review Checklist

## Scope and ownership
- [ ] PR has a clear purpose and limited scope.
- [ ] Changed files belong to the contributor's assigned area, or cross-team changes were agreed.
- [ ] PR does not silently replace, duplicate, or conflict with another active PR.
- [ ] Description identifies dependencies and related PRs.

## Architecture
- [ ] Physics remains independent of Streamlit.
- [ ] Visualization consumes calculated data rather than duplicating physics.
- [ ] Application pages orchestrate inputs, calculations, and display.
- [ ] Shared interfaces match `docs/integration/MODULE_CONTRACTS.md`.
- [ ] Units and angle conventions are consistent with the contract.

## Code quality and security
- [ ] Names, type hints, and docstrings are clear.
- [ ] Invalid-input handling is explicit and consistent.
- [ ] No unnecessary duplication or unrelated changes.
- [ ] No secrets or credentials are committed.
- [ ] Untrusted PR code is not executed during static inspection.

## Tests and automation
- [ ] Relevant tests were added or updated.
- [ ] Boundary and invalid-input cases are covered.
- [ ] Ruff lint and format checks pass.
- [ ] Pytest passes.
- [ ] CI results correspond to the latest PR head commit.

## Review outcome
- [ ] No unresolved blocking findings.
- [ ] Required changes are addressed and re-reviewed.
- [ ] PR head SHA is checked after the final update.
- [ ] Project lead explicitly approves the merge.

Green CI is necessary but does not replace code review. Do not merge automatically.
