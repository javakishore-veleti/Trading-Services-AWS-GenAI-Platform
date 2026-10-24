# Hands-on Development Plan — GenAI on EKS (Trading-Services-AWS-GenAI-Platform)

Rebuild of the aws-samples "GenAI on EKS starter kit", one stage at a time. Every AWS resource is created only by a manually triggered GitHub Actions workflow (`workflow_dispatch`). Infrastructure is CloudFormation stacks; Kubernetes add-ons are installed with `kubectl`/`helm` steps inside the workflow.

Reference (read-only): the upstream clone at `sample-genai-on-eks-starter-kit/` — use its `components/`, `docs/`, and `terraform/modules/` as source material (rewrite Terraform as CloudFormation).

---

## 1. Ground rules

| # | Rule | Why |
|---|------|-----|
| R1 | One stage = one workflow = one stack (or one script). Stages run strictly in order. | Each stage is understandable and revertible alone. |
| R2 | Every workflow is `workflow_dispatch` only. | You decide when money is spent. |
| R3 | Every workflow has `action: plan | apply` and `confirm: APPLY` for apply. Plan = create a change set and show it. | Review before change. |
| R4 | Every stack is named `genai-eks-NN-<name>`. Concurrency group `genai-eks` on all workflows. | Predictable names; no parallel changes. |
| R5 | Never create or delete the VPC you bring (`VPC_ID` is an input). | Your network survives every teardown. |
| R6 | Secrets only in GitHub Secrets. Nothing secret in git. | Keys in git are leaked keys. |
| R7 | Each stage ends with a verification step and a teardown note. | "Deployed" is not "works". |
| R8 | Commit only when you say so: `commit stage NN`. Message `feat(stage-NN): <title>`. | You control history. |

---

## 2. One-time setup (you do this)

**Ownership:** you do the AWS account items (IAM user, access key, budget, GPU quota, VPC ID) and GitHub secrets, variables, and the `sandbox` environment. The assistant writes the workflows, templates, and scripts; you run them from the Actions tab.

### 2.1 AWS side
1. **Region:** `us-east-1`. Use it everywhere.
2. **CI IAM user:** `Trading-Services-AWS-GenAI-Platform`, access key, policy `Trading-Services-AWS-GenAI-Platform` built from `iam/ci-policy.json`. Extended per stage.
3. **Budget alarm:** monthly budget (e.g. $100) with alerts at 50/80/100%. GPU stages are the expensive ones.
4. **GPU quota:** Service Quotas → Amazon EC2 → "Running On-Demand G and VT instances" ≥ 4 vCPU. Request early; approval can take days. (Current value in this account: 520 vCPUs.)
5. **VPC:** `vpc-5514cf32` (172.30.0.0/16). Has ≥ 2 AZs and public subnets with an internet gateway. It has **no private subnets and no NAT gateway**.

### 2.2 GitHub side
- Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Variables: `AWS_REGION` = `us-east-1`, `VPC_ID` = `vpc-5514cf32`
- Environment `sandbox` with you as required reviewer
- Later: `HF_TOKEN` (Stage 11), `DOMAIN` only if you own a Route 53 zone (Stage 08)

### 2.3 Learning-mode decision
EKS nodes run in the **public subnets** of `vpc-5514cf32`. No NAT gateway, so no hourly cost. Nodes get public IPs — acceptable for a sandbox that is torn down; production needs private subnets with NAT egress.

---

## 3. Conventions

```
.github/workflows/NN-<name>.yml     # one workflow per stage (NN = stage number)
stages/NN-<name>/template.yaml      # CloudFormation template (if the stage creates AWS resources)
stages/NN-<name>/*.sh               # scripts (preflight, tags, kubectl/helm steps)
stages/NN-<name>/README.md          # cost, verify, teardown
```

Standard inputs:
```yaml
on:
  workflow_dispatch:
    inputs:
      action:
        type: choice
        options: [plan, apply]
        default: plan
      confirm:
        description: 'Type APPLY to execute the change set'
        required: false
```

Standard job flow for a CloudFormation stage:
1. checkout → configure AWS credentials → lint (`cfn-lint`)
2. **plan:** `aws cloudformation create-change-set --change-set-type` (CREATE or UPDATE) → `describe-change-set` → print the changes to the job summary → delete the change set
3. **apply** (`environment: sandbox`, only if `confirm = APPLY`): `aws cloudformation deploy --stack-name genai-eks-NN-<name> --template-file stages/NN-<name>/template.yaml --capabilities CAPABILITY_NAMED_IAM --parameter-overrides ... --no-fail-on-empty-changeset`
4. Verify step (the proof command) and job summary (outputs and the teardown command)

