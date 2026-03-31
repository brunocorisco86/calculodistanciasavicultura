# Próximos Passos (Next Steps) 🚀

Lista de melhorias técnicas e funcionais priorizadas.

## 🛠️ Melhorias Técnicas
- [ ] **Barra de Progresso:** Integrar a biblioteca `tqdm` no `main.py` e `convert_to_pdf.py` para visualização em tempo real do processamento de grandes lotes.
- [ ] **Multiprocessamento:** Utilizar `concurrent.futures` para gerar PDFs e mapas em paralelo, reduzindo o tempo de processamento em máquinas multi-core.
- [ ] **Cache de Rotas:** Implementar cache em SQLite para evitar recalcular rotas que não mudaram de coordenadas.

## ✨ Novas Funcionalidades (Curto Prazo)
- [ ] **Interface Gráfica (Web):** Criar uma versão com interface simples (Streamlit) para seleção de arquivos e pontos de partida.
- [ ] **Filtros de Saída:** Adicionar argumentos de linha de comando para escolher quais arquivos gerar (ex: `--no-pdf` ou `--only-html`).

## ✅ Concluído
- [x] **Setup do Motor Local:** Implementada a stack do **Valhalla** via Docker com setup automático.
- [x] **Suporte a Múltiplas Origens:** Implementado menu interativo e cadastro via `data/ponto_partida.json`.
- [x] **Normalização de Coordenadas:** Desenvolvida lógica para corrigir automaticamente coordenadas sem ponto decimal ou mal formatadas.
- [x] **Compactação de Relatórios:** Criado utilitário `scripts/zip_reports.py` para exportação rápida.
- [x] **Prefixação de Arquivos:** Todos os arquivos gerados agora incluem o ID do aviário no nome para facilitar buscas e organização.

---
*Última atualização: 26 de Março de 2026*
