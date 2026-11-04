# Azure deployment exercise

This is the project's cloud target, not a claim that it has already been deployed. `main.bicep` defaults to `deployResources=false`. CI deployment is also disabled unless explicitly enabled. No workflow provisions infrastructure automatically.

## What runs

A Consumption Container Apps environment and one app, serving both the React build and FastAPI API from the tested Docker image. Ingress uses Azure's HTTPS hostname. Scale is 0-1 replicas; persistent data stays in external PostgreSQL (for example Neon Free). No Azure database, paid registry, VM, or Log Analytics workspace is provisioned. Console log streaming remains available; durable Azure log ingestion is deliberately disabled.

Scale-to-zero and free allowances do not guarantee a zero bill. Use an eligible student/credit subscription with its spending protection intact. Do not upgrade to pay-as-you-go for this exercise. Check resource availability and credit expiry before opting in. Budget alerts alone are not a spending cap.

## Prerequisites

1. Finish the local Compose and CI checks first. Install Docker Desktop locally (or another working Docker Engine + Compose); do not claim container verification before it passes.
2. Push to your own GitHub repository and run the manual workflow with **publish_image=true**, **deploy_azure=false**. Set the resulting GHCR package's visibility to public so Azure can pull it without credentials. The image contains application code, not `.env` files or runtime data.
3. Install Azure CLI/Bicep, log in, and select the intended protected subscription. Register `Microsoft.App` if needed.
4. Create a dedicated empty resource group, e.g. `careerlens-demo-rg`. Keep unrelated resources out of it so cleanup is unambiguous.
5. Copy `parameters.example.json` to the ignored `infra/azure/parameters.local.json`. Supply the tested image SHA tag, database URL, a generated JWT secret, and optionally the Groq Free key. Do not commit the file or paste secrets into terminal arguments. The database must be migrated separately if already populated; inspect the baseline before stamping it.

## Preview and opt in

The commands below do not run automatically. First compile and validate using your selected subscription:

```bash
az bicep build --file infra/azure/main.bicep
az deployment group validate --resource-group careerlens-demo-rg --template-file infra/azure/main.bicep --parameters @infra/azure/parameters.local.json
```

The default false flag is safe but previews no resources. To review the actual proposed resources, deliberately change `deployResources` to true in your local parameters file, then run:

```bash
az deployment group what-if --resource-group careerlens-demo-rg --template-file infra/azure/main.bicep --parameters @infra/azure/parameters.local.json
```

Only after reviewing the plan and your subscription's spending protection, create them:

```bash
az deployment group create --resource-group careerlens-demo-rg --template-file infra/azure/main.bicep --parameters @infra/azure/parameters.local.json
```

Use the output HTTPS URL. Run `python scripts/smoke.py --url https://YOUR-HOST` against the deployed stack (the script creates and deletes one synthetic account and makes no AI call). Visit `/sample`, then test live analysis only with synthetic input and your Free-plan key.

## Gated delivery after initial provisioning

Use GitHub environment `azure-demo`, ideally restricted to the main branch and protected by a reviewer. Set up an Azure federated identity for subject `repo:OWNER/REPO:environment:azure-demo`; grant access to the dedicated app/resource group only. OIDC avoids a long-lived Azure client secret. Configure environment variables:

- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_APP`

Set repository variable `ENABLE_AZURE_DEPLOY=true` only after the initial deployment and cost review. Dispatch the workflow on `main` with both publish and deploy enabled. Deployment waits for backend, evaluation-contract, frontend, infrastructure compile, and container smoke jobs, then publishes the same tested image artifact and updates the existing app. Ordinary pushes and PRs never deploy or publish.

## Observe, roll back, tear down

```bash
az containerapp logs show --name careerlens-demo --resource-group careerlens-demo-rg --type console --follow
az containerapp update --name careerlens-demo --resource-group careerlens-demo-rg --image ghcr.io/OWNER/REPO:PREVIOUS_TESTED_SHA
```

Migrations should remain backward-compatible with the previous image. An image rollback does not undo a database migration; back up data before schema changes and review migration compatibility.

After the exercise, delete only the dedicated resource group through Azure Portal, verifying its contents first. Remove demo data from Neon separately if no longer needed, disable `ENABLE_AZURE_DEPLOY`, and delete local parameter files. Neither the repo nor CI automatically deletes cloud data.

References: [Container Apps template schema](https://learn.microsoft.com/azure/templates/microsoft.app/containerapps), [GitHub OIDC](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect), [Container Apps scaling](https://learn.microsoft.com/azure/container-apps/scale-app).
