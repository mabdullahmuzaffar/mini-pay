# Linux Evidence

**Environment:** WSL2 Ubuntu 24.04.5 LTS on Windows 11, Docker Desktop  
**Host:** DESKTOP-HNESNGA — 12-core Intel i5-1235U, 3.7Gi RAM

## 1. OS and Kernel

Linux DESKTOP-HNESNGA 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC
Ubuntu 24.04.5 LTS (Noble Numbat)


## 2. CPU and Memory

CPU: 12th Gen Intel Core i5-1235U, 12 CPUs (6 cores x 2 threads)
Memory: 3.7Gi total, 1.1Gi used, 2.6Gi available
Swap: 1.0Gi total, 44Ki used


## 3. Disk Usage

/dev/sdf 1007G 3.0G 953G 1% / (WSL2 root)
C:\ 238G 196G 42G 83% /mnt/c (Windows C drive)

Project directory breakdown:
244M .
242M ./.venv
880K ./.git


## 4. Listening Ports

Port 8080 — nginx (MiniPay UI)
Port 8081 — FastAPI (MiniPay API)
Port 5432 — PostgreSQL (MiniPay DB)
Port 53 — systemd-resolved (DNS)


Output from `sudo ss -tlnp`:

*:8080 LISTEN (nginx container)
*:8081 LISTEN (api container)
*:5432 LISTEN (db container)


## 5. Highest Memory Process

PID COMMAND RSS
563 docker-desktop 31000 KB
198 unattended-upgr 22496 KB
45 systemd-journal 16700 KB
3593 wsl-pro-service 13544 KB
1 systemd 13336 KB

Highest: docker-desktop (PID 563), RSS 31MB

## 6. DNS and Network

eth0: 172.17.96.191/20 (WSL2 virtual NIC)
DNS resolution: google.com → 2a00:1450:4019:817::200e (working)


## 7. Application and Container Logs

API container — all requests returning 200, request IDs on every line
DB container — PostgreSQL 16.15 started, accepting connections on port 5432
"database system is ready to accept connections"


## 8. Health Check Script

=== MiniPay Health Check — Wed Sep 16 11:36:47 PKT 2026 ===
[ OK ] CPU load 0.10 on 12 cores
[ OK ] Memory 30% used
[ OK ] Disk 1% used
[ OK ] Port 8080 listening
[ OK ] Port 8081 listening
[ OK ] Port 5432 listening
[ OK ] API health 200
[ OK ] Database reachable from API
[ OK ] UI returned 200
[ OK ] No unhealthy containers

Summary: 0 FAIL, 0 WARN
Exit code: 0


## Troubleshooting Approaches

### High CPU
1. Check load vs cores: `uptime` then `nproc`
2. Find the process: `ps -eo pid,comm,%cpu --sort=-%cpu | head`
3. If container: `docker stats --no-stream`
4. If PostgreSQL: `SELECT pid, now()-query_start AS runtime, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY runtime DESC;`
5. Mitigate: scale the API with `docker compose up --scale api=3`

### Low Disk Space
1. Which filesystem: `df -h`
2. What's using it: `du -h --max-depth=1 / | sort -hr | head`
3. Docker usage: `docker system df`
4. Safe cleanup: `docker system prune -f` — never `docker volume prune` (deletes the database)
5. Deleted-but-open files: `sudo lsof +L1` (space not freed until process restarts)

### API Endpoint Unreachable
1. Is the process running: `docker compose ps`
2. Is it listening: `sudo ss -tlnp | grep 8080`
3. Does it answer locally: `curl http://localhost:8081/health`
4. Check nginx proxy: `docker compose logs ui --tail=20`
5. If Kubernetes: `kubectl -n minipay get endpoints minipay-api` — empty means selector mismatch

### Process Keeps Terminating
1. Read exit reason: `docker inspect <container> --format '{{.State.ExitCode}} {{.State.OOMKilled}}'`
2. Exit code 137 = OOM killed: `dmesg | grep -i "killed process"`
3. Read logs from the dead instance before it restarted: `docker compose logs api`
4. Check if a liveness probe is killing it: look for probe failures in `docker compose logs`
5. Fix: raise memory limit in docker-compose.yml or find the memory leak
