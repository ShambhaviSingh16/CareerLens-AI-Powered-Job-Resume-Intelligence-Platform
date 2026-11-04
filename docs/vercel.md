# Vercel frontend deployment

Vercel hosts the React interface in this deployment. The full Docker image remains the deployment unit for the Python API and frontend together on Azure. Changing these Vercel settings does not create Azure resources.

## Existing project settings

In the CareerLens Vercel project, open **Settings → Build and Deployment** and configure:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | `Vite` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Commands and output paths are relative to `frontend`; do not use `frontend/dist` with this root. The checked-in `frontend/vercel.json` declares the framework, commands, output, and SPA fallback. It is read only when Vercel uses the correct project root.

After saving, deploy the commit containing this configuration. Redeploy without the existing build cache when correcting an old framework/root setting. Confirm the deployment's source commit and that the build log runs Vite and produces `dist/index.html`.

## Backend connection

Landing and `/sample` need no API. Registration, login, history, and AI analysis need a running, publicly reachable HTTPS API and database.

Once that API is deployed, set **VITE_API_BASE_URL** in the Vercel project's environment variables for the intended environments and rebuild:

- Full CareerLens container: `https://YOUR-APP-HOST/api`.
- Separately hosted native API with no `API_PREFIX`: `https://YOUR-API-HOST`.

Set backend `CORS_ORIGINS` to the exact frontend origin, e.g. `https://careerlens-umber.vercel.app`. Include any additional frontend origins deliberately. Vite variables are included in browser JavaScript: never put `GROQ_API_KEY`, `JWT_SECRET`, or `DATABASE_URL` there.

`localhost` on a visitor's browser refers to their computer. It cannot connect a public website to your local Docker stack. Azure deployment is disabled by default, so a working public frontend alone does not establish a working public AI service.

## Diagnosing a 500

`FUNCTION_INVOCATION_FAILED` means a Vercel server function failed; the screenshot alone does not identify its exception. The frontend in this directory needs static hosting for its pages. Check the project root/framework first. If it still invokes a function after a fresh deployment, open that deployment's runtime logs and inspect the first exception and matching request time. Do not share environment values or secrets with logs.

Verify `/` and a directly opened `/sample` load, and that browser Network requests for `/assets/...` return JavaScript/CSS. Test API-dependent flows only after configuring the public backend.

References: [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite), [project configuration](https://vercel.com/docs/project-configuration).
