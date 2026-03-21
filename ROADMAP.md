# Roadmap de Desenvolvimento 🗺️

Planejamento estratégico de longo prazo para a evolução da ferramenta de logística de apanha.

## 🟢 Fase 1: Estabilização e UX (Q2-Q3 2026)
*Foco: Melhorar a experiência do usuário e robustez do código.*
- [ ] **Interface Gráfica (GUI):** Criar uma versão com interface simples (Streamlit ou PyQt) para usuários que não usam terminal.
- [ ] **Documentação Dinâmica:** Gerar um site estático (GitHub Pages) com os relatórios consolidados e mapas agregados.
- [ ] **Tradução de Instruções:** Refinar as frases geradas pelo OSRM para termos técnicos de logística agroindustrial.

## 🟡 Fase 2: Roteamento Avançado (Q4 2026 - Q1 2027)
*Foco: Adicionar camadas de inteligência específicas para transporte pesado.*
- [ ] **Perfis de Veículos:** Implementar perfis de roteamento específicos para caminhões (Truck profile), considerando alturas de pontes e limites de peso em estradas rurais.
- [ ] **Múltiplos Destinos (Multi-stop):** Algoritmos para planejar rotas de coleta que passam por vários aviários na mesma viagem (Problema do Caixeiro Viajante).
- [ ] **Integração com Clima:** Adicionar alertas de rotas críticas em dias de chuva para estradas de terra.

## 🟠 Fase 3: Integração e Escala (2027+)
*Foco: Tornar o sistema parte do ecossistema corporativo.*
- [ ] **API Corporativa (REST):** Transformar o projeto em um microserviço para ser consumido por outros sistemas da cooperativa.
- [ ] **Dashboard Gerencial:** Visualização agregada de custos logísticos, economia de km e tempos médios de toda a frota.
- [ ] **Monitoramento em Tempo Real:** Conexão com sistemas de telemetria dos caminhões para comparar o planejado vs executado.

---
*Este planejamento é dinâmico e pode ser ajustado conforme novas demandas de negócio surgirem.*
