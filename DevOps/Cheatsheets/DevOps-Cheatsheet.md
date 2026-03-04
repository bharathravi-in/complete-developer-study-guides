# DevOps Cheatsheets

## Docker Cheatsheet

```bash
# Images
docker build -t name:tag .
docker pull image:tag
docker push image:tag
docker images
docker rmi image
docker image prune -a

# Containers
docker run -d -p 8080:80 --name web image
docker run -it --rm image bash
docker ps / docker ps -a
docker stop/start/restart container
docker rm container
docker logs -f container
docker exec -it container bash
docker inspect container
docker stats

# Compose
docker compose up -d
docker compose down [-v]
docker compose logs -f service
docker compose exec service sh
docker compose build
docker compose ps

# System
docker system prune -a
docker system df
docker network ls/create/inspect
docker volume ls/create/inspect
```

## Kubernetes Cheatsheet

```bash
# Cluster
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# Resources
kubectl apply -f file.yaml
kubectl delete -f file.yaml
kubectl get pods/deployments/services
kubectl describe pod/deployment/service name

# Pods
kubectl logs pod [-f] [-c container]
kubectl exec -it pod -- /bin/sh
kubectl port-forward pod 8080:3000
kubectl top pods

# Deployments
kubectl rollout status deployment/name
kubectl rollout history deployment/name
kubectl rollout undo deployment/name
kubectl scale deployment name --replicas=5

# Config
kubectl create configmap name --from-file=config.yaml
kubectl create secret generic name --from-literal=key=value
kubectl get secret name -o jsonpath='{.data.key}' | base64 -d

# Debug
kubectl get events --sort-by='.metadata.creationTimestamp'
kubectl describe pod name  # Check Events section
kubectl logs pod --previous  # Previous container logs
```

## Terraform Cheatsheet

```bash
terraform init          # Initialize
terraform plan          # Preview changes
terraform apply         # Apply changes
terraform destroy       # Destroy all
terraform fmt           # Format code
terraform validate      # Check syntax
terraform output        # Show outputs
terraform state list    # List resources
terraform import resource id  # Import existing
terraform workspace new/select name
```

## GitHub Actions Cheatsheet

```yaml
# Triggers
on: [push, pull_request]
on:
  push:
    branches: [main]
    paths: ['src/**']
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

# Common actions
uses: actions/checkout@v4
uses: actions/setup-node@v4
uses: actions/setup-python@v5
uses: actions/cache@v4
uses: actions/upload-artifact@v4
uses: docker/build-push-action@v5

# Matrix
strategy:
  matrix:
    node: [18, 20, 22]
    os: [ubuntu-latest, windows-latest]

# Secrets & Env
env:
  MY_VAR: ${{ secrets.MY_SECRET }}
  REF: ${{ github.ref }}

# Conditions
if: github.event_name == 'push'
if: success() || failure()
if: contains(github.event.head_commit.message, '[skip ci]') == false
```
