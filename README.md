# Trading-Services-AWS-GenAI-Platform

Hands-on build of a GenAI platform on Amazon EKS, one manually triggered GitHub Actions workflow per stage.

- **Plan:** [PLAN.md](PLAN.md)
- **Workflows:** `.github/workflows/NN-<name>.yml` (workflow_dispatch only)
- **Stage code:** `stages/NN-<name>/`
- **CI IAM policy starter:** `iam/ci-policy.json`

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
