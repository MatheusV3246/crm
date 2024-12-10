import pandas as pd 
import flet as ft
import datetime
import re
import locale
import main
import sqlite3
from main import usuario_email
from DataConect import Anotações

 ### Conecta com o banco de dados
conn = sqlite3.connect('bd_crm.db', check_same_thread=False)

# Definir localidade para a formatação da moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Caminho do arquivo
base_associados = r"C:\Users\leonardo.yotsui\OneDrive - Sicoob\Área de Trabalho\Projetos\2. Projetos Aaa+\23. CRM\Base de Associados.csv"
base_gerente = r"C:\Users\leonardo.yotsui\OneDrive - Sicoob\Área de Trabalho\Projetos\2. Projetos Aaa+\23. CRM\Base dos Gerentes.csv"
anotacoes_df_path = 'anotacoes.csv'

# Carregar os dados do arquivo CSV
associados = pd.read_csv(base_associados, sep=';', encoding='utf-8').rename(columns={'Número CPF/CNPJ': 'CPF/CNPJ'})
gerentes = pd.read_csv(base_gerente, sep=';', encoding='utf-8')

# Converter a coluna 'Valor Saldo Final Integralizado Diário' para numérico
associados['Valor Saldo Final Integralizado Diário'] = pd.to_numeric(associados['Valor Saldo Final Integralizado Diário'], errors='coerce')
associados['CPF/CNPJ'] = associados['CPF/CNPJ'].astype(str)

# Carregar a tabela 'propensos' do banco de dados
df_combined = pd.read_sql("SELECT * FROM propensos", conn)

# Converter a coluna 'CPF/CNPJ' para string no DataFrame
df_combined['CPF/CNPJ'] = df_combined['CPF/CNPJ'].astype(str) 
  
# Unificar df_combined com a base de associados através do CPF/CNPJ para obter informações adicionais
df_combined = df_combined.merge(associados[['CPF/CNPJ', 'Data Matricula', 'Número Conta Corrente', 'Grupo Econômico', 'E-mail', 'Data Última Renovação Cadastral', 'Valor Saldo Final Integralizado Diário']], on='CPF/CNPJ', how='left')
        
# Carregar e informar base de propensos com base no gerente e origem
def carregar_propensos(gerente, origem):
    filtrados = df_combined[df_combined['Nome Gerente'] == gerente]
    if origem != "Todos":
        filtrados = filtrados[filtrados['Origem'] == origem]
    return filtrados[['Nome Cliente', 'CPF/CNPJ', 'Telefone Celular', 'Origem', 'Data Matricula', 'Número Conta Corrente', 'Grupo Econômico', 'E-mail', 'Data Última Renovação Cadastral', 'Valor Saldo Final Integralizado Diário']]

