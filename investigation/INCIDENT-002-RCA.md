# INCIDENT-002 — App Unreachable After Kubernetes Deployment

**Priority:** P1
**Status:** Resolved
**Date:** 2026-09-16

## Summary

After deploying MiniPay using the supplied starter manifest, users could
not reach the application. Pods appeared to start. There were four
independent defects — any one sufficient to cause the outage.

## Timeline

| Time | Event |
|---|---|
| T+0m | Manifest applied, outage reported |
| T+1m | `kubectl get pods` shows `InvalidImageName` — D1 found |
| T+5m | Image loaded; pods `Running` but `0/1 READY` — D2 found |
| T+12m | Readiness fixed; `kubectl get endpoints` shows `<none>` — D3 found |
| T+16m | Selector fixed; connections refused — D4 found |
| T+20m | All four corrected, all pods `1/1 Running`, service restored |

## Investigation

### Step 1 — Pod status (D1 visible)
```text
NAME                           READY   STATUS             RESTARTS   AGE
minipay-api-74dd7d5775-fwcgb   0/1     InvalidImageName   0          17s
minipay-api-74dd7d5775-kjnlr   0/1     InvalidImageName   0          17s
```

### Step 2 — describe pod (D1 and D2 visible)
```text
Image: YOUR_IMAGE_HERE
State: Waiting — Reason: InvalidImageName
Readiness: http-get http://:8081/health ← wrong port
Liveness: http-get http://:8080/health ← correct port
```

### Step 3 — Endpoints (D3 visible)
```text
NAME          ENDPOINTS   AGE
minipay-api   <none>      17s
```

### Step 4 — Selector vs labels (D3 proof)
```text
Service selector: {"app":"minipay-backend"}
Pod labels: app=minipay-api
```
These do not match — Service selects zero pods.

## Root Cause

Four defects in `broken-api.yaml`. Full analysis in
`investigation/kubernetes-findings.md`.

The key lesson: **"pods are Running" is not "the service works"**.
Running describes a container process. Serving traffic also requires
the pod to be Ready, the Service selector to match it, and the target
port to be what the process actually listens on. Three of those four
were wrong simultaneously.

## Fix

Corrected manifest: `kubernetes/30-api-deployment.yaml`

## Validation
```text
NAME                               READY   STATUS    RESTARTS   AGE
pod/minipay-api-597c568f98-k5zqj   1/1     Running   0          2m27s
pod/minipay-api-597c568f98-ztjw8   1/1     Running   0          2m38s
pod/minipay-db-0                   1/1     Running   0          15m
pod/minipay-ui-6c6f66d5c5-lr82g    1/1     Running   0          12m

endpoints/minipay-api 10.244.0.16:8080,10.244.0.17:8080

curl http://localhost:30080/health
{"status":"ok","database":"ok","time":"2026-09-16T07:20:40.375421Z"}
```

Rolling update and rollback confirmed working:
- Scaled to 3 replicas — new pod came up cleanly
- `kubectl rollout undo` rolled back successfully

## Prevention

1. Run `kubectl apply --dry-run=server` before every deploy
2. Check `kubectl get endpoints <svc>` immediately after deploy — empty endpoints = selector mismatch
3. Use named ports in manifests (probe and Service both reference the name, not the number — mismatch becomes impossible)
4. Add a post-deploy smoke test: `curl /health` from outside the cluster
5. Never rely on "pods are Running" as the success signal
