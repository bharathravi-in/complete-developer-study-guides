# Day 16: GitHub Actions – Complete CI/CD Guide

## 📚 Topics to Cover (3-4 hours)

---

## 1. GitHub Actions Concepts

```
Repository
└── .github/
    └── workflows/
        ├── ci.yml        ← Runs on every push/PR
        ├── deploy.yml    ← Runs on release
        └── cron.yml      ← Scheduled tasks
```

| Concept | Description |
|---------|-------------|
| **Workflow** | Automated process defined in YAML |
| **Event** | Trigger (push, PR, schedule, manual) |
| **Job** | Set of steps running on same runner |
| **Step** | Individual task (run command or action) |
| **Action** | Reusable unit of code |
| **Runner** | Machine that executes jobs |
| **Artifact** | Files produced by jobs |
| **Secret** | Encrypted environment variables |

---

## 2. Complete CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Cancel in-progress runs for same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage --ci
      - name: Upload coverage
        if: matrix.node-version == 20
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  e2e:
    runs-on: ubuntu-latest
    needs: test
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run e2e
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7

  build:
    runs-on: ubuntu-latest
    needs: [test, e2e]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment: production
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # kubectl set image deployment/web web=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
```

---

## 3. Python CI Pipeline

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - run: |
          ruff check .
          ruff format --check .
      - run: pytest --cov=src --cov-report=xml -v
      - uses: codecov/codecov-action@v3
        if: matrix.python-version == '3.12'
```

---

## 4. Reusable Workflows

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      KUBE_CONFIG:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      - run: |
          kubectl set image deployment/web web=myimage:${{ inputs.image-tag }}
          kubectl rollout status deployment/web

# Calling workflow
name: Deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]

jobs:
  deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: ${{ inputs.environment }}
      image-tag: ${{ github.sha }}
    secrets:
      KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
```

---

## 5. Deployment Strategies

### Blue-Green

```yaml
deploy-blue-green:
  steps:
    - name: Deploy to green
      run: kubectl apply -f k8s/green-deployment.yaml
    - name: Wait for green ready
      run: kubectl rollout status deployment/web-green
    - name: Run smoke tests
      run: npm run smoke-test -- --url=$GREEN_URL
    - name: Switch traffic
      run: |
        kubectl patch service web -p '{"spec":{"selector":{"version":"green"}}}'
    - name: Remove old blue
      run: kubectl delete deployment web-blue
```

### Canary

```yaml
deploy-canary:
  steps:
    - name: Deploy canary (10% traffic)
      run: |
        kubectl apply -f k8s/canary-deployment.yaml
        kubectl scale deployment web-canary --replicas=1
        # Total: 9 stable + 1 canary = 10% traffic
    - name: Monitor canary (5 min)
      run: |
        sleep 300
        ERROR_RATE=$(curl -s prometheus/api/v1/query?query=rate(http_errors[5m]))
        if [ "$ERROR_RATE" -gt "0.01" ]; then
          kubectl delete deployment web-canary
          exit 1
        fi
    - name: Promote canary
      run: |
        kubectl set image deployment/web-stable web=myapp:$NEW_VERSION
        kubectl delete deployment web-canary
```

---

## 6. Secrets & Environment Management

```yaml
# Using secrets
steps:
  - name: Deploy
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
      API_KEY: ${{ secrets.API_KEY }}
    run: ./deploy.sh

# Using environments (with approval)
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://myapp.com
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production"

# Secrets from external managers
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-arn: ${{ secrets.AWS_ROLE_ARN }}
  - name: Get secrets from AWS
    run: |
      SECRET=$(aws secretsmanager get-secret-value --secret-id myapp/prod)
```

---

## 🎯 Interview Questions

### Q1: How do you handle secrets in GitHub Actions?
**A:** Use GitHub Secrets (encrypted, not logged). For advanced: use OIDC tokens with cloud providers (no long-lived credentials), Environment secrets with approval gates, external secret managers (AWS Secrets Manager, Vault).

### Q2: Explain Blue-Green vs Canary deployments
**A:** **Blue-Green**: Two identical environments, switch traffic all at once. Fast rollback (switch back). Higher cost (double resources). **Canary**: Gradually shift traffic (1% → 10% → 100%). Lower risk, metrics-based promotion. More complex to implement.

### Q3: How do you optimize CI pipeline speed?
**A:** Caching (npm, pip, Docker layers), parallel jobs, matrix strategies, skip unnecessary jobs (`paths` filter), incremental builds, self-hosted runners for heavy workloads, concurrency groups to cancel stale runs.

---

## 📝 Practice Exercises

1. Create a CI pipeline that builds, tests, and deploys a Node.js app
2. Set up matrix testing across multiple Node/Python versions
3. Implement a reusable workflow for deployment
4. Create a canary deployment pipeline with health checks
