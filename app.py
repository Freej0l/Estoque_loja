import streamlit as st 
import pandas as pd
import sqlite3 as sql
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from datetime import datetime

con = sql.connect("estoque.db")
cur = con.cursor()

try:
    cur.execute("""
            CREATE TABLE IF NOT EXISTS estoque(
                id INTEGER PRIMARY KEY,
                produto TEXT,
                preco REAL,
                preco_custo REAL,
                quantidade INTEGER,
                tamanho TEXT,
                fornecedor TEXT,
                valor_total REAL)
    """)
except sql.Error:
    st.error("Erro ao inicializar a tabela de estoque no banco de dados.")

try:
    cur.execute("ALTER TABLE estoque ADD COLUMN preco_custo REAL DEFAULT 0.0")
    con.commit()
except sql.OperationalError:
    pass
except sql.Error:
    pass

try:
    cur.execute("""CREATE TABLE IF NOT EXISTS vendas(
                id INTEGER PRIMARY KEY,
                produto TEXT,
                tamanho TEXT,
                quantidade_vendida INT,
                preco_praticado REAL,
                custo_da_peca REAL,
                data_venda TEXT)""")
    con.commit()
except sql.Error:
    st.error("Erro ao inicializar a tabela de vendas no banco de dados.")

try:
    cur.execute("""CREATE TABLE IF NOT EXISTS configuracoes(
                id INTEGER PRIMARY KEY,
                nome_empresa TEXT,
                meta_mensal REAL,
                margem REAL,
                email TEXT,
                frete REAL,
                tamanhos_padrao TEXT)""")
    cur.execute("INSERT OR IGNORE INTO configuracoes (id) VALUES (1)")
    con.commit()
except sql.Error:
    st.error("Erro ao inicializar a tabela de configurações no banco de dados.")

st.sidebar.header("Menu")
escolha = st.sidebar.selectbox("Menu", ["Início", "Cadastrar produto","Venda de produtos", "Financeiro", "Remover produto", "Alterar produto","Informações do estoque", "Configurações"])

