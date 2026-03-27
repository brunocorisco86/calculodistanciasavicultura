#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOG_DIR="${ROOT_DIR}/logs/valhalla"
LOG_FILE="${LOG_DIR}/valhalla_health.log"

VALHALLA_HOST="${VALHALLA_HOST:-localhost}"
VALHALLA_PORT="${VALHALLA_PORT:-8002}"
INTERVAL="${INTERVAL:-30}"  # segundos

mkdir -p "${LOG_DIR}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

log_info "Iniciando monitoramento do Valhalla em ${VALHALLA_HOST}:${VALHALLA_PORT}"
log_info "Logs em: ${LOG_FILE}"
echo "==== $(date '+%Y-%m-%d %H:%M:%S') - Iniciando monitoramento ====" >> "${LOG_FILE}"

while true; do
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
  url="http://${VALHALLA_HOST}:${VALHALLA_PORT}/status"

  # Pega código HTTP e resposta JSON (silenciosamente)
  response="$(curl -s -w "\n%{http_code}" "${url}" || echo -e "{}\n000")"
  http_code="$(echo "${response}" | tail -n1)"
  body="$(echo "${response}" | sed '$d')"

  if [[ "${http_code}" == "200" ]]; then
    # extrair dados usando jq
    version="$(echo "${body}" | jq -r '.version // "unknown"')"
    # ready e tiles podem não estar presentes em algumas versões
    ready="$(echo "${body}" | jq -r '.ready // "N/A"')"
    tiles="$(echo "${body}" | jq -r '.has_tiles // "N/A"')"

    log_info "OK ${http_code} - Version: ${version} (Ready: ${ready}, Tiles: ${tiles})"
    echo -e "${timestamp}\tOK\t${http_code}\t${version}\t${ready}\t${tiles}" >> "${LOG_FILE}"
  else
    log_warn "Falha ${http_code} ao acessar ${url}"
    echo -e "${timestamp}\tFAIL\t${http_code}\t${body}" >> "${LOG_FILE}"
  fi

  sleep "${INTERVAL}"
done
