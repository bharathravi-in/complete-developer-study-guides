# Day 27: Enterprise Patterns

## Learning Objectives
- Design multi-tenant agent architectures
- Implement RBAC for agent access control
- Build audit trails and compliance logging
- Handle data privacy and PII
- Design agent marketplaces and versioning
- Define SLAs for agent services

---

## 1. Multi-Tenant Architecture

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Tenant:
    id: str
    name: str
    tier: str  # "free", "pro", "enterprise"
    config: dict = field(default_factory=dict)
    api_keys: dict = field(default_factory=dict)  # provider → key
    limits: dict = field(default_factory=lambda: {
        "requests_per_minute": 60,
        "tokens_per_day": 100_000,
        "max_agents": 5,
        "max_tools": 10,
    })

class TenantManager:
    """Manage tenant isolation and configuration."""
    
    def __init__(self):
        self.tenants: dict[str, Tenant] = {}
        self.usage: dict[str, dict] = {}  # tenant_id → usage counters
    
    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self.tenants.get(tenant_id)
    
    def get_agent_config(self, tenant_id: str) -> dict:
        """Get tenant-specific agent configuration."""
        tenant = self.tenants[tenant_id]
        return {
            "model": tenant.config.get("model", "gpt-4o-mini"),
            "tools": tenant.config.get("allowed_tools", []),
            "system_prompt_prefix": tenant.config.get("prompt_prefix", ""),
            "max_steps": tenant.config.get("max_steps", 10),
            "data_sources": tenant.config.get("data_sources", []),
        }
    
    def check_limits(self, tenant_id: str) -> bool:
        """Check if tenant is within usage limits."""
        tenant = self.tenants.get(tenant_id)
        usage = self.usage.get(tenant_id, {})
        
        if usage.get("requests_today", 0) >= tenant.limits.get("requests_per_day", 1000):
            return False
        if usage.get("tokens_today", 0) >= tenant.limits["tokens_per_day"]:
            return False
        return True
    
    def record_usage(self, tenant_id: str, tokens: int, cost: float):
        """Record usage for billing."""
        if tenant_id not in self.usage:
            self.usage[tenant_id] = {"requests_today": 0, "tokens_today": 0, "cost_today": 0.0}
        self.usage[tenant_id]["requests_today"] += 1
        self.usage[tenant_id]["tokens_today"] += tokens
        self.usage[tenant_id]["cost_today"] += cost
```

---

## 2. Role-Based Access Control (RBAC)

```python
from enum import Enum

class Permission(Enum):
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_EXECUTE = "agent:execute"
    TOOL_MANAGE = "tool:manage"
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    ADMIN = "admin:all"
    AUDIT_READ = "audit:read"

@dataclass
class Role:
    name: str
    permissions: set[Permission]

# Predefined roles
ROLES = {
    "viewer": Role("viewer", {Permission.AGENT_READ}),
    "user": Role("user", {Permission.AGENT_READ, Permission.AGENT_EXECUTE, Permission.DATA_READ}),
    "developer": Role("developer", {Permission.AGENT_READ, Permission.AGENT_WRITE, 
                                     Permission.AGENT_EXECUTE, Permission.TOOL_MANAGE, Permission.DATA_READ}),
    "admin": Role("admin", {p for p in Permission}),
}

class RBACManager:
    """Manage user roles and permissions."""
    
    def __init__(self):
        self.user_roles: dict[str, list[str]] = {}  # user_id → role names
    
    def assign_role(self, user_id: str, role_name: str):
        self.user_roles.setdefault(user_id, []).append(role_name)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        roles = self.user_roles.get(user_id, [])
        for role_name in roles:
            role = ROLES.get(role_name)
            if role and (permission in role.permissions or Permission.ADMIN in role.permissions):
                return True
        return False
    
    def check_access(self, user_id: str, action: str, resource: str) -> dict:
        """Check access and return decision with reason."""
        permission_map = {
            "run_agent": Permission.AGENT_EXECUTE,
            "create_agent": Permission.AGENT_WRITE,
            "view_agent": Permission.AGENT_READ,
            "manage_tools": Permission.TOOL_MANAGE,
            "read_data": Permission.DATA_READ,
            "write_data": Permission.DATA_WRITE,
        }
        
        required = permission_map.get(action)
        if not required:
            return {"allowed": False, "reason": f"Unknown action: {action}"}
        
        allowed = self.has_permission(user_id, required)
        return {"allowed": allowed, "reason": f"{'Granted' if allowed else 'Denied'}: {required.value}"}
```

---

## 3. Audit Trail

```python
from datetime import datetime
import json

@dataclass
class AuditEvent:
    timestamp: str
    tenant_id: str
    user_id: str
    action: str
    resource: str
    details: dict
    result: str  # "success", "denied", "error"
    trace_id: str = ""