def main(page: ft.Page, usuario_email):
    print(usuario_email)
    page.clean() # Limpa a página 
    page.title = "Gestão de Relacionamentos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    page.spacing = 20

    # Estilo dos campos e botões
    gerente_nomes = gerentes[gerentes['email'] == usuario_email]['Nome Gerente'].dropna().unique().tolist()
    input_busca = ft.TextField(
        label="Digite o nome do Gerente:",
        width=400,
        border_radius=10,
        filled=True,
        border_color="blue",
        label_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
        on_change=lambda e: update_suggestions(e)
    )
    suggestions_box = ft.Column(visible=False)

    def update_suggestions(e):
        query = str(e.control.value).lower()
        suggestions = [gerente for gerente in gerente_nomes if isinstance(gerente, str) and query in gerente.lower()]
        suggestions_box.controls.clear()
        if suggestions:
            suggestions_box.visible = True
            for suggestion in suggestions:
                suggestions_box.controls.append(
                    ft.TextButton(
                        text=suggestion,
                        on_click=lambda e, s=suggestion: select_suggestion(s)
                    )
                )
        else:
            suggestions_box.visible = False
        page.update()

    def select_suggestion(suggestion):
        input_busca.value = suggestion
        suggestions_box.visible = False
        page.update()

    # Obter valores únicos da coluna 'Origem'
    valores_unicos_origem = df_combined['Origem'].dropna().unique().tolist()
    valores_unicos_origem.insert(0, "Todos")
    dropdown_origem = ft.Dropdown(
        label="Filtrar por Origem:",
        options=[ft.dropdown.Option(valor) for valor in valores_unicos_origem],
        width=400
    )

    ### Conteiners de dados e anotações
    metade_tela = page.width // 2
    resultado_container = ft.Column(spacing=10, width=700, height=400, scroll=ft.ScrollMode.ALWAYS)
    detalhes_container = ft.Column(spacing=10, width=440, height=600, scroll=ft.ScrollMode.ALWAYS)
    anotacoes_container = ft.Column(spacing=10, width=380, height=600, scroll=ft.ScrollMode.ALWAYS)

    data_hora_text = ft.TextField(
        label="Agendar data para lembrete (dd/mm/aaaa):",
        width=400,
        border_radius=10,
        filled=True,
        border_color="blue",
        label_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
        on_blur=lambda e: format_data_hora_text(e)
    )
    data_hora_text.visible = False
    data_hoje_hidden = ft.TextField(visible=False, value=datetime.datetime.now().strftime('%d/%m/%Y'))
    error_message = ft.Text(
        value="",
        color="red",
        visible=False
    )

    def format_data_hora_text(e):
        user_input = e.control.value
        formatted_date = None
        try:
            if re.match(r'^\d{2}/\d{2}/\d{4}$', user_input):
                formatted_date = datetime.datetime.strptime(user_input, '%d/%m/%Y').strftime('%d/%m/%Y')
            elif re.match(r'^\d{8}$', user_input):
                formatted_date = datetime.datetime.strptime(user_input, '%d%m%Y').strftime('%d/%m/%Y')
            if formatted_date:
                e.control.value = formatted_date
                error_message.visible = False
            else:
                raise ValueError("Formato de data inválido")
        except ValueError:
            e.control.value = ""
            error_message.value = "Data inválida. Por favor, insira no formato dd/mm/aaaa."
            error_message.visible = True
        page.update()
        
        # Botão para voltar à página inicial
    botao_voltar = ft.ElevatedButton(
        "Voltar à Página Inicial",
        on_click=lambda e: app.main_app_splash(page),
        bgcolor="#49479D",  # Cor roxo do Sicoob
        color="white"
    )
    
    switch_mostrar_sem_anotacoes = ft.Switch(
        label="Mostrar propensos sem anotações",
        value=True
    )

    def buscar_propensos(e):
        gerente = input_busca.value
        origem = dropdown_origem.value
        resultado = carregar_propensos(gerente, origem)
        mostrar_resultados(resultado)

    def mostrar_resultados(resultado):
        resultado_container.controls.clear()
        if not resultado.empty:
            # Faz a busca das anotações no banco de dados
            cpf_com_anotacoes = conn.execute('SELECT cpf_cnpj FROM anotacoes').fetchall()
            cpf_set = {row[0] for row in cpf_com_anotacoes} # Grava em uma lista os cpfs com anotações

            if switch_mostrar_sem_anotacoes.value:
                resultado = resultado[~resultado['CPF/CNPJ'].isin(cpf_set)] # mostra apenas cpfs que não estão com anotações
            else:
                resultado = resultado # mostra todos os resultados
            for _, row in resultado.iterrows(): ### _, indice ignorado, enquanto .iterrows é um metodo que itera por linhas da tabela
 
                def on_hover(e):
                    e.control.bgcolor = "lightblue" if e.data == "true" else "white"
                    e.control.update()
                
                def on_click(e, row=row):
                    detalhes_container.controls.clear()
                    anotacoes_container.controls.clear()

                    detalhes_container.controls.append(
                        ft.Text(f"Nome Cliente: {row['Nome Cliente']}", weight=ft.FontWeight.BOLD)
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"CPF/CNPJ: {row['CPF/CNPJ']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"Telefone Celular: {row['Telefone Celular']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"Abertura da Conta: {row['Data Matricula']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"Conta Corrente: {row['Número Conta Corrente']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"Grupo Econômico: {row['Grupo Econômico']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"E-mail: {row['E-mail']}")
                    )
                    detalhes_container.controls.append(
                        ft.Text(f"Data Última Renovacao Cadastral: {row['Data Última Renovação Cadastral']}")
                    )
                    # Formatar valor como moeda
                    valor_formatado = locale.currency(row['Valor Saldo Final Integralizado Diário'], grouping=True)
                    detalhes_container.controls.append(
                        ft.Text(f"Valor Saldo Final Integralizado Diário: {valor_formatado}")
                    )

                     # Adicionar informações sobre listas de propensos
                    origens_unicas = df_combined[df_combined['CPF/CNPJ'] == row['CPF/CNPJ']]['Origem'].unique().tolist()
                    detalhes_container.controls.append(
                        ft.Text(f"Listas de propensos: {', '.join(origens_unicas)}")
                    )
                    
                    # Campos para adicionar anotação
                    detalhes_container.controls.append(ft.Text("Adicionar Anotação:", size=18, weight=ft.FontWeight.BOLD, color="blue"))
                    meio_dropdown = ft.Dropdown(
                        label="Meio:",
                        options=[
                            ft.dropdown.Option("Agência"),
                            ft.dropdown.Option("Visita"),
                            ft.dropdown.Option("Ligação"),
                            ft.dropdown.Option("Whatsapp")
                        ],
                        width=400
                    )
                    oferta_dropdown = ft.Dropdown(
                        label="Oferta:",
                        options=[
                            ft.dropdown.Option("Oferta de Crédito"),
                            ft.dropdown.Option("Oferta de Produtos"),
                            ft.dropdown.Option("Cobrança"),
                            ft.dropdown.Option("Relacionamento")
                        ],
                        width=400
                    )
                    resultado_dropdown = ft.Dropdown(
                        label="Resultado:",
                        options=[
                            ft.dropdown.Option("Não tem interesse"),
                            ft.dropdown.Option("Pediu para ligar depois"),
                            ft.dropdown.Option("Aceitou oferta"),
                            ft.dropdown.Option("Agendado visita")
                        ],
                        width=400,
                        on_change=lambda e:toggle_date_text_visibility()
                    )

                    def toggle_date_text_visibility():
                        if resultado_dropdown.value in ["Pediu para ligar depois","Agendado visita"]:
                            data_hora_text.visible = True
                        else:
                            data_hora_text.visible = False
                        page.update()

                    anotacoes_field = ft.TextField(
                        label="Anotações:",
                        multiline=True,
                        width=400,
                        height=100
                    )
                    
                    def anotacao_propenso(e):
                        nova_anotacao = Anotações()
                        gerente = usuario_email
                        meio = meio_dropdown.value
                        resultado = resultado_dropdown.value
                        anotacao = anotacoes_field.value
                        oferta = oferta_dropdown.value
                        data_contato = data_hoje_hidden.value
                        data_agendada = data_hora_text.value

                        # Incluir anotação no banco de dados 
                        nova_anotacao.inserir_anotações(row['CPF/CNPJ'], row['Nome Cliente'], gerente, meio, oferta, resultado, anotacao, data_agendada, data_contato)
                        
                        # Limpar campos de anotações e fechar container
                        detalhes_container.controls.clear() # Limpa os resultados
                        anotacoes_container.controls.clear() # Limpa o container de anotações
                        page.update()
                        
                    salvar_anotacao_button = ft.ElevatedButton(
                        "Salvar Anotação",
                        on_click=lambda e: [anotacao_propenso(e), page.update()], # Chama a função de anotação. 
                        bgcolor="green",
                        color="white"
                    )

                    detalhes_container.controls.extend([
                        meio_dropdown,
                        oferta_dropdown,
                        resultado_dropdown,
                        anotacoes_field,
                        data_hora_text,
                        data_hoje_hidden,
                        error_message,
                        salvar_anotacao_button
                    ])

                    anotacoes_container.controls.append(ft.Text("Anotações", weight=ft.FontWeight.BOLD, color="blue"))
                    
                    # Buscar as anotações do CPF no banco de dados
                    anotacoes_query = '''
                        SELECT data_contato, meio, oferta, resultado, anotacao
                        FROM anotacoes
                        WHERE cpf_cnpj = ?
                    '''
                    anotacoes_result = conn.execute(anotacoes_query, (row['CPF/CNPJ'],)).fetchall()
                    
                    for anotacao in anotacoes_result:
                        data_contato, meio, oferta, resultado, anotacao_texto = anotacao
                        anotacoes_container.controls.append(
                            ft.Text(f"Data: {data_contato}, Meio: {meio}, Oferta: {oferta}, Resultado: {resultado}, Anotação: {anotacao_texto}")
                        )

                    page.update()
                

                linha_container = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(row['Nome Cliente'], width=200),
                            ft.Text(row['CPF/CNPJ'], width=150),
                            ft.Text(row['Telefone Celular'], width=150),
                            ft.Text(row.get('Origem', 'N/A'), width=100)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    bgcolor= "darkgray" if row['CPF/CNPJ'] in cpf_set  else "white",
                    border_radius=5,
                    ink=True,
                    on_hover= None if row['CPF/CNPJ'] in cpf_set else on_hover,
                    on_click=lambda e, row=row: on_click(e, row)
                )
                resultado_container.controls.append(linha_container)
        else:
            resultado_container.controls.append(
                ft.Text(
                    "Nenhum resultado encontrado.",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="red"
                )
            )
        page.update()

    buscar_button = ft.ElevatedButton(
        "Buscar Propensos",
        on_click=buscar_propensos,
        bgcolor="#00AE9D", # Turquesa do Sicoob
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

        # Layout principal
    layout = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            input_busca, botao_voltar,
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Row(
                        controls=[
                            buscar_button,
                            switch_mostrar_sem_anotacoes,
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    suggestions_box,
                    dropdown_origem,
                    resultado_container
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            detalhes_container,
            anotacoes_container
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START
    ) 

    page.add(layout)

