# Docker Learning Summary

## Topic 1: What is Docker?

Docker packages applications + dependencies into isolated, portable units called **containers**.

| Concept | Description |
|---------|-------------|
| Container | Lightweight, isolated environment for running apps |
| vs VM | Shares host OS kernel (faster, smaller than VMs) |
| Benefits | Consistency, isolation, portability, efficiency |

---

## Topic 2: Images and Containers

| Term | Definition | Analogy |
|------|------------|---------|
| Image | Read-only template (blueprint) | Recipe / Class |
| Container | Running instance of image | Dish / Object |

**Key commands:**
- `docker pull` - download image
- `docker run` - create & start container
- `docker ps` - list running containers
- `docker stop/start/rm` - manage containers

**Image naming:** `registry/repository:tag` (e.g., `python:3.11-slim`)

---

## Topic 3: Dockerfile

Text file with instructions to build an image.

| Instruction | Purpose | When |
|-------------|---------|------|
| `FROM` | Base image | Build |
| `WORKDIR` | Set directory | Build |
| `COPY` | Copy files | Build |
| `RUN` | Execute command | Build |
| `ENV` | Environment variable | Build + Runtime |
| `EXPOSE` | Document port | Documentation |
| `CMD` | Default command | Runtime |
| `ENTRYPOINT` | Fixed command | Runtime |

**Build:** `docker build -t name:tag .`

---

## Topic 4: Docker Layers

Each instruction creates an immutable layer (snapshot of filesystem).

**Key points:**
- Layers are read-only and permanent
- Deleting files in new layer doesn't reduce image size
- Combine RUN commands to keep images small
- Order by change frequency (least → most changing)

**Layer caching:** Docker reuses unchanged layers for faster builds.

**Example - The Cleanup Trap:**

```dockerfile
# BAD - 3 layers, cleanup doesn't help (Total: ~130 MB)
RUN apt-get update                    # Layer 1: +30 MB (cache files stored)
RUN apt-get install -y curl vim       # Layer 2: +100 MB
RUN rm -rf /var/lib/apt/lists/*       # Layer 3: +0 MB (files still in Layer 1!)

# GOOD - 1 layer, cleanup works (Total: ~70 MB)
RUN apt-get update && \
    apt-get install -y curl vim && \
    rm -rf /var/lib/apt/lists/*       # Single layer: only final state saved
```

**Why:** Each layer is immutable. Layer 3 only records "delete these files" but files still exist in Layer 1. In single RUN, cleanup happens before snapshot.

---

## Topic 5: docker run Options

| Flag | Purpose | Example |
|------|---------|---------|
| `-d` | Detached (background) | `-d` |
| `--name` | Container name | `--name myapp` |
| `-p` | Port mapping | `-p 8080:80` |
| `-v` | Volume mount | `-v data:/app/data` |
| `-e` | Environment variable | `-e KEY=value` |
| `--network` | Connect to network | `--network mynet` |
| `--rm` | Auto-remove on stop | `--rm` |
| `-it` | Interactive terminal | `-it` |
| `--restart` | Restart policy | `--restart unless-stopped` |
| `--memory` | Memory limit | `--memory="512m"` |
| `--cpus` | CPU limit | `--cpus="1"` |

---

## Topic 6: Docker Volumes

Persist data beyond container lifecycle.

| Type | Syntax | Use Case |
|------|--------|----------|
| Named Volume | `-v mydata:/path` | Databases, persistent data |
| Bind Mount | `-v /host:/container` | Development, config files |
| tmpfs | `--tmpfs /path` | Temp/sensitive data (RAM) |

**Commands:**
- `docker volume create/ls/inspect/rm`
- `docker volume prune` - remove unused

**Read-only:** `-v /path:/path:ro`

---

## Topic 7: Docker Networking

| Driver | Use Case | Name Resolution |
|--------|----------|-----------------|
| bridge (default) | Single host | IP only |
| bridge (custom) | Single host | Container names work |
| host | No isolation | Host's network |
| none | Disabled | N/A |

**Custom network (recommended):**
```
docker network create mynetwork
docker run --network mynetwork --name app1 image
docker run --network mynetwork --name app2 image
# app1 can reach app2 by name
```

**Commands:**
- `docker network create/ls/inspect/rm`
- `docker network connect/disconnect`

---

## AWS Service Volume Mounts (LocalStack & Docker)

| Service | Image | Volume Path |
|---------|-------|-------------|
| LocalStack (all AWS) | localstack/localstack | `/var/lib/localstack` |
| PostgreSQL (RDS) | postgres:16 | `/var/lib/postgresql/data` |
| MySQL (RDS) | mysql:8 | `/var/lib/mysql` |
| Redis (ElastiCache) | redis:7 | `/data` |
| MongoDB (DocumentDB) | mongo:7 | `/data/db` |
| Elasticsearch | elasticsearch:8 | `/usr/share/elasticsearch/data` |

---

## Topic 8: Docker Compose

Define and run multi-container apps with a single YAML file.

**File structure:**
```yaml
version: '3.8'
services:
  service_name:
    image: or build:
    ports:
    volumes:
    environment:
    depends_on:
volumes:
networks:
```

**Key service options:**