Deleting a stage = `aws cloudformation delete-stack` in reverse order (Stage 99 does this).

---

## 4. Stage map

| Stage | Workflow | What it creates | Est. cost while running | Commit |
|---:|---|---|---|---|
| 00 | `00-preflight.yml` | Nothing (read-only) | $0 | `commit stage 00` |
| 02 | `02-vpc-subnet-tags.yml` | Tags on your existing subnets (CLI script, not a stack) | $0 | `commit stage 02` |
| 03 | `03-efs.yml` | Stack: EFS, mount targets, security group | low, per GB | `commit stage 03` |
| 04 | `04-eks-cluster.yml` | Stack: EKS cluster (Auto Mode), cluster and node IAM roles, access entries | ~$0.10/h + nodes | `commit stage 04` |
| 05 | `05-addon-efs-csi.yml` | Stack: Pod Identity role/association; Helm: EFS CSI driver; StorageClass | minor | `commit stage 05` |
| 06 | `06-addon-lb-controller.yml` | Stack: LB controller IAM + Pod Identity; Helm: controller | ALB hourly on use | `commit stage 06` |
| 07 | `07-addon-ingress-nginx.yml` | Helm: ingress-nginx + basic-auth secret (NLB/ALB) | NLB/ALB hourly | `commit stage 07` |
| 08 | `08-addon-external-dns.yml` | Stack: Route 53 role; Helm: external-dns (optional, needs domain) | minor | `commit stage 08` |
| 09 | `09-smoke-app.yml` | kubectl: nginx Deployment, Service, Ingress (ALB) | ALB hourly | `commit stage 09` |
| 10 | `10-gpu-nodepool.yml` | kubectl: Karpenter GPU NodePool + NodeClass → on-demand GPU EC2 | **high** ($/h per GPU) | `commit stage 10` |
| 11 | `11-vllm-model.yml` | kubectl: HF secret, vLLM Deployment + Service on GPU | high | `commit stage 11` |
| 12 | `12-litellm.yml` | kubectl: LiteLLM gateway + key secret | low | `commit stage 12` |
| 13 | `13-openwebui.yml` | kubectl: Open WebUI + Ingress | low | `commit stage 13` |
| 14 | `14-tei-embedding.yml` | kubectl: TEI on CPU | low | `commit stage 14` |
| 15 | `15-qdrant.yml` | kubectl: Qdrant StatefulSet + EBS PVC | low | `commit stage 15` |
| 16 | `16-ecr-and-build.yml` | Stack: ECR repo (immutable tags, scan on push); build job | low | `commit stage 16` |
| 17 | `17-strands-calculator-agent.yml` | kubectl: agent + MCP calculator | low | `commit stage 17` |
| 18 | `18-langfuse.yml` *(optional)* | kubectl/helm: Langfuse + Postgres | low | `commit stage 18` |
| 19 | `19-oidc-role.yml` | Stack: GitHub OIDC provider + deploy role | $0 | `commit stage 19` |
| 99 | `099-aws-destroy-all.yml` | Deletes stacks and Helm releases in reverse order | — | `commit stage 99` |

Stage 01 (Terraform state bucket) was removed: CloudFormation keeps its own state.

---

## 5. Stage details

### Stage 00 — Preflight (read-only)
- **Goal:** prove credentials, VPC, subnets, and GPU quota before anything is created.
- **Build:** `00-preflight.yml` → `stages/00-preflight/preflight.sh`: checks identity, VPC, AZs, public/NAT routes, GPU quota.
- **Verify:** job summary shows PASS/WARN/FAIL per check.
- **Learn:** IAM identity, VPC anatomy, Service Quotas.

### Stage 02 — Tag your existing subnets (not a stack)
- **Goal:** EKS, ALBs and Karpenter find subnets through tags, without recreating the VPC.
- **Build:** a script (`aws ec2 create-tags`) adds `kubernetes.io/role/elb=1` to public subnets and `karpenter.sh/discovery=genai-eks` to the subnets EKS nodes will use (public, in learning mode). CloudFormation cannot tag existing resources without importing them, so this stage stays a CLI script.
- **Verify:** `aws ec2 describe-subnets --filters Name=vpc-id,Values=vpc-5514cf32` shows the tags.
- **Teardown:** the script removes only the tags it added. The VPC stays.

