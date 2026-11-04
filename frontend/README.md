# CareerLens frontend

React 19, Vite, React Router, and CSS/Tailwind. This is the interface for the Python/FastAPI application.

## Develop

Run the backend first, then:

```bash
npm ci
npm run dev
```

The default API base is `http://localhost:8000`. A local `.env` can set `VITE_API_BASE_URL`; never place provider/database secrets in Vite variables.

The root Dockerfile builds with `VITE_API_BASE_URL=/api` and copies the static assets into the Python image. No Node process is needed in the runtime container. Standalone static hosting remains supported by `vercel.json`, but is not the primary container deployment path.

For Vercel, select **Root Directory: `frontend`**, **Framework: Vite**, and **Output Directory: `dist`**. See the [deployment and 500-error guide](../docs/vercel.md), including the public API requirement for account and AI features.

## Routes

- `/`: landing and interactive illustrative resume annotations.
- `/sample`: fictional report, requiring no account/provider call.
- `/signup`, `/login`: account forms.
- `/dashboard`: protected upload, history, report inspection, and deletion.
- `/settings`: password-confirmed account deletion.

## Checks

```bash
npm run lint
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests expect the full stack at `http://127.0.0.1:8080`. Set `PLAYWRIGHT_BASE_URL` to change it. `PLAYWRIGHT_API_URL` can point tests at a separate native API. `PLAYWRIGHT_CHROME_PATH` can select an existing local Chrome binary instead of downloading Chromium.

Tests use real registration/login/history/deletion, unique synthetic accounts, and cleanup. They do not call the LLM. Desktop and mobile projects run serially to respect authentication throttling. Traces and screenshots are retained on failure in ignored folders; do not publish them if you rerun tests with personal data.

## Design

Warm paper surfaces, ink typography, restrained orange actions, and green/amber status cues. Status labels accompany colors. Report tabs support arrow/Home/End keys, forms have associated labels, and reduced-motion preferences are respected. The sample explicitly distinguishes illustrative content from live analysis.