class AuditLogger:
    """Immutable audit trail for compliance."""
    
    def __init__(self, storage_backend: str = "file"):
        self.events: list[AuditEvent] = []
        self.storage = storage_backend
    
    def log(self, tenant_id: str, user_id: str, action: str, 
            resource: str, details: dict, result: str, trace_id: str = ""):
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            tenant_id=tenant_id, user_id=user_id,
            action=action, resource=resource,
            details=details, result=result, trace_id=trace_id,
        )
        self.events.append(event)
        self._persist(event)
    
    def query(self, tenant_id: str = None, user_id: str = None, 
              action: str = None, start_date: str = None) -> list[AuditEvent]:
        """Query audit log with filters."""
        results = self.events
        if tenant_id:
            results = [e for e in results if e.tenant_id == tenant_id]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if action:
            results = [e for e in results if e.action == action]
        if start_date:
            results = [e for e in results if e.timestamp >= start_date]
        return results
    
    def compliance_report(self, tenant_id: str) -> dict:
        """Generate compliance report for a tenant."""
        events = self.query(tenant_id=tenant_id)
        return {
            "total_events": len(events),
            "denied_access_attempts": sum(1 for e in events if e.result == "denied"),
            "data_access_events": sum(1 for e in events if "data" in e.action),
            "agent_executions": sum(1 for e in events if e.action == "agent_execute"),
            "unique_users": len(set(e.user_id for e in events)),
        }
    
    def _persist(self, event: AuditEvent):
        """Write to immutable storage."""
        # In production: write to append-only log (S3, immutable DB)
        with open("audit.jsonl", "a") as f:
            f.write(json.dumps(event.__dict__) + "\n")
```

---

## 4. Data Privacy & PII

```python
import re

class PIIHandler:
    """Detect and handle PII in agent interactions."""
    
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }
    
    def detect(self, text: str) -> list[dict]:
        """Detect PII in text."""
        findings = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append({"type": pii_type, "start": match.start(), "end": match.end()})
        return findings
    
    def redact(self, text: str) -> str:
        """Replace PII with redaction markers."""
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", text)
        return text
    
    def anonymize_for_logging(self, messages: list[dict]) -> list[dict]:
        """Anonymize messages before logging."""
        anonymized = []
        for msg in messages:
            content = msg.get("content", "")
            anonymized.append({**msg, "content": self.redact(content)})
        return anonymized

class DataRetentionPolicy:
    """Manage data retention per compliance requirements."""
    
    def __init__(self, default_retention_days: int = 30):
        self.default_retention = default_retention_days
        self.tenant_policies: dict[str, int] = {}
    
    def set_policy(self, tenant_id: str, retention_days: int):
        self.tenant_policies[tenant_id] = retention_days
    
    def should_delete(self, tenant_id: str, created_at: datetime) -> bool:
        retention = self.tenant_policies.get(tenant_id, self.default_retention)
        age = (datetime.now() - created_at).days
        return age > retention
```

---

## 5. Agent Versioning & Marketplace

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentVersion:
    agent_id: str
    version: str  # semver: "1.2.3"
    system_prompt: str
    tools: list[str]
    model: str
    config: dict
    created_at: str
    status: str = "active"  # active, deprecated, retired

class AgentRegistry:
    """Registry for managing agent versions."""
    
    def __init__(self):
        self.agents: dict[str, list[AgentVersion]] = {}
    
    def publish(self, agent: AgentVersion):
        """Publish a new agent version."""
        self.agents.setdefault(agent.agent_id, []).append(agent)
    
    def get_latest(self, agent_id: str) -> AgentVersion | None:
        versions = self.agents.get(agent_id, [])
        active = [v for v in versions if v.status == "active"]
        return active[-1] if active else None
    
    def get_version(self, agent_id: str, version: str) -> AgentVersion | None:
        versions = self.agents.get(agent_id, [])
        return next((v for v in versions if v.version == version), None)
    
    def deprecate(self, agent_id: str, version: str):
        """Mark a version as deprecated."""
        v = self.get_version(agent_id, version)
        if v:
            v.status = "deprecated"
    
    def rollback(self, agent_id: str) -> AgentVersion | None:
        """Rollback to previous active version."""
        versions = self.agents.get(agent_id, [])
        active = [v for v in versions if v.status == "active"]
        if len(active) >= 2:
            active[-1].status = "retired"
            return active[-2]
        return None

class AgentMarketplace:
    """Marketplace for shared agents."""
    
    def __init__(self):
        self.listings: list[dict] = []
    
    def list_agent(self, agent_id: str, name: str, description: str, 
                   category: str, pricing: str = "free"):
        self.listings.append({
            "agent_id": agent_id, "name": name, "description": description,
            "category": category, "pricing": pricing, "installs": 0, "rating": 0.0,
        })
    
    def search(self, query: str, category: str = None) -> list[dict]:
        results = self.listings
        if category:
            results = [l for l in results if l["category"] == category]
        if query:
            results = [l for l in results if query.lower() in l["description"].lower() 
                      or query.lower() in l["name"].lower()]
        return results
```

---

## 6. SLA Management

