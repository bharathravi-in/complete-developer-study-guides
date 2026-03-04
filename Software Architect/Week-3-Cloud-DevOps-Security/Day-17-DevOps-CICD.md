# Day 17: DevOps & CI/CD

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. CI/CD Pipelines
- [ ] Understand CI/CD concepts
- [ ] Know pipeline stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CI/CD Pipeline                                                          │
│                                                                         │
│  Continuous Integration                      Continuous Deployment      │
│  ═══════════════════════════════════════════════════════════════════   │
│                                                                         │
│   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐    │
│   │ Code │──►│Build │──►│ Test │──►│ Scan │──►│Deploy│──►│Monitor│    │
│   │Commit│   │      │   │      │   │      │   │      │   │      │    │
│   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘    │
│      │          │          │          │          │          │         │
│      │          │          │          │          │          │         │
│      ▼          ▼          ▼          ▼          ▼          ▼         │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │                                                              │    │
│   │  Git │ Docker │ Jest │ SonarQube │ Kubernetes │ Datadog     │    │
│   │      │ Build  │ Unit │ Security  │ Helm/ArgoCD│ Prometheus  │    │
│   │      │        │ E2E  │ SAST/DAST │            │             │    │
│   │                                                              │    │
│   └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Feedback Loop                                 │   │
│  │   < 10 min build │ Auto rollback │ Alerts │ Metrics             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Pipeline Stages:**

| Stage | Tools | Purpose |
|-------|-------|---------|
| **Source** | Git, GitHub | Version control |
| **Build** | Docker, npm | Compile and package |
| **Test** | Jest, Cypress, k6 | Verify quality |
| **Security** | Snyk, SonarQube | Vulnerability scan |
| **Deploy** | Helm, ArgoCD | Release to environment |
| **Monitor** | Prometheus, Grafana | Observe behavior |

**GitHub Actions Example:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Test
        run: npm run test:coverage
      
      - name: Build
        run: npm run build
      
      - name: Build Docker image
        run: docker build -t app:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker push registry.example.com/app:${{ github.sha }}
  
  deploy:
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install app ./chart \
            --set image.tag=${{ github.sha }}
