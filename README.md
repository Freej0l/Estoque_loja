# 📊 Sistema de Controle de Estoque e Fluxo Financeiro Inteligente

Esse projeto foi desenvolvido com o propósito inicial de ajudar comércios que enfrentam dificuldades na gestão de suas mercadorias. O sistema evoluiu de uma estrutura inicial simples para uma aplicação web robusta, automatizada e focada em inteligência de negócios, integrando controle rigoroso de estoque a análises financeiras detalhadas.

---

## 🚀 Funcionalidades Principais

* **Painel de Controle Dinâmico (Dashboard):** Visão instantânea do total de itens, lucro estimado em estoque e alertas automáticos de nível crítico de mercadorias (5 ou menos unidades).
* **Gestão de Metas Comerciais:** Barra de progresso visual que monitora e exibe o percentual atingido da meta de faturamento mensal em tempo real.
* **Grade Dinâmica de Cadastro:** Permite o cadastro customizado de preços de venda e custos por tamanho, além da opção de embutir taxas e custos operacionais fixos automaticamente.
* **Carrinho de Compras com Validação:** Módulo de vendas integrado que lê a disponibilidade do banco de dados e impede a inserção de quantidades superiores ao estoque real.
* **Módulo Financeiro Avançado:** Filtros interativos por produto, tamanho, mês e ano, acompanhados de gráficos de evolução temporal e barras para análise de faturamento e lucro líquido.
* **Localização e Padrão Brasileiro:** Toda a interface exibe valores monetários formatados em Reais (`R$`) e as datas convertidas para o formato de leitura brasileiro (`DD/MM/AAAA`).
* **Segurança e Exportação:** Sistema preventivo com botão nativo para download de backup do banco de dados (`.db`) e exportação de relatórios financeiros filtrados em formato `.CSV`.

---

## 🛠️ Tecnologias Utilizadas

* **Python** (Linguagem base do projeto)
* **Streamlit** (Construção da interface web e componentes interativos)
* **Pandas** (Modelagem, tratamento e filtragem dos dados estruturados)
* **SQLite3** (Persistência e gerenciamento do banco de dados relacional local)
* **Matplotlib** (Renderização customizada dos gráficos financeiros)

---

## 🔧 Como Executar o Projeto Localmente

1. Clone o repositório para a sua máquina:
   ```bash
   git clone https://github.com/Freej0l/Estoque_loja.git