| Option | Purpose |
|--------|---------|
| `image` | Use existing image |
| `build` | Build from Dockerfile |
| `ports` | Port mapping |
| `volumes` | Mount volumes |
| `environment` | Set env vars |
| `env_file` | Load from .env file |
| `depends_on` | Start order |
| `healthcheck` | Health verification |
| `restart` | Restart policy |
| `networks` | Connect to networks |

**Commands:**

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start in background |
| `docker-compose down` | Stop and remove |
| `docker-compose down -v` | Also remove volumes |
| `docker-compose logs -f` | Follow logs |
| `docker-compose exec service cmd` | Run command |
| `docker-compose build` | Rebuild images |
| `docker-compose ps` | List containers |

---

## Topic 9: Docker Secrets

Secure way to manage sensitive data (passwords, API keys, certificates).

**Why not environment variables?**
- Visible in `docker inspect`
- Appear in logs
- Not encrypted

**Secrets are:**
- Encrypted at rest (Swarm)
- Mounted as files at `/run/secrets/`
- Never exposed in logs

**Compose usage:**
```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

**Reading in Python:**
```python
with open('/run/secrets/db_password') as f:
    password = f.read().strip()
```

**Supported `_FILE` env vars:** PostgreSQL, MySQL, MariaDB support `*_FILE` variants.

---

## Topic 10: Multi-stage Builds

Use multiple `FROM` statements to create smaller production images.

**Problem:** Build images include compilers, dev deps, source code (~1GB+)

**Solution:** Build in one stage, copy only artifacts to final stage

```dockerfile
# Stage 1: Build (heavy)
FROM node:18 AS builder
RUN npm ci && npm run build

# Stage 2: Production (light)
FROM node:18-alpine
COPY --from=builder /app/dist ./dist
```

**Size reduction:**

| Language | Before | After |
|----------|--------|-------|
| Node.js | 1.5 GB | 150 MB |
| Python | 1 GB | 150 MB |
| Go | 800 MB | 10 MB |
| React | 1.5 GB | 25 MB |

**Key commands:**
- `FROM image AS stagename` - name a stage
- `COPY --from=stagename` - copy from stage
- `docker build --target stagename` - build specific stage

---

## Topic 11: Docker Security

### Image Security
- Use official/verified images
- Pin specific versions (not `latest`)
- Use minimal base images (slim, alpine, distroless)
- Scan for vulnerabilities: `docker scout cves image:tag`

### Build Security
- Run as non-root user (`USER appuser`)
- Never store secrets in image
- Use COPY instead of ADD
- Clean up in same layer as install

### Runtime Security

| Flag | Purpose |
|------|---------|
| `--read-only` | Read-only filesystem |
| `--cap-drop ALL` | Drop all capabilities |
| `--security-opt no-new-privileges` | Prevent privilege escalation |
| `--memory="512m"` | Limit memory |
| `--user 1000:1000` | Run as specific user |
| Never `--privileged` | Full host access (dangerous) |

### Network Security
- Bind to localhost: `127.0.0.1:5432:5432`
- Use internal networks for databases
- Don't expose Docker socket

---

## Topic 12: Docker in Production

### Deployment Options

| Option | Complexity | Use Case |
|--------|------------|----------|
| Docker Compose | Low | Single host, small apps |
| Kubernetes | High | Industry standard, any scale |
| AWS ECS/Fargate | Medium | AWS-native |
| Cloud Run / Container Apps | Low | Serverless |

### Key Production Components

1. **Container Registry** - Store images (ECR, GCR, Docker Hub)
2. **Reverse Proxy** - Nginx/Traefik for SSL, load balancing
3. **Logging** - Centralized (CloudWatch, ELK)
4. **Monitoring** - Prometheus + Grafana, container stats
5. **Backups** - Database dumps, volume backups

### Image Tagging Strategy
- Semantic version: `1.2.3`
- Git SHA: `abc123f`
- Combined: `1.2.3-abc123f`

### Production Checklist
- Specific image tags (not latest)
- Non-root user
- Health checks
- Resource limits
- Restart policy
- Logging configured
- Reverse proxy with SSL
- Backup strategy

---

## Topic 13: CI/CD with Docker

### Pipeline Stages

```
Code Push → Build Image → Test → Push to Registry → Deploy
```

### Popular Platforms
- GitHub Actions, GitLab CI, Jenkins, CircleCI, AWS CodePipeline

### Key GitHub Actions

| Action | Purpose |
|--------|---------|
| `docker/login-action` | Login to registry |
| `docker/build-push-action` | Build and push image |
| `aws-actions/amazon-ecr-login` | Login to AWS ECR |
| `aquasecurity/trivy-action` | Security scanning |

### GitOps with ArgoCD
1. CI builds image, pushes to ECR
2. CI updates image tag in config repo (argocd-apps)
3. ArgoCD detects change, deploys to Kubernetes

### Best Practices
- Pin action versions (`@v4` not `@latest`)
- Use BuildKit cache for faster builds
- Tag with git SHA (immutable)
- Scan images before deployment
- Separate build/test/push/deploy stages

---

## Topics Completed!

1. What is Docker
2. Images and Containers
3. Dockerfile
4. Docker Layers
5. docker run Options
6. Docker Volumes
7. Docker Networking
8. Docker Compose
9. Docker Secrets
10. Multi-stage Builds
11. Docker Security
12. Docker in Production
13. CI/CD with Docker