### Stage 03 — EFS (stack)
- **Template:** EFS file system (encrypted), one mount target per subnet, security group allowing TCP 2049 from `172.30.0.0/16`.
- **Verify:** mount targets `available`.
- **Learn:** mount targets, security groups as access control, EFS vs EBS.
- **Teardown:** delete after Stage 05's PVCs are gone (EFS data deletion is irreversible).

### Stage 04 — EKS cluster in Auto Mode (stack)
- **Template:** `AWS::EKS::Cluster` with Auto Mode compute, cluster role, node role, access entry for the CI user, subnets from Stage 02.
- **Verify:** workflow runs `aws eks update-kubeconfig` then `kubectl get nodepools` and `kubectl get nodes`.
- **Learn:** control plane vs data plane, Auto Mode, IAM roles for cluster and nodes, access entries.
- **Teardown:** Stage 99 deletes the stack after all workloads are gone.

### Stage 05 — EFS CSI driver
- **Template:** Pod Identity role and `AWS::EKS::PodIdentityAssociation`.
- **Helm:** `aws-efs-csi-driver`. StorageClass `efs` points at the Stage 03 file system ID (read from stack outputs).
- **Verify:** test PVC `Bound`; data survives a pod restart.
- **Learn:** Pod Identity, CSI, RWX.

### Stage 06 — AWS Load Balancer Controller
- **Template:** controller IAM role + Pod Identity association.
- **Helm:** controller with `clusterName`, `vpcId`, `region`; IngressClass for the shared ALB.
- **Verify:** controller `Available`, no IAM errors in logs.
- **Teardown:** delete Ingresses first — the controller creates the ALBs, and CloudFormation can't remove them.

### Stage 07 — ingress-nginx with basic auth
- **Helm:** ingress-nginx (one `Service type=LoadBalancer`); basic-auth Secret from GitHub Secrets.
- **Verify:** `curl -u user:wrong` → 401; `curl -u user:right` → 404 (no backend yet).
- **Teardown:** `helm uninstall` releases the load balancer.

### Stage 08 — ExternalDNS (optional, needs a Route 53 zone)
- **Template:** role scoped to one hosted zone + Pod Identity.
- **Helm:** `external-dns` with `domainFilters` set to `DOMAIN`.
- **Verify:** test Ingress for `smoke.<DOMAIN>` resolves to the ALB.
- **Skip if** you don't own a domain.

### Stage 09 — Smoke test behind an ALB
- **kubectl:** nginx Deployment, Service, Ingress.
- **Verify:** `curl http://<ALB_DNS>/` returns the body; URL printed in the summary.
- **Teardown:** delete the Ingress first, so the ALB is released.

### Stage 10 — GPU node pool (Karpenter)
- **kubectl:** NodePool + NodeClass for one GPU family (`g6e` to start), on-demand, with taint `nvidia.com/gpu`. Copy the shape from `components/nvidia-platform` / the kit's `eks-auto-mode/eks-addons.tf`.
- **Verify:** a throwaway pod requesting `nvidia.com/gpu: 1` gets a node; deleting it removes the node after consolidation.
- **Teardown:** delete the NodePool; check the EC2 console afterwards.

### Stage 11 — First model: vLLM
- **Secret:** `HF_TOKEN` from GitHub Secrets → Kubernetes Secret.
- **kubectl:** one vLLM Deployment + Service on the GPU pool, cache on the EFS PVC. Start with the smallest model: `components/llm-model/vllm/model-deepseek-r1-qwen3-8b.template.yaml`.
- **Verify:** `GET /v1/models` lists the model; a chat completion returns text.
- **Teardown:** scale to zero, then delete.

### Stage 12 — LiteLLM gateway
- **kubectl:** LiteLLM Deployment + config mapping `vllm/<model>` to the vLLM Service; master key from Secrets.
- **Verify:** request with key → answer; without key → 401.

### Stage 13 — Open WebUI
- **kubectl:** Deployment, `OPENAI_API_BASE_URL` → LiteLLM, admin from Secrets, Ingress via the ALB controller.
- **Verify:** log in and get a streamed reply.

### Stage 14 — Embeddings on CPU (TEI)
- **kubectl:** TEI with `qwen3-embedding-06b-bf16-cpu`.
- **Verify:** `POST /embed` returns a vector.

