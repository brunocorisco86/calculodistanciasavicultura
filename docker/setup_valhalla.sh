#!/usr/bin/env bash
# =============================================================================
# setup_valhalla.sh
# Configura e sobe o servidor Valhalla com dados do Paraná (OSM/GeoFabrik)
# C.Vale - Logística de Apanha Avicultura
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Variáveis configuráveis
# ---------------------------------------------------------------------------
OSM_URL="https://download.geofabrik.de/south-america/brazil/parana-latest.osm.pbf"
PBF_FILENAME="parana-latest.osm.pbf"
CUSTOM_FILES_DIR="$(pwd)/custom_files"
CONTAINER_NAME="valhalla_cvale"
VALHALLA_PORT="8002"
VALHALLA_IMAGE="ghcr.io/valhalla/valhalla:latest"

# ---------------------------------------------------------------------------
# Cores para output
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---------------------------------------------------------------------------
# 1. Verificar dependências
# ---------------------------------------------------------------------------
log_info "Verificando dependências..."

for cmd in docker curl wget; do
  if ! command -v "$cmd" &>/dev/null; then
    log_error "'$cmd' não encontrado. Instale antes de continuar."
    exit 1
  fi
done

if ! docker info &>/dev/null; then
  log_error "Docker não está rodando. Inicie o serviço Docker primeiro."
  exit 1
fi

log_info "Todas as dependências OK."

# ---------------------------------------------------------------------------
# 2. Criar diretório custom_files
# ---------------------------------------------------------------------------
log_info "Criando diretório: ${CUSTOM_FILES_DIR}"
mkdir -p "${CUSTOM_FILES_DIR}"

# ---------------------------------------------------------------------------
# 3. Baixar arquivo OSM PBF
# ---------------------------------------------------------------------------
PBF_PATH="${CUSTOM_FILES_DIR}/${PBF_FILENAME}"

if [[ -f "${PBF_PATH}" ]]; then
  log_warn "Arquivo PBF já existe: ${PBF_PATH}"
  read -rp "Deseja rebaixar o arquivo? [s/N]: " RESPOSTA
  if [[ "${RESPOSTA,,}" == "s" ]]; then
    log_info "Removendo arquivo existente..."
    rm -f "${PBF_PATH}"
  else
    log_info "Mantendo arquivo existente. Pulando download."
  fi
fi

if [[ ! -f "${PBF_PATH}" ]]; then
  log_info "Baixando ${PBF_FILENAME} do GeoFabrik..."
  log_info "URL: ${OSM_URL}"
  wget --progress=bar:force -O "${PBF_PATH}" "${OSM_URL}"
  log_info "Download concluído: ${PBF_PATH}"
fi

# ---------------------------------------------------------------------------
# 4. Parar e remover container existente (se houver)
# ---------------------------------------------------------------------------
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  log_warn "Container '${CONTAINER_NAME}' já existe. Removendo..."
  docker stop "${CONTAINER_NAME}" 2>/dev/null || true
  docker rm   "${CONTAINER_NAME}" 2>/dev/null || true
  log_info "Container removido."
fi

# ---------------------------------------------------------------------------
# 5. Subir container Valhalla
# ---------------------------------------------------------------------------
log_info "Iniciando container Valhalla..."
log_info "Imagem : ${VALHALLA_IMAGE}"
log_info "Porta  : ${VALHALLA_PORT}"
log_info "Dados  : ${CUSTOM_FILES_DIR}"

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -p "${VALHALLA_PORT}:8002" \
  -v "${CUSTOM_FILES_DIR}:/custom_files" \
  -e "tile_urls=${OSM_URL}" \
  "${VALHALLA_IMAGE}"

log_info "Container '${CONTAINER_NAME}' iniciado com sucesso!"

# ---------------------------------------------------------------------------
# 6. Aguardar inicialização e validar
# ---------------------------------------------------------------------------
log_info "Aguardando Valhalla processar tiles (pode demorar alguns minutos)..."
log_warn "Acompanhe o progresso com: docker logs -f ${CONTAINER_NAME}"

MAX_WAIT=300   # 5 minutos
ELAPSED=0
INTERVAL=10

while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "http://localhost:${VALHALLA_PORT}/status" 2>/dev/null || echo "000")

  if [[ "${HTTP_CODE}" == "200" ]]; then
    log_info "Valhalla está pronto! Endpoint: http://localhost:${VALHALLA_PORT}"
    log_info "Teste rápido:"
    echo "  curl http://localhost:${VALHALLA_PORT}/status"
    break
  fi

  log_warn "Aguardando... (${ELAPSED}s / ${MAX_WAIT}s) - HTTP ${HTTP_CODE}"
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

if [[ $ELAPSED -ge $MAX_WAIT ]]; then
  log_warn "Timeout atingido. O Valhalla ainda pode estar processando tiles."
  log_warn "Execute manualmente: curl http://localhost:${VALHALLA_PORT}/status"
fi

log_info "=================================================================="
log_info "  Comandos úteis:"
log_info "  Ver logs    : docker logs -f ${CONTAINER_NAME}"
log_info "  Parar       : docker stop ${CONTAINER_NAME}"
log_info "  Reiniciar   : docker start ${CONTAINER_NAME}"
log_info "  Status API  : curl http://localhost:${VALHALLA_PORT}/status"
log_info "=================================================================="
