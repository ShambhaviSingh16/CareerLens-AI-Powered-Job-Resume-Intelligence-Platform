# Verification record

This record distinguishes observed local results from configured or unperformed checks. It is not a claim that the application has already run in Azure or that GitHub's remote workflow has executed.

## Observed

- 53 Python tests passed locally, including authentication, ownership, parsing, evidence validation, failure handling, quotas, streamed body limits, account deletion, retention, SPA routing, and evaluation contracts. The coverage run reported 93% statement coverage; see the commands in the root README to reproduce it.
- Ruff checks (`--select F`), frontend ESLint, and the production Vite build passed.
- The full Docker image built under Docker Engine in Ubuntu WSL2 with Python 3.12 and Node 22. Compose started PostgreSQL 16 and the app, and the app/database health checks passed.
- The real container-backed smoke script passed registration, login, authorization, history, SPA fallback, and account cleanup without an AI call.
- The opt-in live smoke check also passed synthetic PDF upload/parsing, a real Groq call, response validation, Python scoring, PostgreSQL persistence, retrieval, report deletion, and account cleanup.
- All six Playwright desktop/mobile tests passed against the actual container-backed application without mocked account APIs. They cover navigation, resume annotations, skill filters, keyboard tabs, JSON export, registration/login, form reset, and account deletion. Screenshots are in `docs/screenshots/`.
- The final PostgreSQL migration/model check passed with no new upgrade operations detected, including migration 0003 for anonymous daily quota totals.
- Azure Bicep 0.48.1 compiled the infrastructure locally without creating resources.
- The Groq model list was checked with the configured account. The old Llama default returned 404. Qwen 3.8 27B was available; a large output budget returned 429, while the smaller 2,200-token budget produced valid responses.
- Live evaluation of Qwen on the 12-case/25-requirement synthetic challenge set returned 12 valid responses: label accuracy 84%, macro F1 0.7202, weighted-score MAE 8 points. The oracle-extraction keyword baseline scored 44%, macro F1 0.3188, score MAE 52.17 points. Results are committed in `backend/evaluation/results/`.

## Evaluation limitations and error analysis

All 11 expected missing labels were identified as missing. Of 10 strong labels, 9 were strong and 1 partial. Of 4 partial labels, only 1 was partial and 3 were marked missing. This version is conservative about related/limited evidence; that is the main observed failure mode. This is a small development set with manual labels and no independent holdout, not a general accuracy or hiring benchmark.

Failed exploratory runs are retained separately. They establish configuration failure behavior, not model quality. The full successful report is `live-qwen-full.json`; `baseline.json` is the keyword baseline.

## Still requires external execution

- The GitHub workflow must be pushed and run in the user's repository to establish a remote CI result.
- Azure deployment is deliberately disabled. An account, protected subscription/credits, reviewed plan, and explicit deployment opt-in are required. Compilation is not subscription validation or deployment verification.
- Provider/model availability and free-tier limits can change. Re-run the evaluation after a model or prompt change.

## Local runtime note

The first detached WSL run later exited with container code 255 and `OOMKilled=false` when the WSL VM stopped. Keeping a foreground WSL session active restored stable Windows-to-container connections, after which the full suite and live smoke check passed. On this Windows machine, keep the documented attached Compose terminal open during previews. This is distinct from Docker Desktop or a hosted cloud runtime.

## Dependency findings

Nonbreaking npm security updates moved Axios to 1.21.0 and Vite to 8.3.5 and removed the reported high-severity findings. Six moderate findings remain in ESLint's development dependency chain through minimatch; npm reported no compatible fix. They are not shipped in the Python runtime/static browser bundle. Recheck advisories before publication and update the tooling when a compatible patch is available; no forced breaking upgrade was applied.

Third-party Python testing libraries emit deprecation warnings with the tested versions. The warnings do not represent test failures. Python package versions are constrained and the Docker bases are pinned by digest; update those pins deliberately and rerun the checks for future releases.
