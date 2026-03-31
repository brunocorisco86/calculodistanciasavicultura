# Logística de Apanha - Avicultura 🚛🐔

Sistema inteligente para otimização logística na avicultura, focado no cálculo de rotas reais, distâncias precisas e tempos de viagem entre pontos centrais e aviários.

## 📌 Visão Geral

Este projeto utiliza o motor de roteamento **Valhalla** (rodando localmente em Docker) e dados do **OpenStreetMap** para processar milhares de rotas com precisão operacional. Ele resolve problemas comuns de dados mal formatados e gera documentação completa para suporte logístico.

## ✨ Principais Funcionalidades

- **Motor Valhalla (Perfil Truck):** Cálculo de rota real considerando restrições de manobra e tráfego pesado.
- **Normalização Automática:** Corrige erros de coordenadas (ex: `-2434534` para `-24.34534`) durante o processamento.
- **Multiorigem Dinâmica:** Permite escolher entre Abatedouros, Fábricas de Ração, Incubatórios ou Unidades de Apoio através de um menu interativo e configuração via JSON (`data/ponto_partida.json`).
- **Relatórios Personalizados:** Cada aviário recebe:
  - 📄 **PDF Consolidado:** Gerado com `fpdf2` contendo gráficos e roteiros.
  - 🗺️ **Mapa Interativo (HTML):** Gerado com `folium` (Leaflet).
  - 📝 **Relatório TXT:** Documento de texto contendo as manobras e orientações.
  - 📉 **Gráfico PNG:** Plotagem estática da trajetória (Matplotlib).
- **Utilitário de Exportação:** Script para gerar arquivos ZIP (`scripts/zip_reports.py`) dos relatórios.

## 🚀 Como Começar

### Configuração do Valhalla (Docker)

O projeto inclui um setup automatizado para o Sul do Brasil.

```bash
chmod +x docker/setup_valhalla.sh
./docker/setup_valhalla.sh
```

### Instalação e Execução

1. Configure o ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. Execute o orquestrador principal e escolha o ponto de partida:
   ```bash
   python main.py
   ```

## 📁 Estrutura do Projeto

- `data/ponto_partida.json`: Cadastro de pontos centrais da cooperativa.
- `docs/rotas_por_aviario/`: Local onde todos os arquivos individuais são salvos.
- `scripts/zip_reports.py`: Utilitário para compactar mapas e relatórios TXT para distribuição.

## 🏆 Créditos e Tecnologias

Gostaríamos de agradecer às comunidades e desenvolvedores que tornaram este projeto possível:

- **Valhalla Routing Engine:** Comunidade [Valhalla](https://github.com/valhalla/valhalla) (Mapzen/Tesla).
- **Docker Wrapper:** [Nils Nolde](https://github.com/nilsnolde/docker-valhalla) pelo suporte à implementação Docker.
- **Dados:** [OpenStreetMap](https://www.openstreetmap.org/) (Contribuidores OSM).
- **Core Stack:** [Python 3.12](https://python.org/), [Requests](https://requests.readthedocs.io/), [Folium](https://python-visualization.github.io/folium/), [FPDF2](https://github.com/fpdf2/fpdf2), [Matplotlib](https://matplotlib.org/).

---
*Desenvolvido para C.VALE - Cooperativa Agroindustrial*
*Última Atualização: 26 de Março de 2026*
