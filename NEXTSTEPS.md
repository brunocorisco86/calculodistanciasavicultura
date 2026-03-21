# Próximos Passos (Next Steps) 🚀

Lista de melhorias técnicas e funcionais priorizadas para as próximas sprints de desenvolvimento.

## 🛠️ Melhorias Técnicas
- [ ] **Barra de Progresso:** Integrar a biblioteca `tqdm` no `main.py` e `convert_to_pdf.py` para visualização em tempo real do processamento de grandes lotes.
- [ ] **Tratamento de Erros de API:** Implementar um sistema de *retries* (tentativas automáticas) com *exponential backoff* para lidar com falhas temporárias na API do OSRM.
- [ ] **Multiprocessamento:** Utilizar `concurrent.futures` para gerar PDFs e mapas em paralelo, reduzindo o tempo de processamento em máquinas multi-core.
- [ ] **Validação de CSV:** Adicionar uma camada de validação robusta para os dados de entrada (checar coordenadas inválidas, nomes vazios, etc.) antes de iniciar o roteamento.

## ✨ Novas Funcionalidades (Curto Prazo)
- [ ] **Suporte a Múltiplas Origens:** Permitir que o CSV de entrada especifique diferentes abatedouros ou pontos de partida, em vez de usar um fixo no código.
- [ ] **Filtros de Saída:** Adicionar argumentos de linha de comando para escolher quais arquivos gerar (ex: `--no-pdf` ou `--only-html`).
- [ ] **Compactação de Relatórios:** Criar um utilitário para zipar as pastas de relatórios por região ou lote de processamento.

## 🧪 Qualidade e Testes
- [ ] **Testes de Integração:** Criar testes que validem o fluxo completo desde a leitura do CSV até a existência do arquivo PDF gerado.
- [ ] **Mock da API:** Implementar mocks para as respostas do OSRM nos testes unitários para permitir execução offline.

---
*Última atualização: 21 de Março de 2026*
