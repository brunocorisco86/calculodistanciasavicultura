# Logística de Apanha - Avicultura 🚛🐔

Sistema inteligente para otimização logística na avicultura, focado no cálculo de rotas reais, distâncias precisas e tempos de viagem entre abatedouros e aviários integrados.

## 📌 Visão Geral

Este projeto substitui cálculos simplistas de distância linear (Haversine) por trajetórias reais baseadas na malha viária (OpenStreetMap), utilizando a API do **OSRM (Open Source Routing Machine)**. Ele processa grandes volumes de dados de aviários e gera documentação completa para suporte à decisão logística.

## ✨ Principais Funcionalidades

- **Cálculo de Rota Real:** Trajetória exata via estradas atualizadas.
- **Estimativa de Tempo Dual:** 
  - Tempo dinâmico baseado no motor de roteamento OSRM.
  - Tempo fixo baseado em velocidade média operacional (ex: 40 km/h).
- **Relatórios Multiformato:** Para cada aviário, o sistema gera automaticamente:
  - 📄 **Relatório PDF:** Documento consolidado com mapa, roteiro e link interativo.
  - 🗺️ **Mapa Interativo (HTML):** Visualização dinâmica com zoom e marcadores (Folium).
  - 📝 **Relatório Markdown:** Documentação técnica da rota em texto.
  - 📉 **Gráfico de Rota (PNG):** Representação estática da trajetória para consulta rápida.
- **Processamento em Lote:** Capacidade de processar milhares de pontos a partir de arquivos CSV.
- **Logging Robusto:** Rastreamento completo para auditoria e monitoramento de falhas.

## 🚀 Como Começar

### Pré-requisitos

- Python 3.12 (ou superior)
- Ambiente Virtual (venv) configurado

### Instalação

1. Clone o repositório e acesse a pasta:
   ```bash
   git clone <url-do-repositorio>
   cd calculodistanciasavicultura
   ```

2. Configure o ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

## 🛠️ Uso

### Preparação dos Dados
Coloque seu arquivo de entrada em `data/raw/aviarios.csv`. O formato esperado é:
`aviario, nome produtor, latitude, longitude`

**Dica:** Utilize o modelo disponível em `template/aviarios_template.csv` como base para criar seu arquivo de dados.

### Execução Principal
Para gerar todos os relatórios (MD, HTML, PNG e PDF):
```bash
python main.py
```

### Conversão Manual para PDF
Caso já tenha as pastas geradas e queira apenas criar/atualizar os PDFs:
```bash
python src/convert_to_pdf.py
```

## 📁 Estrutura do Projeto

```text
├── data/
│   ├── raw/                # CSVs de entrada
│   └── processed/          # Resultados consolidados
├── docs/
│   └── rotas_por_aviario/  # [IGNORADO] Relatórios gerados individualmente
├── src/
│   ├── api_client.py       # Cliente API OSRM
│   ├── logistica_aviarios.py # Core do processamento
│   ├── report_generator.py  # Engine de geração de relatórios (PDF/HTML/MD)
│   ├── convert_to_pdf.py    # Script utilitário de conversão em massa
│   └── utils/              # Auxiliares e Logger
├── main.py                 # Orquestrador do sistema
└── requirements.txt        # Dependências (Folium, FPDF2, Matplotlib, etc)
```

## ⚠️ Qualidade dos Dados e Auditoria

Para garantir a precisão dos resultados, é fundamental observar:

- **Auditoria de Coordenadas:** Antes de realizar atualizações de rotas em larga escala, as coordenadas dos aviários devem ser auditadas para garantir que representam o ponto exato de acesso.
- **Auditoria de Mapas:** A malha viária regional no **OpenStreetMap (OSM)** deve ser verificada constantemente.
- **Comunidade OSM:** Recomendamos fomentar uma comunidade de editores para mapear estradas rurais, garantindo a correta designação de **pavimento** e **tipo de estrada**, o que impacta diretamente na precisão do tempo e custo logístico.

## 📘 Documentação Adicional

- [**KNOWLEDGE.md**](./KNOWLEDGE.md): Detalhes técnicos, fórmulas de cálculo e arquitetura.
- [**CHANGELOG.md**](./CHANGELOG.md): Histórico de melhorias e correções.

---
*Desenvolvido para C.VALE - Cooperativa Agroindustrial*
