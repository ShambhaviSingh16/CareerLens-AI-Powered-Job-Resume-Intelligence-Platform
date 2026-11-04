# Architecture and engineering decisions

## Request lifecycle

1. A same-origin React client sends a bearer JWT and a multipart upload to `/api/analyses` in the container deployment. Local Vite development uses the separate API URL without the `/api` prefix.
2. ASGI middleware caps the full request at 6 MiB, tags the response with a generated request ID, applies a per-IP authentication throttle, and logs method/path/status/duration without bodies or secrets.
3. FastAPI validates credentials and binds all reads/writes to the authenticated user.
4. The parser accepts bounded text-based PDF/DOCX inputs. DOCX archive size and entry counts are checked before extraction. No original file is persisted.
5. A semaphore bounds provider concurrency per process. PostgreSQL transaction advisory locking serializes quota reservations across overlapping instances; quota attempts persist independently of deletable results.
6. A versioned system prompt treats documents as data. Groq returns JSON; Pydantic validates its shape and application code verifies quotations. This validates provenance, not the truth of the model's interpretation.
7. Python calculates a weighted score. Model/version, prompt hash, token usage, and timing are saved with the result.
8. Resume text, job text, and analysis commit together after a successful provider response. Provider failures store only a quota attempt.

## Why these choices

- **FastAPI + SQLAlchemy + PostgreSQL:** typed HTTP contracts, explicit persistence, migrations, ownership checks, and transactions. SQLite keeps non-container local development accessible.
- **One container for UI/API:** the production build has one origin, one image, and one deployable artifact. It removes cross-origin browser configuration from the cloud exercise. Separate frontend hosting remains supported for experimentation.
- **Direct HTTPX provider client:** the current workload needs one bounded JSON request. A framework dependency would not itself improve evaluation or grounding.
- **Explicit rubric:** scoring is inspectable and versioned. It remains dependent on the LLM's extracted requirements and labels.
- **No automatic provider retries:** retries can amplify free-tier pressure. The UI shows actionable errors; the evaluator records failures.
- **Persistent quota attempts:** deleting a report cannot restore a user's request allowance.
- **Azure Container Apps:** demonstrates Docker delivery, managed HTTPS, probes, revisions, and scale-to-zero. Selection is an engineering choice, not a claim that Azure is more valued than AWS in hiring.
- **Disabled cloud deployment by default:** daily pushes run verification only. Publishing/deploying requires manual inputs and explicit repository configuration.

## Data ownership and lifecycle

Every analysis is created with the caller's user ID; arbitrary resume/job IDs are never accepted from the client. Another user's report returns 404. A report can be exported as JSON or deleted with its associated inputs. Password-confirmed account deletion removes all stored account data and invalidates its tokens because the user no longer exists. Anonymous daily attempt totals have no user identifier and remain to enforce the global budget.

`python -m maintenance --older-than-days 30` previews stale reports. Adding `--apply` deletes them and old quota records. This is operator-triggered, not an automatically enforced 30-day retention promise. Groq-side handling remains subject to Groq's policies. Database backups may have a separate lifecycle.

## Known boundaries

- Browser JWTs live in sessionStorage; XSS prevention and HTTPS remain important. No refresh tokens, password recovery, or email verification are implemented.
- Authentication rate limiting is per process and depends on the server's trusted proxy configuration for client IP. The cloud template uses one replica; this is not distributed bot protection.
- PDF OCR, full layout/ATS validation, embeddings, model training, and hiring predictions are outside this product's claims.
- Inputs are size-bounded, but document parsers are not a malware scanning service. The runtime container is nonroot, Compose is read-only, and no raw uploads are retained.
- The challenge set is synthetic and small. The recorded live run is development-set evidence, not general accuracy or hiring validation.
- Cloud creation can consume credits or incur charges outside protected allowances. No infrastructure is provisioned by normal CI runs.
- Schema migration rollback is distinct from image rollback. Back up persistent data and design later migrations for compatibility.
