# DevOps Interview Questions – Comprehensive Q&A

## 📚 50+ Interview Questions for Senior Engineers

---

## Docker

### Q1: What are namespaces and cgroups?
**A:** **Namespaces** provide isolation: PID, NET, MNT, UTS, IPC, USER. Each container gets its own view of the system. **Cgroups** limit resources: CPU, memory, I/O. Together they create lightweight isolated environments without the overhead of VMs.

### Q2: Docker image layers — how do they work?
**A:** Each Dockerfile instruction creates a read-only layer. Layers are cached (content-addressable). A container adds a writable layer on top. Layers are shared between images (deduplication). Order Dockerfile from least to most frequently changing for optimal caching.

### Q3: Multi-stage builds — when and why?
**A:** Use multiple FROM statements: builder stage has build tools, production stage only has runtime + artifacts. Benefits: 80%+ size reduction, no build tools in prod image, better security. Example: Build Angular/React, then copy dist/ to nginx:alpine.

### Q4: Docker networking modes?
**A:** **Bridge** (default): Isolated network with DNS resolution. **Host**: Container uses host's network (no isolation, max performance). **Overlay**: Multi-host networking (Swarm). **None**: No networking. **Macvlan**: Container gets its own MAC address on LAN.

### Q5: How to handle persistent data in Docker?
**A:** **Volumes**: Docker-managed, best for production (`docker volume create`). **Bind mounts**: Host directory mapped into container (development). **tmpfs**: In-memory, no persistence (sensitive data). Never store data in container's writable layer.

---

## Kubernetes

### Q6: Explain K8s architecture
**A:** **Control Plane**: API Server (gateway), etcd (state store), Scheduler (pod placement), Controller Manager (desired state). **Worker Nodes**: kubelet (pod lifecycle), kube-proxy (networking), container runtime. All communication through API Server.

### Q7: Pod vs Deployment vs StatefulSet
**A:** **Pod**: Smallest unit, ephemeral. **Deployment**: Manages stateless pods via ReplicaSets, handles rolling updates. **StatefulSet**: For stateful apps (databases), provides stable network identity, ordered deployment, persistent storage per pod.

### Q8: Service types in K8s?
**A:** **ClusterIP**: Internal only (default). **NodePort**: Expose on each node's IP (30000-32767). **LoadBalancer**: Cloud provider LB. **ExternalName**: DNS CNAME alias. **Ingress** (not a Service): HTTP routing with host/path rules, TLS termination.

### Q9: How does K8s handle rolling updates?
**A:** Creates new ReplicaSet, gradually scales up new pods while scaling down old. `maxSurge` (extra pods allowed) and `maxUnavailable` (pods that can be down). Health checks gate progression. `kubectl rollout undo` reverts instantly.

### Q10: Liveness vs Readiness vs Startup probes?
**A:** **Liveness**: "Is it alive?" Failure → restart container. **Readiness**: "Can it serve traffic?" Failure → remove from service endpoints. **Startup**: "Has it started?" Disables other probes during startup. Used for slow-starting apps.

### Q11: How do you debug a CrashLoopBackOff?
**A:** (1) `kubectl logs pod-name --previous` for crash logs. (2) `kubectl describe pod` for events. (3) Check resource limits (OOMKilled). (4) Verify image and command. (5) Check liveness probe configuration. (6) `kubectl exec` for interactive debugging.

### Q12: Helm charts — what and why?
**A:** Package manager for K8s. Bundles multiple YAML manifests into reusable, templated packages. Features: version control, parameterization via values.yaml, dependency management, rollback capability. Think of it as npm for Kubernetes.

---

## CI/CD

### Q13: Explain CI/CD pipeline stages
**A:** **CI**: Source → Build → Lint → Unit Test → Integration Test → Security Scan → Artifact. **CD**: Artifact → Deploy to staging → E2E Tests → Approval → Deploy to production → Smoke Tests → Monitor.

### Q14: Blue-Green vs Canary vs Rolling deployment?
**A:** **Blue-Green**: Two full environments, instant switch, fast rollback, double cost. **Canary**: Gradual traffic shift (1%→10%→100%), metrics-based promotion, lower risk. **Rolling**: Replace pods one-by-one, no extra infrastructure, slower rollback.

### Q15: How to handle database migrations in CI/CD?
**A:** Run migrations as a separate job before deployment. Use forward-compatible migrations (add columns, don't remove). Two-phase: first deploy code that handles both schemas, then migrate, then deploy code using new schema only. Never break backward compatibility.

### Q16: How to handle secrets in CI/CD?
**A:** Never in code or logs. Use: Platform secrets (GitHub Secrets, GitLab Variables), external managers (Vault, AWS Secrets Manager), OIDC for cloud auth (no long-lived keys), environment-specific secrets with approval gates.

---

## Terraform / IaC

### Q17: What is Terraform state?
**A:** JSON file mapping config to real resources. Contains IDs, attributes, metadata, dependencies. Remote backends (S3, GCS) for team access. State locking (DynamoDB) prevents concurrent writes. `terraform state` commands for management.

### Q18: How to manage multiple environments?
**A:** (1) Workspaces: Simple but limited. (2) Directory per env: Most common, with shared modules. (3) Terragrunt: DRY wrapper. Best practice: shared modules + environment-specific variable files + remote state per env.

### Q19: How to handle drift?
**A:** Drift = real infrastructure differs from state. Detect: `terraform plan` shows unexpected changes. Fix: `terraform apply` to reconcile, or `terraform import` for new resources. Prevent: only modify infrastructure through Terraform, use CI/CD.

### Q20: Terraform vs CloudFormation vs Pulumi?
**A:** **Terraform**: Multi-cloud, HCL, huge ecosystem, state management needed. **CloudFormation**: AWS-only, YAML/JSON, no state file (AWS manages), tightly integrated. **Pulumi**: Real programming languages (TypeScript, Python), multi-cloud, steeper learning curve.

---

## DevOps Culture & Practices

### Q21: What does "shift left" mean?
**A:** Move testing, security, and quality checks earlier in the pipeline. Instead of catching bugs in production, catch them in development. Examples: linting in IDE, pre-commit hooks, security scanning in CI, infrastructure testing.

### Q22: GitOps principles?
**A:** (1) Declarative config in Git (single source of truth). (2) Git as the only way to change systems. (3) Automated reconciliation (ArgoCD, Flux). (4) Software agents ensure cluster matches Git state. Benefits: audit trail, rollback via git revert.

### Q23: How do you implement zero-downtime deployments?
**A:** Rolling updates with health checks, blue-green deployments, canary releases. Prerequisites: graceful shutdown handling, database backward compatibility, proper health check endpoints, load balancer configuration, connection draining.

### Q24: Monitoring vs Observability?
**A:** **Monitoring**: Known-unknowns, predefined metrics and alerts. **Observability**: Unknown-unknowns, ability to understand system from outputs. Three pillars: Metrics (Prometheus), Logs (ELK), Traces (Jaeger). Observability helps debug novel issues.
