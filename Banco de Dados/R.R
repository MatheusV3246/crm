# Carregando o pacote
library(RSQLite)
library(DBI)

# Caminho do banco de dados
caminho_bd <- "C:\\Users\\leonardo.yotsui\\OneDrive - Sicoob\\Área de Trabalho\\Projetos\\2. Projetos Aaa+\\23. CRM\\bd_crm.db"

# Criar ou conectar ao banco
con <- dbConnect(RSQLite::SQLite(), caminho_bd)

# Listar tabelas no banco de dados 
dbListTables(con)

### Atribuindo uma tabela a um dataframe para visualização 
## nome_da_tabela <- dbReadTable(con, "nome_da_tabela")
anotacoes <- dbReadTable(con, "anotacoes")


### Excluir a tabela
## dbExecute(con, "DROP TABLE nome_da_tabela")



