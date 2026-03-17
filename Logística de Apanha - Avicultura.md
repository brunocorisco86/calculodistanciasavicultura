# Logística de Apanha - Avicultura

Este script Python foi desenvolvido para calcular a distância real (via estradas) e o tempo de viagem entre o abatedouro central e diversos aviários.

## Configurações
- **Ponto de Partida (Abatedouro):** `-24.330706428602536, -53.85805796419288`
- **Velocidade Média:** 40 km/h
- **API de Roteamento:** OSRM (Open Source Routing Machine) - Gratuito e sem necessidade de chave API.

## Pré-requisitos
Certifique-se de ter o Python 3 instalado e a biblioteca `requests`:
```bash
pip install requests
```

## Como Usar
1. Prepare seu arquivo `.csv` seguindo o modelo:
   | aviario | nome produtor | latitude | longitude |
   |---------|---------------|----------|-----------|
   | 140     | jose da silva | -24.0    | -53.0     |

2. Execute o script passando o caminho do seu CSV:
```bash
python logistica_aviarios.py aviarios.csv
```

## Funcionamento
O script consulta as rotas reais via OpenStreetMap para garantir que a distância calculada considere as estradas, e não apenas uma linha reta (haversine). O tempo é calculado com base na velocidade média de 40 km/h solicitada.
