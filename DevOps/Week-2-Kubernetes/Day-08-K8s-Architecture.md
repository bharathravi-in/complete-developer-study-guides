# Day 8: Kubernetes Architecture & Fundamentals

## 📚 Topics to Cover (3-4 hours)

---

## 1. Why Kubernetes?

Docker: "How do I run a container?"  
Kubernetes: "How do I run 1000 containers reliably?"

### Problems K8s Solves
- **Service Discovery**: How do containers find each other?
- **Load Balancing**: How to distribute traffic?
- **Auto-scaling**: How to handle traffic spikes?
- **Self-healing**: What if a container crashes?
- **Rolling Updates**: How to deploy without downtime?
- **Secret Management**: How to handle config/secrets?
- **Storage**: How to persist data?

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Control Plane                       │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ API Server   │  │ etcd     │  │ Scheduler     │  │
│  │ (kube-api)   │  │ (store)  │  │               │  │
│  └──────────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────────────────┐  ┌──────────────────────┐  │
│  │ Controller Manager    │  │ Cloud Controller     │  │
│  └──────────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────┘
              │                    │
    ┌─────────▼─────────┐  ┌──────▼──────────┐
    │    Worker Node 1   │  │  Worker Node 2   │
    │  ┌──────────────┐  │  │  ┌──────────────┐│
    │  │   kubelet    │  │  │  │   kubelet    ││
    │  ├──────────────┤  │  │  ├──────────────┤│
    │  │  kube-proxy  │  │  │  │  kube-proxy  ││
    │  ├──────────────┤  │  │  ├──────────────┤│
    │  │ Container    │  │  │  │ Container    ││
    │  │ Runtime      │  │  │  │ Runtime      ││
    │  ├──────────────┤  │  │  ├──────────────┤│
    │  │ Pod │ Pod│Pod│  │  │  │ Pod │ Pod│Pod││
    │  └──────────────┘  │  │  └──────────────┘│
    └────────────────────┘  └──────────────────┘
```

### Control Plane Components

| Component | Role |
|-----------|------|
| **API Server** | Front-end for K8s, all communication goes through it |
| **etcd** | Distributed key-value store for cluster state |
| **Scheduler** | Assigns pods to nodes based on resources |
| **Controller Manager** | Runs controllers (ReplicaSet, Deployment, etc.) |
| **Cloud Controller** | Integrates with cloud provider APIs |

### Node Components

| Component | Role |
|-----------|------|
| **kubelet** | Agent on each node, manages pod lifecycle |
| **kube-proxy** | Network proxy, handles service routing |
| **Container Runtime** | Runs containers (containerd, CRI-O) |

---

## 3. Core Objects

### Pod (Smallest deployable unit)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: web
    env: production
spec:
  containers:
    - name: app
      image: myapp:1.0
      ports:
        - containerPort: 3000
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
      livenessProbe:
        httpGet:
          path: /health
          port: 3000
        initialDelaySeconds: 10
        periodSeconds: 30
      readinessProbe:
        httpGet:
          path: /ready
          port: 3000
        initialDelaySeconds: 5
        periodSeconds: 10
      env:
        - name: NODE_ENV
          value: "production"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: password
```

### Deployment (Manages ReplicaSets & Rolling Updates)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: myapp:1.0
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
```

### Service (Expose pods to network)

```yaml
# ClusterIP (internal only)
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP

---
# NodePort (expose on node's IP)
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 3000
      nodePort: 30080
  type: NodePort

---
# LoadBalancer (cloud provider LB)
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 3000
  type: LoadBalancer
```

### Ingress (HTTP routing)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: tls-secret
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
```

---

## 4. Essential kubectl Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# Deployments
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl describe deployment web-app
kubectl rollout status deployment/web-app
kubectl rollout history deployment/web-app
kubectl rollout undo deployment/web-app

# Pods
kubectl get pods
kubectl get pods -o wide                  # More details
kubectl describe pod pod-name
kubectl logs pod-name -f                   # Follow logs
kubectl logs pod-name -c container-name    # Multi-container
kubectl exec -it pod-name -- /bin/sh       # Shell into pod
kubectl port-forward pod-name 8080:3000    # Local port forward
kubectl delete pod pod-name

# Services
kubectl get services
kubectl get svc
kubectl expose deployment web-app --port=80 --target-port=3000

# Scaling
kubectl scale deployment web-app --replicas=5

# Config & Secrets
kubectl get configmaps
kubectl get secrets
kubectl create secret generic db-pass --from-literal=password=mysecret

# Debugging
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl top nodes
kubectl top pods
```

---

## 5. ConfigMaps & Secrets

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  config.json: |
    {
      "database": { "host": "db-service", "port": 5432 },
      "cache": { "host": "redis-service", "port": 6379 }
    }

---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
type: Opaque
data:
  username: YWRtaW4=         # base64 encoded
  password: cGFzc3dvcmQxMjM= # base64 encoded

---
# Using in Pod
spec:
  containers:
    - name: app
      envFrom:
        - configMapRef:
            name: app-config
      env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: username
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: app-config
```

---

## 6. Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 🎯 Interview Questions

### Q1: Explain the difference between a Pod, Deployment, and Service
**A:** **Pod**: Smallest unit, one or more containers sharing network/storage. **Deployment**: Manages pods via ReplicaSets, handles rolling updates, scaling, and rollbacks. **Service**: Stable network endpoint to access pods (pods are ephemeral, services are permanent).

### Q2: How does Kubernetes handle a node failure?
**A:** The controller manager detects the node is unreachable (via kubelet heartbeats). After a grace period (~5 min), it marks pods as "Terminating" and the scheduler creates new pods on healthy nodes. If using Deployments, ReplicaSet ensures desired replica count is maintained.

### Q3: What's the difference between liveness and readiness probes?
**A:** **Liveness probe**: "Is the container alive?" If it fails, K8s restarts the container. **Readiness probe**: "Is the container ready to serve traffic?" If it fails, K8s removes pod from Service endpoints. Use liveness for deadlock detection, readiness for startup/dependency checks.

### Q4: How does rolling update work?
**A:** K8s creates new ReplicaSet with updated pods, gradually scaling up new and scaling down old. `maxSurge` controls how many extra pods can exist, `maxUnavailable` controls how many can be down. If health checks fail, update pauses. `kubectl rollout undo` reverts to previous version.

---

## 📝 Practice Exercises

1. Deploy a 3-replica Node.js app with health checks
2. Create a Service and Ingress for the deployment
3. Implement ConfigMaps and Secrets for environment config
4. Set up HPA and simulate load to trigger auto-scaling
