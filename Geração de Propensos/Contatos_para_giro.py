import pandas as pd
import sqlite3
import math
import random

# Conectar ao banco de dados bd_crm.db
conn = sqlite3.connect("bd_crm.db")

# Carregar a planilha 'Associados - Cadastro Geral.xlsx' da pasta 'Banco de Dados'
df_combined = pd.read_excel("C:/Users/leonardo.yotsui/OneDrive - Sicoob/Área de Trabalho/Projetos/2. Projetos Aaa+/23. CRM/Banco de Dados/Associados - Cadastro Geral.xlsx")

# Criar uma coluna de telefone único
telefones = ['Telefone Celular', 'Telefone Comercial', 'Telefone Residencial']
df_combined['Telefone Único'] = df_combined[telefones].apply(lambda row: next((tel for tel in row if tel != -2), "Sem telefone registrado"), axis=1)

# Converter colunas de datas para o formato de data
colunas_data = [
    'Data Movimento', 'Data Matricula', 'Data Saída Matricula',
    'Data Última Renovacao Cadastral', 'Data Última Atualização Bem Imóvel',
    'Data Última Atualização bem Móvel', 'Data Última Atualização Renda'
]
for coluna in colunas_data:
    if coluna in df_combined.columns:
        df_combined[coluna] = pd.to_datetime(df_combined[coluna], errors='coerce')

# Inserir o DataFrame combinado no banco de dados como uma tabela chamada 'associados_cadastro_geral'
df_combined.to_sql("associados_cadastro_geral", conn, if_exists='replace', index=False)

# Ler a tabela 'associados_cadastro_geral' do banco de dados para manipulação
df_combined = pd.read_sql("SELECT * FROM associados_cadastro_geral", conn)

# Renomear a coluna 'Nome Responsável Principal' para 'Gerente'
df_combined.rename(columns={'Nome Responsável Principal': 'Gerente'}, inplace=True)

# Garantir que a coluna 'Gerente' exista
if 'Gerente' not in df_combined.columns:
    raise KeyError("Coluna 'Gerente' não encontrada na tabela 'associados_cadastro_geral'")

# Calcular o número de semanas em 90 dias
num_semanas = 90 // 7

# Selecionar a quantidade adequada de cooperados para cada gerente
cooperados_selecionados = []
for gerente in df_combined['Gerente'].unique():
    df_gerente = df_combined[df_combined['Gerente'] == gerente]
    qtd_cooperados_por_semana = math.ceil(len(df_gerente) / num_semanas)
    if len(df_gerente) > 0:
        df_gerente_sample = df_gerente.sample(n=min(qtd_cooperados_por_semana, len(df_gerente)), random_state=random.randint(1, 1000))
        cooperados_selecionados.append(df_gerente_sample)

# Concatenar os DataFrames dos cooperados selecionados
df_resultado = pd.concat(cooperados_selecionados, ignore_index=True)

# Verificar se o DataFrame final está vazio
if df_resultado.empty:
    raise ValueError("Nenhum cooperado foi selecionado para inserção no banco de dados")

# Inserir o DataFrame combinado no banco de dados como uma tabela chamada 'giro_semanal'
df_resultado.to_sql('giro_semanal', conn, if_exists='replace', index=False)

# Fechar a conexão com o banco de dados
conn.close()
