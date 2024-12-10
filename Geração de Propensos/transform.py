import pandas as pd
import sqlite3

# Função de importação e transformação da tabela de propensos a crédito
def import_transform(file_path, coluna_nome, coluna_cpfcnpj, coluna_situacao, coluna_tipo_atuacao, origem_name):
    # Definir o mapeamento de renomeação fixo
    columns_rename = {
        coluna_nome: 'Nome Cliente',
        coluna_cpfcnpj: 'CPF/CNPJ'
    }
    
    # Adicionar condicional para 'SITUACAO' e 'TIPO_ATUACAO'
    if coluna_situacao != 'NA':
        columns_rename[coluna_situacao] = 'Descricao'
    if coluna_tipo_atuacao != 'NA':
        columns_rename[coluna_tipo_atuacao] = 'Tipo Atuacao'
    
    # Carregar a tabela
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    
    # Selecionar e renomear as colunas conforme o mapeamento fornecido
    df_filtered = df.loc[:, list(columns_rename.keys())].rename(columns=columns_rename)

    # Garantir que a coluna 'CPF/CNPJ' esteja em formato de string
    df_filtered['CPF/CNPJ'] = df_filtered['CPF/CNPJ'].astype(str)
    
    # Criar nova coluna com o nome da origem
    df_filtered['Origem'] = origem_name
    
    # Garantir que as colunas 'Descricao' e 'Tipo Atuacao' existam no DataFrame
    if 'Descricao' not in df_filtered.columns:
        df_filtered['Descricao'] = pd.NA
    if 'Tipo Atuacao' not in df_filtered.columns:
        df_filtered['Tipo Atuacao'] = pd.NA
    
    return df_filtered

# Caminhos para os arquivos CSV
propensos_credito_pessoal_pf = r'PAD Sisbr Analitico\propensos a credito pessoal pf.csv'
propensos_credito_pessoal_pr = r'PAD Sisbr Analitico\propensos a credito pessoal pr.csv'
propensos_investimentos = r'PAD Sisbr Analitico\propensos a investimentos.csv'
base_associados = r'Base de Associados.csv'
propensos_capital_giro = r'PAD Sisbr Analitico\propensos a capital de giro.csv'
propensos_cobranca = r'PAD Sisbr Analitico\propensos a cobranca.csv'
propensos_poupanca = r'PAD Sisbr Analitico\propensos a poupanca.csv'
propensos_cartao = r'PAD Sisbr Analitico\propensos a emissao ou aumento cartao pf.csv'
propensos_aumento_investimentos = r'PAD Sisbr Analitico\propensos a aumento de investimentos.csv'
propensos_aumento_poupanca = r'PAD Sisbr Analitico\propensos a aumento de poupança.csv'
propensos_cheque_especial = r'PAD Mais Negocios\propensos a cheque especial.csv'
propensos_consorcio_auto = r'PAD Mais Negocios\propensos a consorcio auto.csv'
propensos_credito_rural = r'PAD Mais Negocios\propensos a credito rural.csv'
propensos_financiamento_auto = r'PAD Mais Negocios\propensos a financiamento auto.csv'

# Executar a função de importação e transformação para cada arquivo
credito_pessoal_pf = import_transform(propensos_credito_pessoal_pf, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'SITUACAO', 'TIPO_ATUACAO', 'Propenso à Crédito Pessoal')
credito_pessoal_pr = import_transform(propensos_credito_pessoal_pr, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'SITUACAO', 'TIPO_ATUACAO', 'Propenso à Crédito Pessoal PR')
investimentos = import_transform(propensos_investimentos, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'NA', 'NA', 'Propensos à Investimentos')
capital_giro = import_transform(propensos_capital_giro, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'NA', 'TIPO_ATUACAO', 'Propensos à Capital de Giro')
cobranca = import_transform(propensos_cobranca, 'NOME_CLIENTE', 'NR_CPF_CNPJ', 'SITUACAO', 'ACAO', 'Propensos à Cobranca')
poupanca = import_transform(propensos_poupanca, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'NA', 'NA', 'Propensos à Poupanca')
cartao = import_transform(propensos_cartao, 'CLIENTE', 'NUMERO_CPF_CNPJ', 'SITUACAO', 'ACAO_RECOMENDADA', 'Propensos ao Cartão')
aumento_investimentos = import_transform(propensos_aumento_investimentos, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'NA', 'NA', 'Propensos ao Aumento de Investimentos')
aumento_poupanca = import_transform(propensos_aumento_poupanca, 'NOME_COOPERADO', 'NR_CPF_CNPJ', 'NA', 'NA', 'Propensos ao Aumento de Poupança')
cheque_especial = import_transform(propensos_cheque_especial, 'Nome/Razão Social', 'CPFCNPJ', 'NA', 'NA', 'Propensos ao Cheque Especial')
credito_rural = import_transform(propensos_credito_rural, 'Nome/Razão Social', 'CPFCNPJ', 'NA', 'NA', 'Propensos ao Crédito Rural') 
consorcio_auto = import_transform(propensos_consorcio_auto, 'Nome/Razão Social', 'CPFCNPJ', 'NA', 'NA', 'Propensos ao Consorcio Auto')
financiamento_auto = import_transform(propensos_financiamento_auto, 'Nome/Razão Social', 'CPFCNPJ', 'NA', 'NA', 'Propensos ao Financiamento Auto')

# Concatenar os DataFrames de propensos
df_combined = pd.concat([credito_pessoal_pf, credito_pessoal_pr, investimentos, capital_giro, cobranca, poupanca, cartao, aumento_investimentos, aumento_poupanca, cheque_especial, credito_rural, consorcio_auto, financiamento_auto], ignore_index=True)

# Carregar a base de associados
associados = pd.read_csv(base_associados, sep=';', encoding='utf-8')
associados = associados.rename(columns={'Número CPF/CNPJ': 'CPF/CNPJ'})
associados['CPF/CNPJ'] = associados['CPF/CNPJ'].astype(str)

# Normalizar os valores da coluna 'CPF/CNPJ' removendo espaços em branco e garantindo consistência
df_combined['CPF/CNPJ'] = df_combined['CPF/CNPJ'].str.strip()
associados['CPF/CNPJ'] = associados['CPF/CNPJ'].str.strip()

# Unificar df_combined com a base de associados através do CPF/CNPJ e retornar Nome Gerente e Telefone Celular
df_combined = df_combined.merge(associados[['CPF/CNPJ', 'Nome Gerente', 'Telefone Celular']], on='CPF/CNPJ', how='left')

# Conectar ao banco de dados bd_crm.db
conn = sqlite3.connect('bd_crm.db')

# Inserir o DataFrame combinado no banco de dados como uma tabela chamada 'propensos'
df_combined.to_sql('propensos', conn, if_exists='replace', index=False)

# Fechar a conexão com o banco de dados
conn.close()
