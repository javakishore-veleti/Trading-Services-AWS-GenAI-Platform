# GenAI on EKS — Hands-on Development Plan

A staged, one-workflow-per-stage path to rebuild the
[aws-samples/sample-genai-on-eks-starter-kit](https://github.com/aws-samples/sample-genai-on-eks-starter-kit)
yourself, with AWS resources created **only** by manually triggered GitHub Actions workflows.

Reference clone (read-only for this plan):
`sample-genai-on-eks-starter-kit/` — its `terraform/`, `components/` and `docs/` are the source material.

---

## 1. Ground rules

| # | Rule | Why |
|---|------|-----|
| R1 | **One stage = one workflow file = one concept.** Stages run strictly in order. | Each stage can be understood, verified and reverted alone. |
| R2 | **Every workflow is `workflow_dispatch` only.** No `push` triggers that create AWS resources. | You decide when money is spent. |
| R3 | Every workflow has `action: plan \| apply \| destroy` and a **typed confirmation** for `apply`/`destroy`. | Plan first, always. |
| R4 | Every stage has its own **Terraform state key** in S3 and a shared **concurrency group** `genai-eks`. | No two stages mutate the same state at once. |
| R5 | **Never create or delete the VPC you bring.** The VPC is an input (`VPC_ID`), not an output. | Your existing network must survive every teardown. |
| R6 | Secrets only in **GitHub Secrets**. Nothing secret in git. `.env` stays ignored. | Keys in git are leaked keys. |
| R7 | Each stage ends with a **verification step** (a command that proves it works) and a **teardown note**. | "It applied" is not "it works". |
| R8 | Commit only when you say so: `commit stage NN`. Commit message = `feat(stage-NN): <title>`. | You control the history. |

---

## 2. One-time setup (Stage 00 prerequisites — do these yourself, once)

**Ownership:** you do the AWS account items (IAM user, access key, budget, GPU quota, VPC ID) and the GitHub secrets, variables and `sandbox` environment. The assistant writes the workflows and scripts; you run them from the Actions tab.

### 2.1 AWS side
1. **Account & region.** Region is `us-east-1` (you chose it). Use it everywhere.
2. **IAM user for CI** (`Trading-Services-AWS-GenAI-Platform`). Start with an access key (as you asked); attach a policy scoped to the services in this plan. Upgrade to **GitHub OIDC + an assumable role** later (see Stage 19 hardening).
3. **Budget alarm.** AWS Budgets → monthly cost budget (e.g., $100) with email alerts at 50/80/100 %. GPU stages are the expensive ones.
4. **Service quota check.** Service Quotas → *Amazon EC2* → "Running On-Demand G and VT instances" must be ≥ 4 vCPU for the GPU stage. Request an increase early; approval can take days.
5. **Your VPC.** Note `VPC_ID`. It must have ≥ 2 AZs, private subnets with a route to a NAT gateway (or egress), and at least one public subnet for internet-facing load balancers.

### 2.2 GitHub side
1. Create the repo (private recommended), push this scaffold.
2. **Settings → Secrets and variables → Actions**
   - Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - Variables: `AWS_REGION` (e.g. `us-east-1`), `VPC_ID` (e.g. `vpc-0abc...`), `CLUSTER_NAME` (e.g. `genai-on-eks`)
   - Later secrets: `HF_TOKEN` (Stage 11), `DOMAIN` only if you own a Route 53 zone (Stage 08).
3. **Settings → Environments → New: `sandbox`.** Add yourself as a required reviewer. Each `apply`/`destroy` job uses `environment: sandbox`, so GitHub pauses for your approval.

### 2.3 Local tools (for your own verification only)
AWS CLI v2, Terraform ≥ 1.10 (needed for S3 native locking), kubectl, Helm, Git.

---

## 3. Workflow conventions (apply to every stage)

```
.github/workflows/NN-<name>.yml          # one workflow per stage
stages/NN-<name>/                        # Terraform (or manifests) for that stage
  main.tf | values.yaml | ...
  README.md                              # what it is, cost, verify, teardown
```

Standard inputs for every stage workflow:

```yaml
on:
  workflow_dispatch:
    inputs:
      action:
        type: choice
        options: [plan, apply, destroy]
        default: plan
      confirm:
        description: 'Type APPLY or DESTROY to proceed past plan'
        required: false
```

Standard job skeleton (described, not yet written — you will write each one in its stage):

1. `checkout` → `configure-aws-credentials` (from secrets) → `setup-terraform`
2. `terraform init` with the S3 backend and key `stages/NN-<name>/terraform.tfstate`
3. `terraform plan -out=tfplan` → upload plan as artifact → print summary
4. If `action=apply` and `confirm=APPLY`: job waits on `environment: sandbox` → `terraform apply tfplan`
5. Verify step (the proof command for that stage)
6. Job summary (`$GITHUB_STEP_SUMMARY`) with outputs and the teardown command

---

## 4. Stage map at a glance

| Stage | Phase | Workflow | Creates AWS resources? | Est. cost while running | Commit point |
|------:|-------|----------|:---:|---|---|
| 00 | Foundations | `00-preflight.yml` | No (read-only) | $0 | `commit stage 00` |
| 01 | Foundations | `01-state-backend.yml` | Yes — S3 bucket | ~$0 | `commit stage 01` |
| 02 | Network | `02-vpc-adopt.yml` | Tags only on your VPC | $0 | `commit stage 02` |
| 03 | Storage | `03-efs.yml` | Yes — EFS + mount targets | low, per GB | `commit stage 03` |
| 04 | Control plane | `04-eks-cluster.yml` | Yes — EKS cluster + IAM | ~$0.10/h + nodes | `commit stage 04` |
| 05 | Cluster add-ons | `05-addon-efs-csi.yml` | K8s + IAM | minor | `commit stage 05` |
| 06 | Cluster add-ons | `06-addon-lb-controller.yml` | K8s + IAM + ALB (on use) | ALB hourly | `commit stage 06` |
| 07 | Cluster add-ons | `07-addon-ingress-nginx.yml` | K8s + NLB/ALB | ALB/NLB hourly | `commit stage 07` |
| 08 | Cluster add-ons | `08-addon-external-dns.yml` | Route 53 records (needs domain) | minor | `commit stage 08` |
| 09 | Smoke test | `09-smoke-app.yml` | K8s + ALB | ALB hourly | `commit stage 09` |
| 10 | Compute | `10-gpu-nodepool.yml` | K8s NodePool → EC2 GPU on demand | **high** ($/h per GPU) | `commit stage 10` |
| 11 | LLM serving | `11-vllm-model.yml` | K8s pods on GPU | high (GPU hours) | `commit stage 11` |
| 12 | AI gateway | `12-litellm.yml` | K8s + ALB | low | `commit stage 12` |
| 13 | GUI | `13-openwebui.yml` | K8s + ALB | low | `commit stage 13` |
| 14 | Embeddings | `14-tei-embedding.yml` | K8s (CPU) | low | `commit stage 14` |
| 15 | Vector DB | `15-qdrant.yml` | K8s + EBS | low | `commit stage 15` |
| 16 | Container images | `16-ecr-and-build.yml` | ECR repo + build | low | `commit stage 16` |
| 17 | Agent | `17-strands-calculator-agent.yml` | K8s | low | `commit stage 17` |
| 18 | Observability | `18-langfuse.yml` *(optional)* | K8s + storage | low | `commit stage 18` |
| 19 | Hardening | `19-oidc-role.yml` | IAM OIDC provider + role | $0 | `commit stage 19` |
| 99 | Teardown | `99-teardown.yml` | Destroys in reverse order | — | `commit stage 99` |

> Costs are directional. Check the AWS Pricing Calculator for your region before running GPU stages.

---

## 5. Stage details

Each stage lists: **Goal · Build · Verify · Learn · Teardown**.

### Stage 00 — Preflight (read-only)
- **Goal:** Prove the CI credentials, region and your VPC are usable before anything is created.
- **Build:** `00-preflight.yml` runs `aws sts get-caller-identity`, `aws ec2 describe-vpcs --vpc-ids $VPC_ID`, lists its subnets with AZ and `MapPublicIpOnLaunch`, checks each private subnet's route table for a `0.0.0.0/0` → NAT route, and checks the GPU vCPU service quota.
- **Verify:** Job summary shows account ID, VPC CIDR, ≥ 2 AZs, NAT route present, quota value.
- **Learn:** IAM identity, VPC anatomy (subnets, route tables, NAT), Service Quotas.
- **Teardown:** None (no resources).

### Stage 01 — Terraform remote state
- **Goal:** Persistent, locked state that survives ephemeral GitHub runners.
- **Build:** `01-state-backend.yml` creates an S3 bucket `genai-eks-tfstate-<account>` with versioning, SSE-S3 encryption, public access blocked, and `use_lockfile = true` in every backend block (S3 native locking; no DynamoDB needed on Terraform ≥ 1.10).
- **Verify:** `aws s3api get-bucket-versioning` returns `Enabled`; a dummy `terraform init` against the backend succeeds.
- **Learn:** Why state is remote, what locking prevents, bootstrap-chicken-and-egg.
- **Teardown:** Only in Stage 99, last step, and only after all state is destroyed.

### Stage 02 — Adopt your VPC (tags only)
- **Goal:** Make *your* VPC usable by EKS, ALBs and Karpenter without recreating it.
- **Build:** Terraform uses `data "aws_vpc"` and `data "aws_subnets"` (filtered by `vpc-id`) — **no `module "vpc"`**, unlike the kit's `terraform/vpc.tf`. It then tags subnets:
  - public subnets: `kubernetes.io/role/elb = 1`
  - private subnets: `kubernetes.io/role/internal-elb = 1`, `karpenter.sh/discovery = <CLUSTER_NAME>`
  - Plan shows the tag diffs; apply requires `APPLY` confirmation.
- **Verify:** `aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID` shows the tags.
- **Learn:** Subnet tags are how AWS controllers discover where to place load balancers and nodes. Data sources vs. managed resources (you do not own what you did not create).
- **Teardown:** Remove only the tags this stage added (`destroy` action). Never delete the VPC.

### Stage 03 — EFS shared storage
- **Goal:** One ReadWriteMany filesystem for model caches.
- **Build:** EFS file system (encrypted), one mount target per private subnet, security group allowing TCP 2049 from the VPC CIDR only.
- **Verify:** `aws efs describe-mount-targets` → all `LifeCycleState = available`. Output `EFS_FILE_SYSTEM_ID` to the job summary.
- **Learn:** Mount targets live in subnets; SG rules are the access control; why EFS (shared) vs EBS (single-node).
- **Teardown:** `destroy` after Stage 05 and any PVC using it is gone (EFS deletion with data is irreversible).

### Stage 04 — EKS control plane (Auto Mode first)
- **Goal:** A running EKS cluster in your VPC.
- **Build:** Copy the kit's `terraform/modules/eks-auto-mode/` into `stages/04-eks-cluster/`, keep its MIT notice, and call it with **your subnet IDs** from Stage 02 (the kit feeds `module.vpc.private_subnets`; you feed the data source). Start with the **default node pool only** — GPU comes in Stage 10.
- **Verify:** Workflow runs `aws eks update-kubeconfig` and `kubectl get nodes` (Auto Mode nodes appear on demand; `kubectl get nodepools` shows `general-purpose`). Upload kubeconfig as a short-lived artifact only if you need it locally — prefer re-running `update-kubeconfig`.
- **Learn:** Control plane vs data plane, Auto Mode vs self-managed node groups, cluster IAM role and node IAM role, access entries (who can `kubectl`).
- **Teardown:** Stage 99 destroys it after every workload above it.

### Stage 05 — Add-on: EFS CSI driver
- **Goal:** Pods can mount EFS.
- **Build:** IAM role for the EFS CSI driver bound with **EKS Pod Identity** (`aws_eks_pod_identity_association`), Helm install of `aws-efs-csi-driver`, a `StorageClass efs` pointing at the Stage 03 filesystem ID.
- **Verify:** A test PVC with `storageClassName: efs` reaches `Bound`; a pod writes a file and it persists across pod restarts.
- **Learn:** Pod Identity vs IRSA, CSI concepts (StorageClass, PVC, PV), RWX.
- **Teardown:** Delete test PVC, then `destroy`.

### Stage 06 — Add-on: AWS Load Balancer Controller
- **Goal:** Kubernetes `Ingress` creates ALBs.
- **Build:** IAM policy + Pod Identity, Helm `aws-load-balancer-controller` with `clusterName`, `vpcId` (your `VPC_ID`) and `region`. Create an `IngressClass` for the shared internet-facing ALB.
- **Verify:** Controller deployment `Available`; logs show no IAM errors. Full proof comes in Stage 09.
- **Learn:** Ingress → ALB mapping, annotations, why `vpcId` must be passed explicitly.
- **Teardown:** Remove Ingresses first (ALBs are created by the controller; Terraform cannot clean them up if the controller is gone).

### Stage 07 — Add-on: ingress-nginx (basic auth gateway)
- **Goal:** In-cluster HTTP Basic auth for admin UIs (Qdrant, Milvus, dashboards), like the kit's `enable_nginx`.
- **Build:** Helm `ingress-nginx`, one `Service type=LoadBalancer`, a basic-auth `Secret` (credentials from GitHub Secrets, never in git).
- **Verify:** `curl -u user:wrong` → 401; `curl -u user:right` → 404 (no backend yet), proving auth works.
- **Learn:** Ingress controllers vs ALB controller, annotation-based auth, secret handling in CI.
- **Teardown:** Helm uninstall, then Service LB is released.

### Stage 08 — Add-on: ExternalDNS *(optional — requires a Route 53 hosted zone)*
- **Goal:** Ingress hostnames become DNS records automatically.
- **Build:** IAM role scoped to one hosted-zone ARN, Pod Identity, Helm `external-dns` with `domainFilters` set to your `DOMAIN`.
- **Verify:** Create a test Ingress for `smoke.<DOMAIN>` → `dig` returns the ALB.
- **Learn:** Declarative DNS, least-privilege zone scoping.
- **Skip if:** you do not own a domain. Use HTTP per-service ALBs instead and continue.

### Stage 09 — Smoke test: a plain web app behind an ALB
- **Goal:** End-to-end proof that network → cluster → ALB → pod works before adding GPUs.
- **Build:** `09-smoke-app.yml` deploys `nginx` (or `hashicorp/http-echo`) with a Deployment, Service and Ingress.
- **Verify:** `curl http://<ALB_DNS>/` returns the expected body. Job summary prints the URL.
- **Learn:** Deployment → ReplicaSet → Pod, Service vs Ingress, health checks.
- **Teardown:** `kubectl delete -f` (workflow `destroy` action) — **delete the Ingress first** so the ALB is released.

### Stage 10 — GPU node pool
- **Goal:** GPU nodes on demand.
- **Build:** A Karpenter `NodePool` + `NodeClass` for GPU instances (`g6e`, `g6`, `g5` to start — copy the kit's `karpenter_nodepool_gpu` shape from `modules/eks-auto-mode/eks-addons.tf`), restricted to **one** family and **on-demand** capacity while you learn. Add a taint `nvidia.com/gpu` so only GPU pods land there.
- **Verify:** Apply a throwaway pod requesting `nvidia.com/gpu: 1`; `kubectl get nodeclaims` shows a node created; `kubectl describe node` shows the GPU; delete the pod and the node disappears after consolidation.
- **Learn:** Node autoscaling, taints/tolerations, GPU resource requests, consolidation cost behaviour.
- **Teardown:** Delete the NodePool → Karpenter terminates nodes. **Check EC2 console** afterwards.

### Stage 11 — First model: vLLM serving
- **Goal:** An OpenAI-compatible LLM endpoint inside your cluster.
- **Build:** `HF_TOKEN` (GitHub Secret) → Kubernetes Secret. Deploy one vLLM `Deployment` + `Service` on the GPU pool, model cache on the Stage 05 EFS PVC. **Start with the smallest model you can afford**, not the kit's 30B default. Compare `components/llm-model/vllm/model-*.template.yaml` and pick one; the `deepseek-r1-qwen3-8b` template is a smaller starting point.
- **Verify:** Port-forward or in-cluster `curl` → `GET /v1/models` lists the model; `POST /v1/chat/completions` returns text.
- **Learn:** Model download and caching, GPU memory vs model size, OpenAI-compatible API, readiness probes that wait for model load (this takes minutes).
- **Teardown:** Scale to zero first (stops GPU billing via Stage 10 consolidation), then delete.

### Stage 12 — LiteLLM AI gateway
- **Goal:** One API surface and key management in front of vLLM (and later Bedrock).
- **Build:** LiteLLM deployment + config mapping `vllm/<model>` to the vLLM Service; master key from GitHub Secrets.
- **Verify:** `curl` the gateway with the key → same answer as Stage 11; without key → 401.
- **Learn:** Gateway pattern, virtual keys, routing config.
- **Teardown:** Helm/kubectl delete.

### Stage 13 — Open WebUI (chat UI)
- **Goal:** A browser chat interface wired to LiteLLM.
- **Build:** Open WebUI deployment, `OPENAI_API_BASE_URL` → LiteLLM, admin account from Secrets, Ingress via the Stage 06 controller.
- **Verify:** Log in, send a message, get a streamed reply.
- **Learn:** Frontend/back-end split, env-based configuration, persistent volume for the UI DB.

### Stage 14 — Embeddings on CPU (TEI)
- **Goal:** A text-embedding endpoint that does not need a GPU.
- **Build:** Text Embeddings Inference on CPU with the smallest embedding model (`qwen3-embedding-06b-bf16-cpu` template in the kit).
- **Verify:** `POST /embed` returns a vector of the expected dimension.
- **Learn:** Embeddings, CPU vs GPU trade-off, model-specific dimensions.

### Stage 15 — Vector database (Qdrant)
- **Goal:** Store and search embeddings.
- **Build:** Qdrant StatefulSet with an EBS `gp3` PVC (single-node); API key from Secrets; Ingress behind basic auth (Stage 07).
- **Verify:** Create a collection, insert one vector from Stage 14, search and get it back.
- **Learn:** StatefulSets, stable identity, EBS vs EFS for databases.

### Stage 16 — Container images with ECR
- **Goal:** Build your own images in CI instead of pulling only upstream ones.
- **Build:** `16-ecr-and-build.yml`: create an ECR repo (`immutable` tags, scan on push), then a `docker buildx` job that builds from a `Dockerfile` in `stages/16-*/` and pushes with the git SHA as tag.
- **Verify:** `aws ecr describe-images` shows the SHA tag and a scan result.
- **Learn:** Image tagging, immutability, scanning, why not `:latest`.

### Stage 17 — First agent: Strands calculator agent
- **Goal:** An agent that calls tools (MCP) and the LLM through LiteLLM.
- **Build:** Use Stage 16 to build the agent image; deploy with env `LITELLM_BASE_URL`, `LITELLM_MODEL_NAME`; add a small MCP calculator server as a second Deployment.
- **Verify:** Ask it "what is 17 × 23?" and confirm the tool call in logs.
- **Learn:** Agent loop, tool calling, MCP, how agents depend on gateway + model.

### Stage 18 — Observability (optional): Langfuse
- **Goal:** Trace every LLM call.
- **Build:** Langfuse + Postgres (or use the kit's chart), keys into LiteLLM callbacks.
- **Verify:** One chat in Stage 13 shows a trace with tokens and latency.
- **Learn:** Traces, spans, token accounting.

### Stage 19 — Hardening: OIDC instead of access keys
- **Goal:** Remove long-lived AWS keys from GitHub.
- **Build:** IAM OIDC identity provider for `token.actions.githubusercontent.com`; a role trusting only your repo + `sandbox` environment; switch every workflow to `role-to-assume` with `permissions: id-token: write`; delete the access key.
- **Verify:** A workflow run assumes the role (`sts get-caller-identity` shows the assumed-role ARN) with no secret keys in use.
- **Learn:** OIDC federation, trust policy conditions, rotating/deleting keys.
- **Do this before** you leave the sandbox running for long.

---

## 6. Stage 99 — Teardown (reverse order, never the VPC)

`99-teardown.yml` (manual, `destroy`, typed `DESTROY`) runs jobs in this order:

1. Delete test/demo Ingresses and Services of type LoadBalancer → waits until ALBs/NLBs are gone.
2. Delete Deployments using GPUs (Stages 11, 17) → Karpenter drains GPU nodes.
3. Delete the GPU NodePool (Stage 10).
4. Delete add-ons in reverse: 15 → 14 → 13 → 12 → 08 → 07 → 06 → 05.
5. Delete EFS (Stage 03) — **only after PVCs are released**.
6. Destroy EKS (Stage 04).
7. Remove subnet tags added in Stage 02 (your VPC stays).
8. Delete ECR repo (Stage 16) if you want zero cost.
9. Empty and delete the state bucket (Stage 01) **last**, and only when you are done with the whole course.

After teardown, verify manually: EC2 instances, Load Balancers, EFS, EKS clusters, NAT gateways (if you created any — you should not have, since the VPC is yours), Elastic IPs.

---

## 7. Commit protocol

- Work happens on `main` in your own repo (or a branch per stage if you prefer PRs).
- You say: **`commit stage NN`** → I stage only that stage's files plus its workflow, run a quick local lint (`terraform fmt -check`, `actionlint` if available), and commit with:
  ```
  feat(stage-NN): <title>

  <2–4 bullet summary of what it creates and how it was verified>

  Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
  ```
- `.env`, `*.tfstate*`, `.terraform/`, `tfplan`, kubeconfig files are ignored by `.gitignore` and must never be committed.
- Pushing to GitHub is a separate explicit step you request.

---

## 8. Progress tracker

| Stage | Status | Verified on | Notes |
|---|---|---|---|
| 00 Preflight | ☐ | | |
| 01 State backend | ☐ | | |
| 02 VPC adopt | ☐ | | |
| 03 EFS | ☐ | | |
| 04 EKS cluster | ☐ | | |
| 05 EFS CSI | ☐ | | |
| 06 LB controller | ☐ | | |
| 07 ingress-nginx | ☐ | | |
| 08 ExternalDNS (optional) | ☐ | | |
| 09 Smoke app | ☐ | | |
| 10 GPU NodePool | ☐ | | |
| 11 vLLM | ☐ | | |
| 12 LiteLLM | ☐ | | |
| 13 Open WebUI | ☐ | | |
| 14 TEI embeddings | ☐ | | |
| 15 Qdrant | ☐ | | |
| 16 ECR + build | ☐ | | |
| 17 Strands agent | ☐ | | |
| 18 Langfuse (optional) | ☐ | | |
| 19 OIDC hardening | ☐ | | |
| 99 Teardown | ☐ | | |

---

## 9. Decisions made in this plan (change any of them)

1. **Region** `us-east-1` (chosen by you; the kit defaults to `us-west-2`).
2. **Existing VPC** is a data-source input; the kit's `vpc.tf` (which creates a new VPC) is deliberately not used.
3. **Remote state in S3** with native locking, one state key per stage.
4. **Access keys first**, OIDC last (Stage 19), as you asked.
5. **Smallest model first**, not the kit's 30B demo models, to control GPU cost.
6. **Auto Mode first**, GPU via Karpenter NodePool in Stage 10.
7. **ExternalDNS and Langfuse are optional** — they need a domain / extra cost.
