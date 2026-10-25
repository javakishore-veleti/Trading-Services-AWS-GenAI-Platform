# Trading-Services-AWS-GenAI-Platform

Hands-on build of a GenAI platform on Amazon EKS, one manually triggered GitHub Actions workflow per stage.

- **Plan:** [PLAN.md](PLAN.md)
- **Workflows:** `.github/workflows/NN-<name>.yml` (workflow_dispatch only)
- **Stage code:** `stages/NN-<name>/`
- **CI IAM policy starter:** `iam/ci-policy.json`

## Local sign-in

Start with `npm run local::containers::middleware::all:up`. Passwords that say `.env` are in that file and are not written here. Langfuse starts only when `LANGFUSE_ENABLED=true`. Phoenix starts only when `PHOENIX_ENABLED=true`. Open WebUI starts only when `OPENWEBUI_ENABLED=true`. n8n starts only when `N8N_ENABLED=true`. All four default to false.

| Component | Local address | User | Password |
|---|---|---|---|
| LiteLLM admin | [http://127.0.0.1:4000/ui](http://127.0.0.1:4000/ui) | `admin@localhost` | `UI_ADMIN_PASSWORD` in `.env` |
| LiteLLM API | [http://127.0.0.1:4000](http://127.0.0.1:4000) | API key | `LITELLM_MASTER_KEY` in `.env` |
| Open WebUI | [http://127.0.0.1:3001](http://127.0.0.1:3001) | `admin@example.com` | `openwebui` |
| n8n | [http://127.0.0.1:5678](http://127.0.0.1:5678) | chosen on first visit | chosen on first visit |
| Langfuse | [http://127.0.0.1:3000](http://127.0.0.1:3000) | `admin@example.com` | `langfuse` |
| Phoenix | [http://127.0.0.1:6006](http://127.0.0.1:6006) | none | none |
| Embeddings (TEI) | [http://127.0.0.1:8080/embed](http://127.0.0.1:8080/embed) | none | none |
| Ollama | [http://127.0.0.1:11434](http://127.0.0.1:11434) | none | none |
| Postgres | `127.0.0.1:5432` database `postgres` | `postgres` | `postgres` |
| Langfuse database | `127.0.0.1:5432` database `langfuse` | `langfuse` | `langfuse` |
| Strands schema | `127.0.0.1:5432` schema `strands` | `postgres` | `postgres` |
| Agno schema | `127.0.0.1:5432` schema `agno` | `postgres` | `postgres` |
| n8n database | `127.0.0.1:5432` database `n8n` | `n8n` | `n8n` |
| pgvector | `127.0.0.1:5433` database `pgvector` | `pgvector` | `pgvector` |
| pgvector connector | [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health) | none | none |
| Redis | `127.0.0.1:6379` | none | `redis` |
| MinIO console | [http://127.0.0.1:9091](http://127.0.0.1:9091) | `minio` | `miniosecret` |
| MinIO API | [http://127.0.0.1:9090](http://127.0.0.1:9090) | `minio` | `miniosecret` |
| trades-catalog-mcp | [http://127.0.0.1:8101/health](http://127.0.0.1:8101/health) | none | none |
| trades-offers-mcp | [http://127.0.0.1:8102/health](http://127.0.0.1:8102/health) | none | none |
| trades-orders-mcp | [http://127.0.0.1:8103/health](http://127.0.0.1:8103/health) | none | none |
| trades-partners-mcp | [http://127.0.0.1:8104/health](http://127.0.0.1:8104/health) | none | none |
| traders-master-data-mcp | [http://127.0.0.1:8105/health](http://127.0.0.1:8105/health) | none | none |
| traders-analytics-mcp | [http://127.0.0.1:8106/health](http://127.0.0.1:8106/health) | none | none |
| trading-desk-offers | [http://127.0.0.1:8201/health](http://127.0.0.1:8201/health) | none | none |
| trading-desk-bffs | [http://127.0.0.1:8202/health](http://127.0.0.1:8202/health) | none | none |
| trading-desk-io | [http://127.0.0.1:8203/health](http://127.0.0.1:8203/health) | none | none |
| trading-desk-order | [http://127.0.0.1:8204/health](http://127.0.0.1:8204/health) | none | none |
| trading-desk-platforms | [http://127.0.0.1:8205/health](http://127.0.0.1:8205/health) | none | none |
| Strands calculator | [http://127.0.0.1:8301/health](http://127.0.0.1:8301/health) | none | none |
| Strands loan buddy | [http://127.0.0.1:8302/health](http://127.0.0.1:8302/health) | none | none |
| Agno calculator | [http://127.0.0.1:8401/health](http://127.0.0.1:8401/health) | none | none |
| Admin portal | [http://127.0.0.1:4201](http://127.0.0.1:4201) | `admin` | `local-admin` |
| Trading Desk | [http://127.0.0.1:4200](http://127.0.0.1:4200) | `trader001` | `local-trader` |
| app-auth-service | [http://127.0.0.1:8501/health](http://127.0.0.1:8501/health) | none | none |
| traders-service | [http://127.0.0.1:8502/health](http://127.0.0.1:8502/health) | none | none |
| customer-service | [http://127.0.0.1:8503/health](http://127.0.0.1:8503/health) | none | none |
| trades-catalog-service | [http://127.0.0.1:8504/health](http://127.0.0.1:8504/health) | none | none |
| trades-offers-services | [http://127.0.0.1:8505/health](http://127.0.0.1:8505/health) | none | none |
| trades-orders-service | [http://127.0.0.1:8506/health](http://127.0.0.1:8506/health) | none | none |
| FX question service | [http://127.0.0.1:8601/health](http://127.0.0.1:8601/health) | none | none |

vLLM and SGLang are not started on this Mac. ClickHouse stays inside the Langfuse containers and has no localhost port.

## Required GitHub configuration

| Kind | Name | Notes |
|---|---|---|
| Secret | `AWS_ACCESS_KEY_ID` | CI IAM user (replaced by OIDC in Stage 19) |
| Secret | `AWS_SECRET_ACCESS_KEY` | |
| Variable | `AWS_REGION` | `us-east-1` |
| Variable | `VPC_ID` | your existing VPC |
| Environment | `sandbox` | required reviewer = you |

## Running a stage

Actions → pick the workflow → Run workflow. Run `plan` first, read the job summary, then re-run with `apply` and `confirm = APPLY`.

## Never commit

`.env`, `*.tfstate*`, `.terraform/`, `tfplan`, kubeconfig files, keys or tokens.

## Reference

This solution is built on the [GenAI on EKS starter kit](https://github.com/aws-samples/sample-genai-on-eks-starter-kit).