```

---

### 2. GitOps
- [ ] Understand GitOps principles
- [ ] Know ArgoCD basics

```
┌─────────────────────────────────────────────────────────────────────────┐
│  GitOps Architecture                                                     │
│                                                                         │
│   Developer                      Git Repository                         │
│  ┌──────────┐                  ┌────────────────────────────────────┐   │
│  │          │  git push        │                                    │   │
│  │  Code    │─────────────────►│  App Repo        Config Repo       │   │
│  │  Change  │                  │  ┌────────┐     ┌────────────┐     │   │
│  │          │                  │  │ src/   │     │ manifests/ │     │   │
│  └──────────┘                  │  │ tests/ │     │ values.yaml│     │   │
│                                │  └────────┘     └────────────┘     │   │
│                                │                        │           │   │
│                                └────────────────────────┼───────────┘   │
│                                                         │               │
│                                                    Pull (GitOps)        │
│                                                         │               │
│   Kubernetes Cluster                                    │               │
│  ┌──────────────────────────────────────────────────────┼───────────┐   │
│  │                                                      ▼           │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │                    ArgoCD / Flux                            │ │   │
│  │  │                                                            │ │   │
│  │  │  Watch Git ──► Detect Changes ──► Sync to Cluster         │ │   │
│  │  │                                                            │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │                               │                                  │   │
│  │                               ▼                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │ Deployment  │  │  Service    │  │  ConfigMap  │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  GitOps Principles:                                                     │
│  • Declarative: Desired state in Git                                   │
│  • Versioned: Full audit trail                                         │
│  • Automated: Continuous reconciliation                                │
│  • Approved: Pull requests for changes                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Blue-Green Deployment
- [ ] Understand blue-green strategy
- [ ] Know implementation

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Blue-Green Deployment                                                   │
│                                                                         │
│  Step 1: Blue (Current) serving traffic                                │
│  ───────────────────────────────────────                               │
│                                                                         │
│   Users ──────► Load Balancer ──────► Blue (v1.0) ✓                   │
│                      │                                                  │
│                      └──────────────► Green (v1.1) [Idle]              │
│                                                                         │
│  Step 2: Deploy new version to Green                                   │
│  ───────────────────────────────────────                               │
│                                                                         │
│   Users ──────► Load Balancer ──────► Blue (v1.0) ✓                   │
│                      │                                                  │
│                      └──────────────► Green (v1.1) [Testing]           │
│                                                                         │
│  Step 3: Switch traffic to Green                                       │
│  ───────────────────────────────────────                               │
│                                                                         │
│   Users ──────► Load Balancer ──────► Blue (v1.0) [Idle]              │
│                      │                                                  │
│                      └──────────────► Green (v1.1) ✓                   │
│                                                                         │
│  Rollback: Switch back to Blue instantly                               │
│                                                                         │
│  Pros: Zero downtime, instant rollback                                 │
│  Cons: Double infrastructure cost                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 4. Canary Deployment
- [ ] Understand canary releases
- [ ] Know traffic splitting

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Canary Deployment                                                       │
│                                                                         │
│  Step 1: Deploy canary with 5% traffic                                 │
│  ───────────────────────────────────────                               │
│                                                                         │
│                     ┌─────── 95% ───────► Stable (v1.0)                │
│   Users ──────► LB ─┤                                                  │
│                     └─────── 5% ────────► Canary (v1.1)                │
│                                                                         │
│  Step 2: Monitor metrics, increase to 25%                              │
│  ───────────────────────────────────────                               │
│                                                                         │
│                     ┌─────── 75% ───────► Stable (v1.0)                │
│   Users ──────► LB ─┤                                                  │
│                     └─────── 25% ───────► Canary (v1.1)                │
│                                                                         │
│  Step 3: Progressive rollout to 100%                                   │
│  ───────────────────────────────────────                               │
│                                                                         │
│                     ┌─────── 0% ────────► Stable (v1.0)                │
│   Users ──────► LB ─┤                                                  │
│                     └────── 100% ───────► Canary (v1.1) ✓              │
│                                                                         │
│  Metrics to Watch:                                                     │
│  • Error rate                                                          │
│  • Latency (p50, p95, p99)                                            │
│  • Business metrics (conversions, engagement)                          │
│                                                                         │
│  Pros: Low risk, gradual rollout                                       │
│  Cons: Complex traffic management, longer rollout                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Kubernetes Canary with Istio:**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - my-app
  http:
  - route:
    - destination:
        host: my-app
        subset: stable
      weight: 95
    - destination:
        host: my-app
        subset: canary
      weight: 5
```

---

## 📘 Deployment Strategies Comparison

| Strategy | Zero Downtime | Rollback Speed | Risk | Cost |
|----------|--------------|----------------|------|------|
| **Recreate** | No | Slow | High | Low |
| **Rolling** | Yes | Medium | Medium | Low |
| **Blue-Green** | Yes | Instant | Low | High |
| **Canary** | Yes | Fast | Low | Medium |
| **A/B Testing** | Yes | Fast | Low | Medium |

---

## 🎯 Practice Task

### Set Up CI/CD Pipeline

**Instructions:**
1. Create a GitHub Actions workflow
2. Include: Build, Test, Security scan, Deploy
3. Implement canary deployment
4. Set up monitoring

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [ ] [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ ] [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

## ✅ Completion Checklist

- [ ] Understand CI/CD pipeline stages
- [ ] Know GitOps principles
- [ ] Can implement blue-green deployment
- [ ] Can implement canary deployment
- [ ] Set up a complete pipeline

**Date Completed:** _____________
