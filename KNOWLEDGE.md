# Base de Conhecimento - Logística Avicultura 📘

Este documento contém os fundamentos técnicos, decisões de arquitetura e regras de negócio utilizadas no sistema de cálculo de rotas.

## 🏁 Pontos de Partida Dinâmicos

Diferente de versões anteriores, o sistema agora suporta múltiplas origens configuráveis via `data/ponto_partida.json`. 
Os pontos cadastrados incluem:
- **Abatedouro Central**
- **Fábricas de Ração (1, 2, Agrifirm, Vaccinar)**
- **Incubatório**
- **Unidade Assis Chateaubriand**

## 🛤️ Motor de Roteamento: Valhalla

O sistema utiliza o **Valhalla**, um motor de roteamento open-source de alto desempenho rodando localmente via **Docker**.

### Por que Valhalla?
- **Perfis de Carga (Truck):** Diferente de motores genéricos, o Valhalla permite o uso do perfil `truck`, que considera restrições de manobra e velocidades mais realistas para veículos pesados.
- **Privacidade e Performance:** Rodando em um container local, o processamento de milhares de rotas é extremamente rápido e não depende de limites de APIs externas.
- **Dados OSM:** Baseado no **OpenStreetMap (OSM)**, garantindo acesso às estradas rurais do Sul do Brasil.

## 📐 Regras de Cálculo e Normalização

### 1. Normalização Automática de Coordenadas
Uma das funcionalidades críticas do sistema é o método `_normalize_coordinate`. Ele detecta e corrige erros comuns de formatação em bases legadas:
- **Erro de Decimal:** Converte `-2434534` para `-24.34534`.
- **Falsos Floats:** Corrige valores como `-23903.0` para `-23.903`.
- **Validação de Faixa:** Garante que os valores estejam dentro dos limites globais (-90 a 90 para lat, -180 a 180 para lon).

### 2. Tempo de Viagem
O sistema apresenta dois indicadores de tempo:
- **Tempo Valhalla:** Estimativa baseada no perfil `truck` e na malha viária real.
- **Tempo Operacional (40 km/h):** Calculado de forma conservadora para alinhar expectativas com a frota pesada em estradas de terra:
  $$Tempo (minutos) = \frac{Distância (km)}{40} \times 60$$

## 📂 Formatos de Saída

Os arquivos são gerados na pasta `docs/rotas_por_aviario/{id}/` com nomes prefixados para fácil identificação:
- `mapa_{id}.html`: Mapa interativo (Folium/Leaflet).
- `rota_{id}.png`: Gráfico estático (Matplotlib).
- `relatorio_{id}.txt`: Documentação técnica em texto puro.
- `relatorio_{id}.pdf`: Relatório consolidado para impressão (fpdf2).

## 🏆 Créditos da Stack Tecnológica

O sucesso deste projeto é possível graças ao trabalho das seguintes comunidades e desenvolvedores:

- **Motor de Roteamento:** [Valhalla](https://github.com/valhalla/valhalla) (desenvolvido originalmente pela Mapzen, mantido pela Tesla e comunidade).
- **Dockerização Valhalla:** [Nils Nolde](https://github.com/nilsnolde/docker-valhalla) pela excelente implementação plug-and-play.
- **Dados Geográficos:** Colaboradores do [OpenStreetMap (OSM)](https://www.openstreetmap.org/).
- **Bibliotecas Python:**
    - `fpdf2`: Equipe FPDF2 (Max, Lucas Cimon, etc) pela geração de PDFs modernos.
    - `folium`: Python-visualization por integrar Leaflet.js ao Python.
    - `polyline`: Peter Chng pela codificação/decodificação eficiente de geometrias.
    - `matplotlib`: Comunidade Matplotlib pela visualização de dados.

---
*Atualizado em 26 de Março de 2026*
