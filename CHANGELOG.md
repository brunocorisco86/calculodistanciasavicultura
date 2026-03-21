# Registro de Alterações (Changelog) 📜

Este documento registra todas as alterações notáveis feitas neste projeto.

## [1.2.0] - 2026-03-21
### ✨ Adicionado
- **Geração de PDF nativa:** Integração da biblioteca `fpdf2` para gerar relatórios profissionais consolidados.
- **Hyperlinks Interativos:** Adição de links clicáveis nos PDFs que abrem o mapa interativo HTML diretamente no navegador.
- **Script de Conversão em Massa:** Novo utilitário `src/convert_to_pdf.py` para converter relatórios Markdown existentes para PDF.
- **Base de Conhecimento:** Criação do `KNOWLEDGE.md` com detalhes técnicos da operação logística.

### ⚙️ Alterado
- **Refatoração do ReportGenerator:** O gerador de relatórios agora cria MD, HTML, PNG e PDF em uma única passagem.
- **Aprimoramento do README:** Documentação completamente reformulada para refletir as novas capacidades do sistema.
- **Atualização de Dependências:** Adição de `fpdf2` ao ambiente do projeto.

## [1.1.0] - 2026-03-20
### ✨ Adicionado
- **Mapas Interativos:** Implementação de mapas Folium (HTML) para visualização dinâmica das rotas.
- **Gráficos Estáticos:** Inclusão de plots Matplotlib (PNG) para visualização rápida da trajetória.
- **Roteiro Passo a Passo:** Geração de instruções textuais (ex: "vire à esquerda na rua sem nome") baseadas na API OSRM.

### ⚙️ Alterado
- **Cálculo de Distância:** Substituição do cálculo Haversine por distâncias reais da malha viária.

## [1.0.0] - Versão Inicial
- **Core Logistics:** Leitura de CSV e consulta básica à API OSRM.
- **Exportação Básica:** Geração de relatórios consolidados em CSV na pasta `data/processed/`.
- **Logger:** Sistema de logs para monitoramento de execuções.

---
*Manutenido pela equipe técnica de logística - C.VALE*
