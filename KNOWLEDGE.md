# Base de Conhecimento - Logística Avicultura 📘

Este documento contém os fundamentos técnicos, decisões de arquitetura e regras de negócio utilizadas no sistema de cálculo de rotas.

## 🏁 Parâmetros Fixos de Origem

O ponto de partida para todos os cálculos é o **Abatedouro Central**, cujas coordenadas geográficas são:
- **Latitude:** `-24.330706`
- **Longitude:** `-53.858058`

## 🛤️ Motor de Roteamento (OSRM)

Utilizamos o **OSRM (Open Source Routing Machine)**, um motor de roteamento de alto desempenho baseado em dados do **OpenStreetMap (OSM)**.

### Por que OSRM e não Haversine?
- **Haversine:** Calcula a distância de "vôo de pássaro" (linha reta). Ignora obstáculos, curvas e a malha viária real.
- **OSRM:** Retorna a trajetória real que um caminhão percorrerá nas estradas. Essencial para logística de precisão, onde a distância real pode ser até 40% maior que a linear em áreas rurais.

## 📐 Regras de Cálculo

### 1. Distância
A distância retornada pela API é em metros e convertida para quilômetros (km) com duas casas decimais nos relatórios principais.

### 2. Tempo de Viagem
O sistema apresenta dois indicadores de tempo:
- **Tempo OSRM:** Estimativa baseada no perfil de tráfego e limites de velocidade das vias no OSM.
- **Tempo Operacional (40 km/h):** Calculado com a fórmula:
  $$Tempo (minutos) = \frac{Distância (km)}{40} \times 60$$
  *Este parâmetro é utilizado para alinhar as expectativas com a realidade de veículos pesados em estradas rurais.*

## 📂 Formatos de Saída e Decisões Técnicas

### Relatório PDF (`fpdf2`)
- **Link Absoluto:** Devido a restrições de segurança de navegadores, o PDF gera links com o prefixo `file://` apontando para o caminho absoluto do mapa interativo na máquina local.
- **Portabilidade:** Para compartilhar a pasta inteira, o usuário deve garantir que os caminhos absolutos sejam consistentes ou utilizar o mapa HTML diretamente.

### Mapa Interativo (`folium`)
- Utiliza a biblioteca Folium (wrapper do Leaflet.js).
- Renderiza a geometria completa da rota (polilinha azul).
- Marcadores diferenciados para Início (Abatedouro) e Fim (Aviário).

## ⚠️ Limitações e Considerações
- **Dependência de Internet:** O script requer conexão ativa para consultar o servidor OSRM (`router.project-osrm.org`).
- **Precisão dos Mapas:** A precisão depende da atualização dos dados do OpenStreetMap na região.
- **Segurança:** O repositório está configurado para **não rastrear** dados gerados (PDFs/HTMLs), mantendo o foco no código-fonte.

---
*Atualizado em 21 de Março de 2026*
