# CLAUDE.md — Trading-Services-AWS-GenAI-Platform

## What this repo is
A hands-on rebuild of the aws-samples "GenAI on EKS starter kit" on AWS, one stage at a time.
Every AWS resource is created **only** by a manually triggered GitHub Actions workflow
(`workflow_dispatch`). The full plan, stage list, and teardown order are in `PLAN.md`. Read it first.

Reference (read-only, do not modify): the upstream clone at
`/Users/vavkkishore/kishore/runtime_data/temp_gh_repos/AWS_News_Projects/2026/sample-genai-on-eks-starter-kit`
Use its `terraform/`, `components/`, and `docs/` as source material when building a stage.

## Fixed decisions
- **Region:** `us-east-1`. Use it everywhere. Never hard-code another region.
- **Existing VPC:** the VPC ID comes from the GitHub variable `VPC_ID`. Never create or delete a VPC.
  The kit's `terraform/vpc.tf` creates a new VPC, so do not copy it. Reference the VPC by ID.
- **Infrastructure:** CloudFormation. One stack per stage, named `genai-eks-NN-<name>`, template at
  `stages/NN-<name>/template.yaml`. CloudFormation keeps its own state, so there is no state bucket.
  Kubernetes add-ons use `kubectl`/`helm` steps in the workflow, not stacks.
  Stage 02 (subnet tags) is a CLI script because CloudFormation can't tag existing subnets.
- **Credentials:** long-lived access keys in GitHub Secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
  until Stage 19 switches to OIDC. No key is ever written to a file in this repo.
- **Concurrency:** every workflow uses `concurrency: group: genai-eks`, `cancel-in-progress: false`.

## Workflow conventions
- File name: `.github/workflows/NN-<name>.yml`. Title: `"NN - <Title>"`.
- Trigger: `workflow_dispatch` only. Never add `push` or `schedule` triggers that touch AWS.
- Inputs: `action` (`plan` | `apply`, default `plan`) and `confirm` (must equal `APPLY`).
  `plan` creates a change set and prints it; `apply` executes it via `aws cloudformation deploy`.
  The `apply` job must use `environment: sandbox` and run only when `action == 'apply'`.
- Logic lives in `stages/NN-<name>/` as CloudFormation templates and scripts. Keep the YAML thin.
- Every script takes its inputs from env vars and fails loudly if one is missing (`: "${VAR:?...}"`).
- Every stage writes a human-readable summary to `$GITHUB_STEP_SUMMARY`.
- Every stage ends with a verification step that proves the result, not just "apply succeeded".
- Every stage README (or PLAN.md section) states: cost, verify command, teardown order.

## Git rules
- **Do not commit or push unless the user says so.** The trigger is the user's words, e.g. `commit stage 02`.
- Commit message format:
  ```
  feat(stage-NN): <title>

  <2–4 bullets: what it creates, how it was verified>

  Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
  ```
- Never commit: `.env*`, `*.tfstate*`, `.terraform/`, `tfplan`, kubeconfig files, keys, tokens.
- Pushing to GitHub is a separate, explicit request.

## Safety rules
- Never run `terraform apply`, `aws` mutations, or `kubectl apply` on the user's AWS account from
  the local shell. All AWS changes go through the GitHub workflow. Local `aws` calls are read-only
  and only for diagnosis, with the user's approval.
- Destroying anything (Stage 99 or any delete) requires the user to ask for it explicitly.
- Before changing an existing subnet, route table, or tag on the user's VPC, show the plan.
- Costs: GPU stages (10, 11) and the EKS control plane are the expensive ones. Say so before running them.

## Working style for this repo
- Build one stage at a time, in order. Do not start stage N+1 until the user has verified stage N.
- Keep changes scoped to the current stage. Do not refactor earlier stages without asking.
- When a stage is written, list what the user must do next in GitHub (secrets, variables, approvals).
- Be concise in summaries. Put detail in `PLAN.md` or the stage README, not in chat.

## Current status
- Stage 00 (preflight, read-only): written, not yet run.
- Stage 01 was removed (CloudFormation replaces the state bucket).
- Stage 02 onward: not started. Each one is written after the previous stage is verified.
- Teardown: `099-aws-destroy-all.yml` has only a placeholder until stacks exist.
- User-owned prerequisites: IAM user `Trading-Services-AWS-GenAI-Platform` with policy `Trading-Services-AWS-GenAI-Platform` (from `iam/ci-policy.json`), GitHub secrets and
  variables, `sandbox` environment, budget alarm, GPU vCPU quota request, and the VPC ID.
