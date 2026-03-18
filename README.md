# Logística de Apanha - Avicultura 🚛🐔

Este projeto foi desenvolvido para otimizar a logística de transporte na avicultura, calculando rotas reais, distâncias e tempos de viagem entre um abatedouro central e diversos aviários integrados.

## 📌 Visão Geral

O sistema utiliza a API do **OSRM (Open Source Routing Machine)** para obter trajetórias reais via estradas (OpenStreetMap), superando a limitação de cálculos lineares (Haversine). Ele é capaz de processar lotes de aviários a partir de arquivos CSV e gerar relatórios detalhados individuais.

## ✨ Principais Funcionalidades

- **Cálculo de Rota Real:** Distância precisa baseada na malha viária atualizada.
- **Estimativa de Tempo:** Cálculo baseado em velocidade média configurável (padrão: 40 km/h).
- **Processamento em Lote:** Leitura automatizada de múltiplos pontos a partir de CSV.
- **Relatórios Individuais:** Para cada aviário, o sistema gera:
  - 📄 **Relatório Markdown:** Com informações gerais e roteiro passo a passo em português.
  - 🗺️ **Mapa Interativo (HTML):** Visualização dinâmica da rota usando Folium.
  - 📉 **Gráfico de Rota (PNG):** Representação estática da trajetória.
- **Logging Completo:** Rastreamento de todo o processo para auditoria e depuração.

## 🚀 Como Começar

### Pré-requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes)

### Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd calculodistanciasavicultura
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Uso

### Preparação dos Dados

O arquivo de entrada (`data/raw/aviarios.csv`) deve seguir o seguinte formato:

| aviario | nome produtor | latitude | longitude |
|---------|---------------|----------|-----------|
| 1000    | José da Silva | -24.331  | -53.858   |

### Execução

Para iniciar o processamento, execute o `main.py`:

```bash
python main.py
```

Você também pode especificar um arquivo CSV customizado:

```bash
python main.py caminho/para/seu_arquivo.csv
```

## 📁 Estrutura do Projeto

```text
├── data/
│   ├── raw/                # Dados de entrada (CSV)
│   └── processed/          # Resultados consolidados (CSV)
├── docs/
│   └── rotas_por_aviario/  # Relatórios, mapas e gráficos individuais
├── src/
│   ├── api_client.py       # Integração com a API OSRM
│   ├── logistica_aviarios.py # Lógica principal de processamento
│   ├── report_generator.py  # Geração de relatórios e mapas
│   └── utils/              # Loggers e funções auxiliares
├── tests/                  # Testes unitários
├── main.py                 # Ponto de entrada da aplicação
└── requirements.txt        # Dependências do projeto
```

## ⚙️ Configurações Técnicas

- **Abatedouro Central (Origem):** `-24.3307, -53.8581`
- **Velocidade Média de Referência:** 40 km/h
- **API de Roteamento:** [OSRM Project](http://project-osrm.org/)
- **Bibliotecas Principais:** `requests`, `folium`, `matplotlib`, `pandas` (opcional)

---
*Desenvolvido para C.VALE - Cooperativa Agroindustrial*
