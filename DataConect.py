import sqlite3

class Anotações():
    def __init__(self):

        ### Conecta com o banco de dados
        self.conn = sqlite3.connect('bd_crm.db', check_same_thread=False)
        
        ### Para evitar erro, criei esta tabela externamente através do R 
        # Se a tabela não existir, é criada agora 
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS anotacoes (
                cpf_cnpj VARCHAR,
                cooperado VARCHAR,
                gerente VARCHAR,
                meio VARCHAR,
                oferta VARCHAR,
                resultado VARCHAR,
                anotacao VARCHAR,
                data_agendada DATE,
                data_contato DATE,
                concluido BOOLEAN
            )
        ''')
    
    def inserir_anotações(self, cpf_cnpj, cooperado, gerente, meio, produtos, resultado, anotacao, data_agendada, data_contato, concluido):
        self.conn.execute('''
            INSERT INTO anotacoes (cpf_cnpj, cooperado, gerente, meio, oferta, resultado, anotacao, data_agendada, data_contato, concluido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpf_cnpj, cooperado, gerente, meio, produtos, resultado, anotacao, data_agendada, data_contato, concluido))
        self.conn.commit()
        print("Anotação adicionada com sucesso!")
    