if escolha == "Início":
    try:
        cur.execute("SELECT SUM(quantidade), SUM(valor_total) FROM estoque")
        dados_globais = cur.fetchone()
        total_itens = dados_globais[0] if dados_globais[0] else 0
        lucro_total = dados_globais[1] if dados_globais[1] else 0.0

        cur.execute("SELECT nome_empresa, meta_mensal FROM configuracoes WHERE id = 1")
        config_inicial = cur.fetchone()
        nome = config_inicial[0] if (config_inicial and config_inicial[0]) else 'Loja'
        meta_mensal = config_inicial[1] if (config_inicial and config_inicial[1]) else 0.0

        st.title(f"📊 Painel de Controle - Estoque")
        st.subheader(f"Bem-vindo, Administrator da {nome}")
        st.write("Aqui está o resumo em tempo real da sua empresa:")

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total de Itens", value=f"{total_itens} unid.")
        with col2:
            st.metric(label="Lucro Estimado em Estoque", value=f"R$ {lucro_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
        with col3:
            cur.execute("SELECT COUNT(*) FROM estoque WHERE quantidade = 0")
            zerados = cur.fetchone()[0]
            st.metric(label="Produtos Esgotados", value=zerados, delta="- Alerta" if zerados > 0 else None, delta_color="inverse")

        st.divider()

        st.subheader("🎯 Meta de Faturamento Mensal")
        mes_atual = datetime.now().strftime("%Y-%m")
        cur.execute("""
            SELECT SUM(quantidade_vendida * preco_praticado) 
            FROM vendas 
            WHERE data_venda LIKE ?
        """, (f"{mes_atual}%",))
        
        faturamento_realizado_tupla = cur.fetchone()
        faturamento_realizado = faturamento_realizado_tupla[0] if faturamento_realizado_tupla[0] else 0.0

        if meta_mensal > 0:
            porcentagem_concluida = min(faturamento_realizado / meta_mensal, 1.0)
            st.progress(porcentagem_concluida)
            
            faturamento_br = f"R$ {faturamento_realizado:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
            meta_br = f"R$ {meta_mensal:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
            
            st.text(f"Progresso: {porcentagem_concluida * 100:.1f}% atingido ({faturamento_br} de {meta_br})")
        else:
            st.info("💡 Nenhuma meta mensal cadastrada atualmente. Configure uma na aba 'Configurações'.")
        
        st.divider()

        tam_config = 5
        cur.execute("SELECT produto, tamanho, quantidade FROM estoque WHERE quantidade <= ?", (tam_config,))
        alertas = cur.fetchall()

        if alertas:
            st.error("⚠️ **Atenção: Os seguintes itens estão com estoque crítico (5 ou menos unidades):**")
            for item in alertas:
                st.write(f"- {item[0]} (Tamanho {item[1]}): Apenas **{item[2]}** restantes!")
        else:
            st.success("✅ Todos os produtos estão com níveis de estoque saudáveis!")
    except sql.Error as e:
        st.error(f"Erro ao carregar dados da página inicial: {e}")

elif escolha == "Cadastrar produto":
    st.subheader("Cadastrar produto")

    nome = st.text_input("Produto")
    try:
        cur.execute("SELECT nome_empresa, meta_mensal, margem, email, frete, tamanhos_padrao FROM configuracoes WHERE id = 1")
        config = cur.fetchone()
    except sql.Error:
        config = None
    
    meta = config[1] if (config and config[1] is not None) else 0.00
    margem_salva = config[2] if (config and config[2] is not None) else 50.0
    fornecedor_padrao = config[3] if (config and config[3] is not None) else ''
    frete_padrao = config[4] if (config and config[4] is not None) else 0.00

    fornecedor = st.text_input("E-mail do fornecedor", value=fornecedor_padrao)

    if config and config[5] is not None:
        st.text("Tamanhos padrões (caso queira configurar, acesse a aba 'configuração')")
        opcoes_tamanho = [x.strip() for x in config[5].split(',') if x.strip()]
        tamanhos_selecionados = st.multiselect(label="Selecione os tamanhos:", options=opcoes_tamanho)
    else:
        tamanhos_selecionados = []

    value_tamanho = ''
    tamanho_input = st.text_input(label=f"Tamanhos adicionais para o produto {nome} (Separe por vírgula ou espaço)", value=value_tamanho)
    tamanhos_separados = [t.strip() for t in tamanho_input.replace(" ", ",").split(",") if t.strip()]
    for x in tamanhos_separados:
        if x not in tamanhos_selecionados:
            tamanhos_selecionados.append(x)

    dados_por_tamanho = {}

    if tamanhos_selecionados and nome != "":
        st.write("---")
        st.markdown(f"### Preencha os detalhes para cada tamanho de **{nome}**:")
        
        for x in tamanhos_selecionados:
            st.markdown(f"#### Tamanho: **{x}**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                qtd = st.number_input(f"Quantidade ({x})", min_value=0, value=0, step=1, key=f"qtd_{x}")
            with col2:
                prc = st.number_input(f"Preço de Venda ({x})", min_value=0.00, value=0.00, step=0.01, key=f"prc_{x}")
            with col3:
                custo_produto = st.number_input(f"Preço de Custo Uni ({x})", min_value=0.00, value=0.00, step=0.01, key=f"cst_{x}")
                cst = custo_produto 
                value_custo = frete_padrao
                    
                aplicar_custo_fixo = st.checkbox(f"Somar custo fixo operacional (+ R${value_custo:.2f}) neste tamanho", key=f"check_{x}")
                if aplicar_custo_fixo:
                   cst = custo_produto + value_custo
            
            dados_por_tamanho[x] = {
                "quantidade": qtd,
                "preco": prc,
                "preco_custo": cst
            }
        st.write("---")

    if st.button("Salvar Produto"):
        if nome == "" or fornecedor == "" or not tamanhos_selecionados:
            st.error("Por favor, preencha o nome, fornecedor e pelo menos um tamanho!")
        else:
            erro_validacao = False
            tamanhos_duplicados = [] 

            for x, dados in dados_por_tamanho.items():
                if dados["quantidade"] == 0 or dados["preco"] == 0.0 or dados["preco_custo"] == 0.0:
                    st.error("Por favor, preencha a quantidade, preço e custo de todos os tamanhos listados!")
                    erro_validacao = True
                    break

                try:
                    cur.execute("SELECT COUNT(*) FROM estoque WHERE produto = ? AND tamanho = ?", (nome, x))
                    existe = cur.fetchone()[0]
                    if existe > 0:
                        tamanhos_duplicados.append(x)
                except sql.Error:
                    pass

            if not erro_validacao and tamanhos_duplicados:
                lista_tams = ", ".join(tamanhos_duplicados)
                st.warning(f"⚠️ O produto **{nome}** já possui cadastro para o(s) tamanho(s): **{lista_tams}**.")
                st.info("💡 **Sugestão:** Se você deseja atualizar as quantidades ou preços deste item, por favor, vá até a aba **'Alterar produto'** no menu lateral.")

            elif not erro_validacao:
                try:
                    for x, dados in dados_por_tamanho.items():
                        qtd = dados["quantidade"]
                        prc = dados["preco"]
                        cst = dados["preco_custo"]
                        valor_total = (prc - cst) * qtd
                        
                        comando_sql = "INSERT INTO estoque (produto, preco, preco_custo, quantidade, tamanho, fornecedor, valor_total) VALUES (?, ?, ?, ?, ?, ?, ?)"
                        cur.execute(comando_sql, (nome, prc, cst, qtd, x, fornecedor, valor_total))
                    
                    con.commit()
                    st.toast(f"Produto '{nome}' cadastrado com sucesso!", icon="✅")
                    time.sleep(2)
                    st.rerun()
                except sql.Error as e:
                    st.error(f"Erro ao salvar produto no banco de dados: {e}")

elif escolha == "Remover produto":
    try:
        cur.execute("SELECT DISTINCT produto FROM estoque")
        lista_produtos = [linha[0] for linha in cur.fetchall()]
    except sql.Error:
        lista_produtos = []
    
    if not lista_produtos:
        st.info("Nenhum produto cadastrado no estoque.")
    else:
        nome = st.selectbox("Produto", lista_produtos)
        try:
            cur.execute("SELECT tamanho FROM estoque WHERE produto = ?", (nome,))
            variacao = cur.fetchall()
        except sql.Error:
            variacao = []
        tamanho = st.multiselect("Tamanho", [linha[0] for linha in variacao])
        
        if st.button("Remover Produto"):
            if tamanho:
                try:
                    for x in tamanho:
                        cur.execute("DELETE FROM estoque WHERE produto = ? and tamanho = ?", (nome, x))
                    con.commit()
                    st.success(f"Produto '{nome}' removido com sucesso do estoque!")
                    time.sleep(2)
                    st.rerun()
                except sql.Error as e:
                    st.error(f"Erro ao remover produto do banco de dados: {e}")
            else:
                st.error("Por favor, selecione pelo menos um tamanho para remover.")

elif escolha == "Alterar produto":
        try:
            cur.execute("SELECT DISTINCT produto FROM estoque")
            lista_produtos = [linha[0] for linha in cur.fetchall()]
        except sql.Error:
            lista_produtos = []
        
        if not lista_produtos:
            st.info("Nenhum produto cadastrado para alteração.")
        else:
            nome = st.selectbox("Produtos", lista_produtos)
            try:
                cur.execute("SELECT preco, preco_custo, quantidade, tamanho, fornecedor, valor_total FROM estoque WHERE produto = ?", (nome,))
                variacao = cur.fetchall()
            except sql.Error:
                variacao = []
            df = pd.DataFrame(variacao)
            df.columns = ["Preço", "Preço de custo", "Quantidade","Tamanhos","Fornecedor","Lucro Esperado"]
            st.header(f"Informações do produto: {nome}")
            st.table(df.style.format({'Preço': '{:.2f}','Preço de custo': '{:.2f}','Lucro Esperado': '{:.2f}'}))
            
            campos_alterar = []
            valores = []

            tamanho = st.multiselect("Escolha o tamanho para alterar", df["Tamanhos"])
            choose = st.multiselect("Alterar", ["Produto","Preço", "Tamanho", "Fornecedor", "Preço de custo", "Quantidade"])
            
            if "Produto" in choose:
                novo_nome = st.text_input("Digite o novo nome")
                campos_alterar.append("produto = ?")
                valores.append(novo_nome)
            if "Preço" in choose:
                novo_preco = st.number_input("Digite o novo preço", min_value=0.00, value=0.00, step=0.01)
                campos_alterar.append("preco = ?")
                valores.append(novo_preco)
            if "Tamanho" in choose:
                novo_tamanho = st.text_input("Digite o novo tamanho")
                campos_alterar.append("tamanho = ?")
                valores.append(novo_tamanho)
            if "Fornecedor" in choose:
                novo_fornecedor = st.text_input("Digite o novo fornecedor")
                campos_alterar.append("fornecedor = ?")
                valores.append(novo_fornecedor)
            if "Preço de custo" in choose:
                novo_pc = st.number_input("Digite o novo valor que custou a unidade do produto", min_value=0.00, value=0.00, step=0.01)
                campos_alterar.append("preco_custo = ?")
                valores.append(novo_pc)
            if "Quantidade" in choose:
                nova_quantidade = st.number_input("Digite a nova quantidade", min_value=0, value=0, step=1)
                campos_alterar.append("quantidade = ?")
                valores.append(nova_quantidade)
                
            if st.button("Salvar Alteração"):
                if not choose:
                    st.error("Por favor, selecione pelo menos um campo para alterar!")
                elif not tamanho:
                    st.error("Por favor, escolha pelo menos um tamanho para aplicar a alteração!")
                else:
                    try:
                        for tam in tamanho:
                            linha_tamanho = df[df["Tamanhos"] == tam].iloc[0]
                            
                            preco_final = novo_preco if "Preço" in choose else float(linha_tamanho["Preço"])
                            qtd_final = nova_quantidade if "Quantidade" in choose else int(linha_tamanho["Quantidade"])
                            custo_final = novo_pc if "Preço de custo" in choose else float(linha_tamanho["Preço de custo"])
                            
                            valores_esse_tamanho = valores.copy()
                            campos_esse_tamanho = campos_alterar.copy()
                            
                            if "Preço" in choose or "Quantidade" in choose or "Preço de custo" in choose:
                                novo_valor_total = (preco_final - custo_final) * qtd_final
                                campos_esse_tamanho.append("valor_total = ?")
                                valores_esse_tamanho.append(novo_valor_total)
                            
                            string_campos = ", ".join(campos_esse_tamanho)
                            comando_sql = f"UPDATE estoque SET {string_campos} WHERE tamanho = ? AND produto = ?"
                            
                            valores_finais = valores_esse_tamanho + [tam, nome]
                            cur.execute(comando_sql, tuple(valores_finais))
                            
                        con.commit()
                        st.success("Estoque atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()
                    except sql.Error as e:
                        st.error(f"Erro ao atualizar o estoque no banco de dados: {e}")

elif escolha == "Informações do estoque":
    st.subheader("Informações detalhadas do estoque")

    try:
        cur.execute("SELECT produto, preco, quantidade, tamanho, valor_total FROM estoque")
        produtos_info = cur.fetchall()
    except sql.Error:
        produtos_info = []
    
    if not produtos_info:
        st.info("Nenhum produto cadastrado no estoque.")
    else:
        df_info = pd.DataFrame(produtos_info)
        df_info.columns = ['Produto', 'Preço', 'Quantidade', 'Tamanho', 'Lucro']

        ordens_de_agrupamento_info = {
            'Preço': 'first',
            'Quantidade': 'sum',
            'Lucro': 'sum'
        }

        df_info_separado = df_info.groupby(['Produto', 'Tamanho']).agg(ordens_de_agrupamento_info).reset_index()

        st.table(df_info_separado.style.format({
            'Preço': '{:.2f}',
            'Lucro': '{:.2f}'
        }))

elif escolha == "Configurações":
    st.header("Configurações do Sistema")
    st.subheader("Altere as diretrizes do seu estoque abaixo:")

    try:
        cur.execute("SELECT margem, frete, nome_empresa, email, tamanhos_padrao, meta_mensal FROM configuracoes WHERE id = 1")
        config_db = cur.fetchone()
    except sql.Error:
        config_db = None

    m_atual = int(config_db[0]) if (config_db and config_db[0] is not None) else 50
    f_atual = float(config_db[1]) if (config_db and config_db[1] is not None) else 0.00
    n_atual = config_db[2] if (config_db and config_db[2] is not None) else ""
    e_atual = config_db[3] if (config_db and config_db[3] is not None) else ""
    t_atual = config_db[4] if (config_db and config_db[4] is not None) else ""
    mt_atual = float(config_db[5]) if (config_db and config_db[5] is not None) else 0.00

    aba1, aba2, aba3, aba4 = st.tabs(["Financeiro", "Personalização", "Definições Padronizadas", "Backup"])
    
    with aba1:
        st.write("### Ajustes Financeiros")
        margem = st.slider(label="Margem de lucro padrão (%):", value=m_atual, min_value=1, max_value=100)
        custo_fixo = st.number_input("Custo operacional fixo (Ex: Marketplace, embalagem):", min_value=0.00, value=f_atual, step=0.10)

        if st.button("Salvar Ajustes Financeiros", key="btn_salvar_aba1"):
            try:
                cur.execute("UPDATE configuracoes set margem = ?, frete = ? WHERE id = 1", (margem, custo_fixo))
                con.commit()
                st.toast("Configurações financeiras salvas!")
                time.sleep(1)
                st.rerun()
            except sql.Error as e:
                st.error(f"Erro ao salvar configurações financeiras: {e}")

    with aba2:
        st.write("### Identidade da Empresa")
        nome_empresa = st.text_input("Alterar o nome da empresa", value=n_atual, placeholder="Ex: Minha Loja Store")
        st.info("Dica: O tema escuro/claro pode ser alterado pelo usuário clicando nos três pontinhos (⋮) no canto superior direito do Streamlit > Settings.")
        
        if st.button("Salvar Personalização", key="btn_salvar_aba2"):
            try:
                cur.execute("UPDATE configuracoes set nome_empresa = ? WHERE id = 1", (nome_empresa,))
                con.commit()
                st.toast("Nome da empresa atualizado!")
                time.sleep(1)
                st.rerun()
            except sql.Error as e:
                st.error(f"Erro ao salvar personalização: {e}")

    with aba3:
        st.write("### Facilitadores de Cadastro")
        fornecedor_padrao = st.text_input("Fornecedor principal (E-mail):", value=e_atual, placeholder="fornecedor@email.com")
        tamanho_padrao = st.text_input("Tamanho padrão da sua grade:", value=t_atual, placeholder="Ex: P, M, G")
        meta = st.number_input("Meta de faturamento mensal (R$):", min_value=0.00, value=mt_atual, step=100.00)
        
        if st.button("Salvar Definições Padronizadas", key="btn_salvar_aba3"):
            try:
                cur.execute("UPDATE configuracoes set email = ?, tamanhos_padrao = ?, meta_mensal = ? WHERE id = 1", (fornecedor_padrao, tamanho_padrao, meta))
                con.commit()
                st.toast("Padrões de cadastro atualizados!")
                time.sleep(1)
                st.rerun()
            except sql.Error as e:
                st.error(f"Erro ao salvar definições padronizadas: {e}")

    with aba4:
        st.write("### Segurança dos Dados")
        try:
            with open("estoque.db", "rb") as f:
                db_bytes = f.read()
            st.download_button(
                label="📥 Baixar Backup do Banco de Dados (.db)",
                data=db_bytes,
                file_name=f"backup_estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/octet-stream"
            )
        except Exception as e:
            st.error(f"Erro ao gerar arquivo de backup: {e}")

elif escolha == "Venda de produtos":
    st.subheader("Amostra do estoque")
    try:
        cur.execute("SELECT produto, preco, quantidade, tamanho FROM estoque")
        produtos = cur.fetchall()
    except sql.Error:
        produtos = []
    
    if not produtos:
        st.info("Não há itens no estoque para vender.")
    else:
        df = pd.DataFrame(produtos)
        df.columns = ['Produto', 'Preço', 'Quantidade', 'Tamanho']
        
        ordens_de_agrupamento = {
            'Preço': 'first',
            'Quantidade': 'sum',
            'Tamanho': lambda x: ', '.join(x)
        }
        df_compactado = df.groupby('Produto').agg(ordens_de_agrupamento).reset_index()
        st.table(df_compactado.style.format({'Preço': '{:.2f}'}))
        
        dicionario_tamanhos = df.groupby('Produto')['Tamanho'].apply(list).to_dict()
        prod_vendidos = st.multiselect("Escolha os produtos vendidos", df['Produto'].unique())
        
        if 'carrinho' not in st.session_state:
            st.session_state['carrinho'] = []
            
        for x in prod_vendidos:
            with st.expander(f"Tamanhos vendidos de {x}", expanded=True):
                for y in dicionario_tamanhos[x]:
                    tamanho_selecionado = st.checkbox(f"Tamanho {y}", key=f"check_{x}_{y}")
                    
                    if tamanho_selecionado:
                        linha_filtrada = df[(df['Produto'] == x) & (df['Tamanho'] == y)]
                        estoque_disponivel = int(linha_filtrada['Quantidade'].values[0])
                        
                        qtd_no_carrinho = 0
                        for item in st.session_state['carrinho']:
                            if item[0] == x and item[1] == y:
                                qtd_no_carrinho = item[2]
                                break
                                
                        estoque_limite_real = estoque_disponivel - qtd_no_carrinho
                        preco_sugerido = float(linha_filtrada['Preço'].values[0])
                        
                        if estoque_limite_real > 0:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                qtd_vendida = st.number_input(
                                    label=f"Quantidade ({y}) (Máx: {estoque_limite_real})", 
                                    min_value=1, 
                                    max_value=estoque_limite_real,
                                    key=f"qtd_{x}_{y}"
                                )
                            
                            with col2:
                                preco_venda = st.number_input(
                                    label=f"Preço praticado ({y})", 
                                    value=preco_sugerido,
                                    format="%.2f",
                                    key=f"preco_{x}_{y}"
                                )

                            if st.button("Adicionar ao carrinho", key=f"btn_add_{x}_{y}"):
                                item_encontrado = False
                                for item in st.session_state['carrinho']:
                                    if item[0] == x and item[1] == y:
                                        item[2] += qtd_vendida
                                        item[3] = preco_venda
                                        item_encontrado = True
                                        break
                                        
                                if not item_encontrado:
                                    produto_vendido = [x, y, qtd_vendida, preco_venda]
                                    st.session_state['carrinho'].append(produto_vendido)
                                
                                st.success(f"Item adicionado com sucesso!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning(f"O estoque máximo deste produto ({estoque_disponivel} un.) já está no carrinho!")

        st.divider()

        if st.session_state['carrinho']: 
            df_carrinho = pd.DataFrame(
                st.session_state['carrinho'], 
                columns=['Produto', 'Tamanho', 'Quantidade', 'Preço Praticado']
            )
            st.dataframe(df_carrinho, use_container_width=True)
            
            if st.button("Confirmar Todas as Vendas"): 
                data_atual = datetime.now().strftime("%Y-%m-%d")  
                try:
                    for item in st.session_state['carrinho']:
                        prod = item[0]
                        tam = item[1]
                        qtd = item[2]
                        prc = item[3]
                        
                        cur.execute("SELECT preco_custo FROM estoque WHERE produto = ? AND tamanho = ?", (prod, tam))
                        custo_tupla = cur.fetchone()
                        custo_atual = float(custo_tupla[0]) if (custo_tupla and custo_tupla[0]) else 0.0
                        
                        cur.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE produto = ? AND tamanho = ?", (qtd, prod, tam))
                        cur.execute("INSERT INTO vendas (produto, tamanho, quantidade_vendida, preco_praticado, custo_da_peca, data_venda) VALUES (?, ?, ?, ?, ?, ?)", (prod, tam, qtd, prc, custo_atual, data_atual))
                    
                    con.commit()
                    st.session_state['carrinho'] = []
                    st.success("Venda realizada com sucesso! Estoque e financeiro atualizados.")
                    time.sleep(1)
                    st.rerun()
                except sql.Error as e:
                    st.error(f"Erro ao processar as vendas no banco de dados: {e}")

            opcoes_remover = []
            for item in st.session_state['carrinho']:
                opcoes_remover.append(f"{item[0]} - Tam: {item[1]}")
            
            item_selecionado = st.selectbox("Selecione o que você deseja remover", opcoes_remover)
            indice_remover = opcoes_remover.index(item_selecionado)
            item_carrinho = st.session_state['carrinho'][indice_remover]
            qtd_atual = item_carrinho[2]
            
            qtd_removivel = st.number_input(f"Qual a quantidade que você deseja remover? Quantidade máxima = {qtd_atual}",
                                            min_value=1,
                                            max_value=qtd_atual,
                                            step=1)
            remover_button = st.button("Remover")
            if remover_button:
                if qtd_removivel != qtd_atual:
                    item_carrinho[2] -= qtd_removivel
                else:
                    st.session_state['carrinho'].pop(indice_remover)
                st.rerun()
        else:
            st.info("O carrinho está vazio. Adicione itens acima.")

elif escolha == 'Financeiro':
    try:
        cur.execute("SELECT * FROM vendas")
        item_vendido = cur.fetchall()
    except sql.Error as e:
        st.error(f"Erro ao acessar os dados de vendas: {e}")
        item_vendido = []
    
    if not item_vendido:
        st.info("📈 Nenhuma venda registrada ainda no sistema para gerar relatórios financeiros.")
    else:
        dados_financeiros = []
        for prod in item_vendido:
            produto = prod[1]
            tamanho = prod[2]
            quantidade = prod[3]
            preco = prod[4]
            custo = prod[5]
            
            data = prod[6][:10] if prod[6] else ""
            
            lucro_liquido = (preco - custo) * quantidade
            
            dados_financeiros.append({
                'Produto': produto,
                'Tamanho': tamanho,
                'Quantidade': quantidade,
                'Faturamento': preco * quantidade,
                'Lucro': lucro_liquido,
                'Data': data
            })
            
        df_financeiro = pd.DataFrame(dados_financeiros)

        df_financeiro['Data_DT'] = pd.to_datetime(df_financeiro['Data'], errors='coerce')
        df_financeiro['Ano'] = df_financeiro['Data_DT'].dt.year.fillna(0).astype(int)
        df_financeiro['Mês'] = df_financeiro['Data_DT'].dt.month.fillna(0).astype(int)

        metrica_escolhida = st.selectbox(
            "O que você deseja analisar?",
            ["Lucro", "Faturamento"]
        )

        col1, col2 = st.columns(2)
        with col1:
            produtos_disponiveis = df_financeiro['Produto'].unique()
            produtos_filtrados = st.multiselect("Filtrar por Produto", produtos_disponiveis)
            
        with col2:
            tamanhos_disponiveis = df_financeiro['Tamanho'].unique()
            tamanhos_filtrados = st.multiselect("Filtrar por Tamanho", tamanhos_disponiveis)

        col3, col4 = st.columns(2)
        with col3:
            anos_disponiveis = sorted(df_financeiro['Ano'].unique(), reverse=True)
            opcao_ano = st.selectbox("Filtrar por Ano", ["Todos"] + [str(a) for a in anos_disponiveis])

        with col4:
            meses_nomes = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                           7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            meses_no_df = sorted(df_financeiro['Mês'].unique())
            opcoes_meses = ["Todos"] + [meses_nomes[m] for m in meses_no_df if m in meses_nomes]
            opcao_mes = st.selectbox("Filtrar por Mês", opcoes_meses)
        df_para_grafico = df_financeiro.copy()
        
        if produtos_filtrados:
            df_para_grafico = df_para_grafico[df_para_grafico['Produto'].isin(produtos_filtrados)]
        if tamanhos_filtrados:
            df_para_grafico = df_para_grafico[df_para_grafico['Tamanho'].isin(tamanhos_filtrados)]
        
        if opcao_ano != "Todos":
            df_para_grafico = df_para_grafico[df_para_grafico['Ano'] == int(opcao_ano)]
            
        if opcao_mes != "Todos":
            num_mes_selecionado = [k for k, v in meses_nomes.items() if v == opcao_mes][0]
            df_para_grafico = df_para_grafico[df_para_grafico['Mês'] == num_mes_selecionado]

        if not df_para_grafico.empty:
            st.write(f"### Análise de {metrica_escolhida} por Produto/Tamanho")
            df_pivot = df_para_grafico.pivot_table(
                index='Produto', 
                columns='Tamanho', 
                values=metrica_escolhida, 
                aggfunc='sum'
            ).fillna(0)

            fig, ax = plt.subplots(figsize=(10, 5))
            df_pivot.plot(kind='bar', ax=ax, width=0.8)
            
            ax.set_title(f"{metrica_escolhida} por Produto e Tamanho", fontsize=14, pad=15)
            ax.set_xlabel("Produtos", fontsize=12)
            ax.set_ylabel(f"Valor (R$)", fontsize=12)
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f"R$ {x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")))
            ax.grid(axis='y', linestyle='--', alpha=0.7) 
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            st.pyplot(fig)

            total_faturamento = df_para_grafico['Faturamento'].sum()
            total_lucro = df_para_grafico['Lucro'].sum()
            col_card1, col_card2 = st.columns(2)

            with col_card1:
                st.metric(label="Faturamento Total", value=f"R$ {total_faturamento:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))

            with col_card2:
                st.metric(label="Lucro Líquido", value=f"R$ {total_lucro:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
            
            st.write("### Evolução das Vendas no Tempo")
            
            df_tempo = df_para_grafico.groupby('Data_DT')[metrica_escolhida].sum().reset_index()
            df_tempo = df_tempo.dropna(subset=['Data_DT']).sort_values('Data_DT')

            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(df_tempo['Data_DT'], df_tempo[metrica_escolhida], marker='o', color='#2ca02c', linewidth=2)
            
            ax2.set_title(f"{metrica_escolhida} Diário(a)", fontsize=14, pad=15)
            ax2.set_xlabel("Data da Venda", fontsize=12)
            ax2.set_ylabel(f"{metrica_escolhida} (R$)", fontsize=12)
            ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f"R$ {x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax2.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig2)

            st.write("### 📋 Dados Detalhados das Vendas")
            df_detalhado = df_para_grafico[['Data', 'Produto', 'Tamanho', 'Quantidade', 'Faturamento', 'Lucro']].copy()
            df_detalhado['Data'] = pd.to_datetime(df_detalhado['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
            
            st.dataframe(
                df_detalhado.style.format({
                    'Faturamento': 'R$ {:,.2f}',
                    'Lucro': 'R$ {:,.2f}'
                }),
                use_container_width=True
            )

            try:
                df_download = df_detalhado.copy()
                csv_dados = df_download.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Relatório Filtrado (CSV)",
                    data=csv_dados,
                    file_name=f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="btn_download_csv"
                )
            except Exception as e:
                st.error(f"Erro ao preparar arquivo para download: {e}")
            
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")