```python
@dataclass
class SLA:
    tier: str
    availability: float  # e.g., 99.9
    max_latency_p95_ms: int
    max_response_time_ms: int
    support_response_hours: int
    data_retention_days: int

SLAS = {
    "free": SLA("free", 99.0, 30000, 60000, 72, 7),
    "pro": SLA("pro", 99.9, 10000, 30000, 24, 30),
    "enterprise": SLA("enterprise", 99.99, 5000, 15000, 4, 90),
}

class SLAMonitor:
    """Monitor SLA compliance."""
    
    def __init__(self):
        self.measurements: dict[str, list[dict]] = {}
    
    def record(self, tenant_id: str, latency_ms: float, success: bool):
        self.measurements.setdefault(tenant_id, []).append({
            "latency_ms": latency_ms, "success": success,
            "timestamp": datetime.now().isoformat(),
        })
    
    def check_compliance(self, tenant_id: str, sla: SLA) -> dict:
        """Check if we're meeting SLA for a tenant."""
        measurements = self.measurements.get(tenant_id, [])
        if not measurements:
            return {"compliant": True, "no_data": True}
        
        total = len(measurements)
        successful = sum(1 for m in measurements if m["success"])
        availability = (successful / total) * 100
        
        latencies = sorted(m["latency_ms"] for m in measurements)
        p95 = latencies[int(total * 0.95)] if total >= 20 else latencies[-1]
        
        violations = []
        if availability < sla.availability:
            violations.append(f"Availability: {availability:.2f}% < {sla.availability}%")
        if p95 > sla.max_latency_p95_ms:
            violations.append(f"P95 latency: {p95}ms > {sla.max_latency_p95_ms}ms")
        
        return {"compliant": len(violations) == 0, "violations": violations,
                "availability": availability, "p95_latency_ms": p95}
```

---

## Interview Questions

### Beginner
1. **Why do enterprise agent platforms need multi-tenancy?** Multiple customers share infrastructure (cost efficient). Each tenant needs: isolated data, separate billing, custom configuration, independent limits. Without isolation: data leaks between customers, one tenant can exhaust resources for others.
2. **What is RBAC and why do agents need it?** Role-Based Access Control: users get roles (admin, developer, viewer), roles have permissions. Agents need it because: different users should access different agents/tools, some actions are sensitive (data writes), compliance requires access control. Prevents unauthorized agent usage.
3. **Why are audit trails important for agent systems?** Compliance (who did what, when). Debugging (trace back failures). Security (detect unauthorized access). Accountability (which agent made what decision). Billing (track usage per user). Regulatory (GDPR, SOX, HIPAA require logging).

### Intermediate
4. **How do you handle PII in agent conversations?** Detect: regex patterns + NER models for PII. Redact: before logging, replace with tokens. Minimize: don't store full conversations if not needed. Retention: auto-delete after policy period. User rights: support data deletion requests (GDPR). Encrypt: PII at rest and in transit.
5. **Design a versioning strategy for production agents.** Semantic versioning (major.minor.patch). Blue-green deployment: new version gets % of traffic. Rollback: instant revert to previous version. Canary: 5% traffic → monitor → full rollout. A/B testing: compare versions on quality metrics. Deprecation: warn before retiring old versions.
6. **How do you handle SLAs for agent services?** Define: availability, latency, throughput per tier. Monitor: real-time dashboards, automated alerts on violations. Budget: error budget (99.9% = 43min/month downtime allowed). Escalation: auto-alert when approaching limits. Credits: automated SLA credit calculation.

### Advanced
7. **Design an enterprise agent platform for a Fortune 500 company.** Multi-tenant with data isolation. SSO/SAML authentication. RBAC with custom roles. Compliance: SOC2, HIPAA (if healthcare). Multi-region deployment. Audit logging with 7-year retention. PII handling (detect, redact, encrypt). Agent marketplace (internal). SLA tiers. Cost allocation per department. Disaster recovery.
8. **How do you handle cross-tenant data isolation when agents share infrastructure?** Logical isolation: tenant_id on all queries, enforce at middleware layer. Network: VPC per tenant (enterprise tier). Compute: dedicated instances for enterprise. Data: encrypted per-tenant keys. Monitoring: alert on any cross-tenant data access. Testing: regularly verify isolation with penetration tests.
9. **Design a billing system for an agent platform.** Track: tokens consumed, API calls, compute time, storage. Pricing: per-token, per-request, or subscription tiers. Real-time usage dashboard. Alerts: approaching limits. Invoice: monthly with detailed breakdown. Credits: for SLA violations. Usage optimization recommendations.

---

## Hands-On Exercise
1. Implement TenantManager with configuration and usage limits
2. Build RBAC system with roles and permission checking
3. Create audit logger with immutable storage and querying
4. Implement PII detection and redaction
5. Build agent versioning with publish, deprecate, rollback
6. Create SLA monitor that checks compliance metrics
7. Integrate all components into a secured enterprise agent endpoint