### Stage 15 — Qdrant
- **kubectl:** StatefulSet + EBS gp3 PVC; API key from Secrets; Ingress behind basic auth.
- **Verify:** create collection, insert and search one vector.

### Stage 16 — ECR and image build
- **Template:** ECR repo (`ImageTagMutability: IMMUTABLE`, scan on push).
- **Build:** `docker buildx` in the workflow, push with the git SHA as tag.
- **Verify:** `aws ecr describe-images` shows the tag and a scan result.

### Stage 17 — Strands calculator agent
- **kubectl:** agent Deployment (image from Stage 16) + MCP calculator server; env `LITELLM_BASE_URL`, `LITELLM_MODEL_NAME`.
- **Verify:** "what is 17 × 23?" triggers a tool call visible in logs.

### Stage 18 — Langfuse (optional)
- **helm:** Langfuse + Postgres; keys wired into LiteLLM callbacks.
- **Verify:** one chat shows a trace with tokens and latency.

### Stage 19 — OIDC instead of access keys
- **Template:** `AWS::IAM::OIDCProvider` for `token.actions.githubusercontent.com` + deploy role trusting only this repo and the `sandbox` environment.
- **Build:** workflows use `role-to-assume` with `permissions: id-token: write`.
- **Verify:** `aws sts get-caller-identity` shows the assumed role; delete the access key afterwards.

---

## 6. Stage 99 — Teardown (reverse order, never the VPC)

`099-aws-destroy-all.yml` (manual, type `DESTROY`, sandbox approval):
1. Delete demo/test Ingresses and LoadBalancer Services; wait until ALBs and NLBs are gone.
2. Delete GPU workloads (Stages 11, 17); Karpenter drains GPU nodes.
3. Delete the GPU NodePool (Stage 10).
4. Helm uninstall in reverse: 15 → 14 → 13 → 12 → 08 → 07 → 06 → 05.
5. Delete stacks in reverse: 16 (ECR) → 04 (EKS) → 03 (EFS). Delete EFS only after PVCs are gone.
6. Remove the subnet tags from Stage 02. The VPC stays.

After teardown, check manually in the console: EC2 instances, load balancers, EFS, EKS clusters, leftover ENIs, and any NAT gateways (you should have none).

---

## 7. Commit protocol

- You say **`commit stage NN`** → I stage only that stage's files and commit with:
  ```
  feat(stage-NN): <title>

  <2–4 bullets: what it creates and how it was verified>

  Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
  ```
- `.env`, kubeconfig files, keys, and tokens are never committed.
- Pushing is a separate explicit step you request.

---

## 8. Progress tracker

| Stage | Status | Notes |
|---|---|---|
| 00 Preflight | written, not run | |
| 02 Subnet tags | ☐ | |
| 03 EFS | ☐ | |
| 04 EKS cluster | ☐ | |
| 05 EFS CSI | ☐ | |
| 06 LB controller | ☐ | |
| 07 ingress-nginx | ☐ | |
| 08 ExternalDNS (optional) | ☐ | |
| 09 Smoke app | ☐ | |
| 10 GPU NodePool | ☐ | |
| 11 vLLM | ☐ | |
| 12 LiteLLM | ☐ | |
| 13 Open WebUI | ☐ | |
| 14 TEI | ☐ | |
| 15 Qdrant | ☐ | |
| 16 ECR + build | ☐ | |
| 17 Strands agent | ☐ | |
| 18 Langfuse (optional) | ☐ | |
| 19 OIDC | ☐ | |
| 99 Teardown | ☐ | |

---

## 9. Decisions

1. **Region** `us-east-1` (you chose it; the kit defaults to `us-west-2`).
2. **Existing VPC** `vpc-5514cf32` is an input; never created or deleted.
3. **CloudFormation** for AWS resources, one stack per stage, named `genai-eks-NN-<name>`. Kubernetes add-ons with Helm/kubectl in workflow steps.
4. **No state bucket.** CloudFormation keeps state; Stage 01 was removed.
5. **Access keys first**, OIDC in Stage 19.
6. **Learning mode:** EKS nodes in public subnets, no NAT gateway.
7. **Smallest model first** (not the kit's 30B demo).
8. **Auto Mode first**, GPU via Karpenter NodePool in Stage 10.
9. **ExternalDNS and Langfuse are optional.**
