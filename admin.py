import sqlite3 as sql

con = sql.connect("estoque.db")
cur = con.cursor()

cur.execute("""
        CREATE TABLE IF NOT EXISTS estoque(
            id INTEGER PRIMARY KEY,
            produto TEXT,
            preco REAL,
            quantidade INTEGER,
            tamanho TEXT,
            fornecedor TEXT,
            valor_total REAL)
""")

class Produto():
    def __init__(self, produto, preco, quantidade, tamanho, fornecedor, valor_total):
        self.produto = produto
        self.preco = preco
        self.quantidade = quantidade
        self.tamanho = tamanho
        self.fornecedor = fornecedor
        self.valor_total = valor_total

        comando_sql = "INSERT INTO estoque (produto, preco, quantidade, tamanho, fornecedor, valor_total) VALUES (?, ?, ?, ?, ?, ?)"
        cur.execute(comando_sql, (produto, preco, quantidade, tamanho, fornecedor, valor_total))
        con.commit()

    @classmethod
    def info_produto(cls):
        cur.execute("SELECT produto, preco, tamanho, quantidade, fornecedor, valor_total FROM estoque")
        produtos = cur.fetchall()
        print("\n" + "="*40)
        print("         PRODUTOS DISPONÍVEIS")
        print("="*40)

        for indice, item in enumerate(produtos, start=1):
            nome_produto = item[0]
            preco_produto = item[1]
            tamanho_produto = item[2]
            qtd_disponivel = item[3]
            fornecedor = item[4]
            valor_total = item[5]
            
            print(f"{indice}. {nome_produto.title()} | Tam: {tamanho_produto.upper()} | Qtd: {qtd_disponivel} | R$ {preco_produto:.2f} | Fornecedor: {fornecedor} | Lucro esperado: {valor_total:.2f}")
        
        print("="*40)

    @classmethod
    def cadastrar_produto(cls):
        ready = False
        while not ready:
            produto = input("Qual o produto que você deseja cadastrar? ")
            fornecedor = input(f"Qual o email do fornecedor do {produto} para a sua loja? ")
            varia = input("O tamanho é único ou varia? (unico/varia) ")
            if varia == 'unico':
                preco = float(input(f"Qual o preço do {produto}? "))
                quantidade = int(input(f"Qual a quantidade do {produto} presente no seu estoque? "))
                tamanho = input(f"Qual o tamanho do {produto} presente no seu estoque? ")
                valor_total = preco*quantidade
                Produto(produto, preco, quantidade, tamanho, fornecedor, valor_total)
                decisao = input(f"Produto {produto} adicionado ao seu estoque, deseja adicionar algo a mais? (s/n) ")
            else:
                tamanhos = input("Adicione todos os tamanhos ex: 42, 43, 44, 45 ou p, m, g , gg ")
                tamanhos_separados = [t.strip() for t in tamanhos.replace(" ", ",").split(",") if t.strip()]
                for i in tamanhos_separados:
                    preco = float(input(f"Qual o preço do {produto} no tamanho {i}? "))
                    quantidade = int(input(f"Qual a quantidade do {produto} presente no seu estoque do tamanho {i}? "))
                    valor_total = preco*quantidade
                    Produto(produto, preco, quantidade, i, fornecedor, valor_total)
                decisao = input(f"Produto {produto} adicionado ao seu estoque nos tamanhos {tamanhos_separados}, deseja adicionar algo a mais? (s/n) ")
            if decisao == 's':
                ready = False
            else:
                ready = True
        print("Tenha um ótimo dia!")

    @classmethod
    def remover_produto(cls):
        ready = False
        while not ready:
            print("="*34)
            print("=== PRODUTOS NO SEU ESTOQUE ===")
            cur.execute("SELECT DISTINCT produto FROM estoque")
            dados = cur.fetchall()
            lista_nomes = [linha[0] for row in dados for linha in [row]]
            lista_nomes = [linha[0] for linha in dados]
            
            if not lista_nomes:
                print("O estoque está completamente vazio!")
                break
                
            print(f"Produtos no estoque: {lista_nomes}")
            item = input("Qual produto você deseja remover? ")
            
            while item not in lista_nomes:
                print("Esse produto não está no seu estoque!")
                item = input("Qual produto você deseja remover? ")
            else:
                if lista_nomes.count(item) > 1:
                    cur.execute("SELECT produto, tamanho FROM estoque WHERE produto = ?", (item,))
                    valores = cur.fetchall()
                    for x in valores:
                        print(x)
                    tamanho = input("Qual o tamanho do item que você deseja remover? (se desejar remover todos escreva: todos) ")
                    if tamanho == 'todos':
                        cur.execute("DELETE FROM estoque WHERE produto = ?", (item,))
                        print(f"Item {item} de todos os tamanhos removido com sucesso !")    
                    else: 
                        next = False
                        while not next:                    
                            cur.execute("DELETE FROM estoque WHERE produto = ? AND tamanho = ?", (item, tamanho,))
                            print(f"Item {item} do tamanho {tamanho} removido com sucesso !")
                            con.commit() 
                            opa = input(f"Deseja remover mais algum outro tamanho desse item? {item} (s/n)") 
                            if opa == 's':
                                cur.execute("SELECT produto, tamanho FROM estoque WHERE produto = ?", (item,))
                                valores = cur.fetchall()
                                for y in valores:
                                    print(y)
                                tamanho = input("Qual o tamanho do item que você deseja remover? (se desejar remover todos escreva: todos)")                                
                                cur.execute("DELETE FROM estoque WHERE produto = ? AND tamanho = ?", (item, tamanho,))
                                print(f"Item {item} do tamanho {tamanho} removido com sucesso !")
                            else:
                                next = True
                else:
                    cur.execute("DELETE FROM estoque WHERE produto = ?", (item,))
                    print(f"Item {item} removido com sucesso!") 
                con.commit()  
            decisao = input("Deseja remover mais algum item? (s/n) ")
            if decisao == 's':
                ready = False
            else:
                ready = True
        print("Tenha um ótimo dia! ")

    @classmethod
    def alterar_produto(cls):
        cur.execute("SELECT DISTINCT produto FROM estoque")
        lista_tuplas = cur.fetchall()
        lista_nomes = [x[0] for x in lista_tuplas] 
        print("=== PRODUTOS NO ESTOQUE ===")
        for nome in lista_nomes:
            print(nome)   
        item = input("Qual item você deseja alterar? ")
        while item not in lista_nomes:
            print("Item não achado")
            item = input("Qual item você deseja alterar? ")   
        else:
            cur.execute("SELECT produto, preco, quantidade, tamanho, fornecedor FROM estoque WHERE produto = ?", (item,))
            af = cur.fetchall()
            for o in af:
                print(f"Produto = {o[0]} | Preço: R${o[1]:.2f} | Tamanho: {o[3]} | Quantidade: {o[2]} | Fornecedor: {o[4]}")
            
            opcoes = ['produto', 'preco', 'quantidade', 'tamanho', 'fornecedor']
            resposta = input(f"Qual opção você deseja alterar do produto {item} (nome, preco, quantidade, tamanho, fornecedor) ")
            while resposta not in opcoes:
                print("Opção não disponível, escolha uma das seguintes opções: nome, preco, quantidade, tamanho, fornecedor)")
                resposta = input(f"Qual opção você deseja alterar do produto {item} ")
            else:

                if resposta == 'nome':
                    produto = input(f"Qual o nome corrigido do produto {item}? ")
                    cur.execute("UPDATE estoque SET produto = ? WHERE produto = ?", (produto, item))
                    con.commit()
                    print(f"Nome do produto alterado com sucesso para {produto}")

                elif resposta == 'preco':
                    decisao = input("Deseja alterar o valor de um tamanho específico ou de todos? (um/todos): ").lower()
                    decisao_possivel = ['um','todos']
                    while decisao not in decisao_possivel:
                        print('Escolha entre (um) e (todos)')
                        decisao = input("Deseja alterar o valor de um tamanho específico ou de todos? (um/todos): ").lower()
                    else:
                        if decisao == 'um':
                            tamanho = input("Qual o tamanho que você quer alterar o valor? ")
                            preco = float(input(f"Qual o novo preço do {item} tamanho {tamanho}? "))
                            cur.execute("SELECT quantidade FROM estoque WHERE produto = ? AND tamanho = ?", (item, tamanho))
                            resultado = cur.fetchone()
                            
                            if resultado:
                                quantidade = resultado[0]
                                valor_total = preco * quantidade
                                cur.execute("UPDATE estoque SET preco = ?, valor_total = ? WHERE produto = ? AND tamanho = ?", 
                                            (preco, valor_total, item, tamanho))
                                con.commit()
                                print("Preço alterado com sucesso!")
                            else:
                                print("Tamanho não encontrado para este produto.")

                elif resposta == 'quantidade':
                    tamanho = input("Qual o tamanho que você quer alterar o valor? ")
                    cur.execute("SELECT preco FROM estoque WHERE produto = ? AND tamanho = ?", (item, tamanho))
                    resultado = cur.fetchone()
                    quantidade = float(input(f"Qual a quantidade correta do {item} tamanho {tamanho}? "))
                    preco = resultado[0]
                    valor_total = preco * quantidade
                    cur.execute("UPDATE estoque SET quantidade = ?, valor_total = ? WHERE produto = ? AND tamanho = ?", (quantidade, valor_total, item, tamanho))
                    con.commit()

                elif resposta == 'tamanho':
                    tamanho = input("Qual tamanho você quer alterar? ")
                    cur.execute("SELECT tamanho FROM estoque WHERE produto = ?", (item,))
                    resultado = cur.fetchone()
                    while tamanho not in resultado:
                        print("Tamanho não encontrado, selecione um valor possível!")
                        tamanho = input("Qual tamanho você quer alterar? ")
                    else:
                        for o in af:
                            v = str(o[3])
                            if tamanho == v:
                                novo = input(f"Qual valor você deseja colocar no lugar do tamanho: {tamanho} | valor novo: ")
                                cur.execute("UPDATE estoque SET tamanho = ? WHERE produto = ? AND tamanho = ?", (novo, item, tamanho))
                                print("Valor alterado com sucesso! ")
                                con.commit()
                
                elif resposta == 'fornecedor':
                    novo_fornecedor = input("Qual a alteração no email do fornecedor? ")
                    cur.execute("UPDATE estoque SET fornecedor = ? WHERE produto = ?", (novo_fornecedor, item))
                    con.commit()
                    print('A aba fornecedor já está atualizada!')






def exibir_painel():
    rodando = True
    print("Bom dia Admin!")
    print("Escolha uma das opções a seguir")
    while rodando == True:
        print("1. Cadastre seus produtos")
        print("2. Remova um dos seus produtos")
        print("3. Receba informações do seu estoque")
        print("4. Reabastecer seu estoque")
        print("5. Alterar algum produto")
        print("6. Atualizar as vendas") #começar a mexer com esse código e ver video de github para aprender a exportar
        #seu portfólio, n fique maluco tentando, dane-se vc já é, tamo together beijão pra tu, gatinho rsrs
        print("7. Configurações")
        print("8. Finalizar")
        escolha = int(input("Escolha o número recorrente ao desejável! "))
        if escolha == 1:
            Produto.cadastrar_produto()
        elif escolha == 2:
            Produto.remover_produto()
        elif escolha == 3:
            Produto.info_produto()

        elif escolha == 5:
            Produto.alterar_produto()

        elif escolha == 8:
            print("Tenha um ótimo dia")
            rodando = False
        
        else:
            while escolha > 8 or escolha < 1:
                escolha = int(input("Escolha o número recorrente ao desejável! "))
                
exibir_painel()