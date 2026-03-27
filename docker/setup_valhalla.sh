#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CUSTOM_FILES_DIR="${ROOT_DIR}/custom_files"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

log_info "Preparando diretório custom_files..."
mkdir -p "${CUSTOM_FILES_DIR}"
chmod -R 777 "${CUSTOM_FILES_DIR}" || true

log_info "Derrubando stack anterior (se existir)..."
docker compose -f "${SCRIPT_DIR}/docker-compose.yml" down -v --remove-orphans || true

# Export UID/GID for docker compose
export UID=$(id -u)
export GID=$(id -g)

log_info "Subindo Valhalla (docker-valhalla plug and play)..."
docker compose -f "${SCRIPT_DIR}/docker-compose.yml" up -d

MAX_WAIT=900
ELAPSED=0
INTERVAL=10

log_info "Aguardando Valhalla ficar pronto..."
while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  # Check for 200 OK and presence of "version"
  if curl -s "http://localhost:8002/status" | grep -q '"version"'; then
    log_info "Valhalla pronto em http://localhost:8002"
    exit 0
  fi
  
  # Check if container is even running
  if ! docker ps --filter name=valhalla_cvale --filter status=running | grep -q valhalla_cvale; then
      log_error "Container valhalla_cvale parou de rodar. Verifique os logs."
      docker logs valhalla_cvale --tail 20
      exit 1
  fi

  log_info "Aguardando... (${ELAPSED}s / ${MAX_WAIT}s)"
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

log_error "Timeout atingido. Verifique logs com: docker logs -f valhalla_cvale"
exit 1