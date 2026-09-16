# Setup

## Requirements
- Docker + Docker Compose v2
- Python 3.12
- kind and kubectl (for Kubernetes)

## Docker Compose

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    docker compose up --build -d
    # Open http://localhost:8080

## Load 50k rows

    python3 database/generate_data.py | docker compose exec -T db psql -U minipay -d minipay -q

## Tests

    pytest tests/api -v
    playwright install chromium
    pytest tests/ui -v --browser chromium

## Support tool

    export MINIPAY_API_URL=http://localhost:8081
    export MINIPAY_API_KEY=dev-local-key
    python3 -m python.support_tool --health
    python3 -m python.support_tool --transaction TXN00012345

## Kubernetes

    kind create cluster --name minipay --config kind-cluster.yaml
    docker build -t minipay-api:local -f docker/api.Dockerfile .
    docker build -t minipay-ui:local -f docker/ui.Dockerfile .
    kind load docker-image minipay-api:local minipay-ui:local --name minipay
    kubectl apply -k kubernetes/
    # Open http://localhost:30080
