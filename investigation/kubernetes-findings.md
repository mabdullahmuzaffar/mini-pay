# Kubernetes Starter Manifest — Defect Analysis

Original file preserved at: `investigation/broken-api.original.yaml`
Corrected manifest: `kubernetes/30-api-deployment.yaml`

## The four defects

| ID | Location | Defect | Symptom |
|----|----------|--------|---------|
| D1 | Deployment, image field | `image: YOUR_IMAGE_HERE` | Pod stuck `InvalidImageName` — container never starts |
| D2 | Deployment, readinessProbe | probe targets port `8081`, container listens on `8080` | Pod `Running` but `0/1 READY`, removed from Service endpoints |
| D3 | Service, selector | `app: minipay-backend` but pod label is `app: minipay-api` | `kubectl get endpoints` shows `<none>` — zero pods selected |
| D4 | Service, targetPort | `targetPort: 8081` but app listens on `8080` | Traffic forwarded to closed port even after D3 fixed |

## Why D2 is the most deceptive

The livenessProbe is correctly set to port 8080, so the container is
never restarted and logs look completely healthy. Only readinessProbe
is wrong. Readiness controls Service membership — the pod runs fine
but never receives traffic, with no error logs to alert you.

## Evidence from applying the broken manifest

### Pod status — D1 visible immediately
```text
NAME                           READY   STATUS             RESTARTS   AGE
minipay-api-74dd7d5775-fwcgb   0/1     InvalidImageName   0          17s
minipay-api-74dd7d5775-kjnlr   0/1     InvalidImageName   0          17s
```

### describe pod — D1 and D2 visible
```text
Image: YOUR_IMAGE_HERE
Readiness: http-get http://:8081/health delay=2s timeout=1s period=5s
```

### Service endpoints — D3 visible
```text
NAME          ENDPOINTS   AGE
minipay-api   <none>      17s
```

### Selector vs labels — D3 proof
```text
Service selector: {"app":"minipay-backend"}
Pod labels: app=minipay-api
```

## Diagnostic commands

```bash
# D1 — image pull failure
kubectl -n minipay get pods
kubectl -n minipay describe pod <pod> | grep -A5 Events

# D2 — readiness probe port mismatch
kubectl -n minipay describe pod <pod> | grep -A3 Readiness

# D3 — the decisive check: empty endpoints
kubectl -n minipay get endpoints minipay-api
kubectl -n minipay get svc minipay-api -o jsonpath='{.spec.selector}'
kubectl -n minipay get pods --show-labels

# D4 — port confirmed by exec
kubectl -n minipay exec <pod> -- curl -s http://localhost:8080/health
```

## Corrections applied

| ID | Before | After |
|----|--------|-------|
| D1 | `image: YOUR_IMAGE_HERE` | `image: minipay-api:local` + `imagePullPolicy: IfNotPresent` |
| D2 | readinessProbe port `8081` | readinessProbe port `8080` |
| D3 | selector `app: minipay-backend` | selector `app: minipay-api` |
| D4 | `targetPort: 8081` | `targetPort: 8080` |

## Additional gaps closed

- No Namespace resource — added `kubernetes/00-namespace.yaml`
- No resource requests/limits — added to every container
- No database — added PostgreSQL StatefulSet with PersistentVolumeClaim
- No ConfigMap/Secret — separated config from credentials
- No startup ordering — added `wait-for-db` init container
