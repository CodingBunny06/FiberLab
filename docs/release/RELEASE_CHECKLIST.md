# FiberLab v1.0 Release Readiness Checklist

## A. Scope freeze
- [ ] v1.0 feature scope is confirmed.
- [ ] Deferred features are excluded or labelled as future work.
- [ ] Physics and visualization contracts are approved by their owners.
- [ ] No unresolved duplicate or competing implementation PRs remain.

## B. Code and integration
- [ ] Application pages use the agreed module APIs.
- [ ] Physics and visualization remain independent of Streamlit.
- [ ] Required v1.0 features are integrated.
- [ ] No placeholder is presented as a completed simulation.
- [ ] Error handling and input validation are verified.

## C. Quality gates
- [ ] Ruff lint passes on the release-candidate commit.
- [ ] Ruff format check passes on the release-candidate commit.
- [ ] Pytest passes on the release-candidate commit.
- [ ] Manual feature walkthrough passes.
- [ ] CI passes on the exact release-candidate commit.
- [ ] No unresolved blocking or high-severity findings remain.

## D. Documentation
- [ ] README accurately describes implemented features.
- [ ] Installation and launch instructions are verified.
- [ ] Module contracts reflect agreed interfaces.
- [ ] Known limitations are documented.
- [ ] Release notes match shipped implementation.
- [ ] Contributors and ownership are represented accurately.

## E. Release approval
- [ ] Required PR reviews are complete.
- [ ] Project lead explicitly approves the merge.
- [ ] Main branch is verified after merge.
- [ ] Release tag is created only after final validation.
- [ ] Release artifacts and notes are published.

Do not mark the release ready until every required gate has evidence.
