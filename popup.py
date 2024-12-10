import flet as ft
import pandas as pd
import datetime
import sqlite3
from DataConect import Anotações

class PopupHandler:
    def __init__(self, page, usuario_nome, usuario_email):
        self.page = page
        self.usuario_nome = usuario_nome
        self.usuario_email = usuario_email

    def abrir_nova_anotacao(self, e, row=None):
        def change_date(e):
            selected_date.value = f"Selected date: {datepicker.value}"
            self.page.update()

        datepicker = ft.DatePicker(
            first_date=datetime.datetime(2024, 12, 2),
            last_date=datetime.datetime(2026, 12, 1),
            on_change=change_date
        )
        selected_date = ft.Text()

        def open_date_picker(e):
            self.page.overlay.append(datepicker)
            datepicker.open = True
            self.page.update()

        def did_mount():
            self.page.overlay.append(datepicker)
            self.page.update()

        def will_unmount():
            self.page.overlay.remove(datepicker)
            self.page.update()

        print("Função abrir_popup chamada")
        if row:
            print(f"Abrindo popup do cooperado: {row[0]}")
            conn = sqlite3.connect("bd_crm.db")
            query = pd.read_sql(f"SELECT * FROM associados_cadastro_geral WHERE `Nome Cliente` = '{row[0]}'", conn)
            conn.close()

            date_picker_button = ft.ElevatedButton(
                "Pick date",
                icon=ft.icons.CALENDAR_MONTH,
                on_click=lambda e: open_date_picker(e),
                width=400,
                on_blur=lambda e: format_data_hora_text(e)
            )

            date_picker_button.visible = False
            def toggle_date_text_visibility():
                if dropdown_resultado.value in ["Pediu para ligar depois", "Agendado visita"]:
                    date_picker_button.visible = True
                else:
                    date_picker_button.visible = False
                self.page.update()

            dropdown_meio = ft.Dropdown(
                label="Meio:",
                options=[
                    ft.dropdown.Option("Agência"),
                    ft.dropdown.Option("Visita"),
                    ft.dropdown.Option("Ligação"),
                    ft.dropdown.Option("Whatsapp")
                ],
                width=300
            )

            dropdown_oferta = ft.Dropdown(
                label="Oferta:",
                options=[
                    ft.dropdown.Option("Oferta de Crédito"),
                    ft.dropdown.Option("Oferta de Produtos"),
                    ft.dropdown.Option("Cobrança"),
                    ft.dropdown.Option("Relacionamento")
                ],
                width=300
            )

            dropdown_resultado = ft.Dropdown(
                label="Resultado:",
                options=[
                    ft.dropdown.Option("Não tem interesse"),
                    ft.dropdown.Option("Pediu para ligar depois"),
                    ft.dropdown.Option("Aceitou oferta"),
                    ft.dropdown.Option("Agendado visita")
                ],
                width=300,
                on_change=lambda e: toggle_date_text_visibility()
            )

            anotacao_field = ft.TextField(
                label="Anotações:",
                multiline=True,
                width=400,
                height=100
            )

            def salvar_anotacao(e):
                print("Salvar anotação clicado")
                
                ### Verificação dos campos obrigatórios
                campos_obrigatorios = [
                    (self.usuario_nome, "Usuário"),
                    (dropdown_meio.value, "Meio", dropdown_meio),
                    (dropdown_oferta.value, "Oferta", dropdown_oferta),
                    (dropdown_resultado.value, "Resultado", dropdown_resultado),
                    (anotacao_field.value, "Anotação", anotacao_field)
                ]
                
                if dropdown_resultado.value in ["Pediu para ligar depois", "Agendado visita"]:
                    campos_obrigatorios.append((datepicker.value, "Data agendada", datepicker))

                campos_vazios = [campo_info for campo_info in campos_obrigatorios if not campo_info[0]]

                if campos_vazios:
                    for campo_info in campos_vazios:
                        _, _, elemento = campo_info
                        if elemento is not None:
                            elemento.border_color = "red"
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Preencha todos os campos obrigatórios", color="white"),
                        bgcolor="red"
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

                popup_dialog.open = False
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Anotação para o cooperado {row[0]} salva com sucesso", color="white"),
                    bgcolor="green"
                )
                self.page.snack_bar.open = True
                nova_anotacao = Anotações()
                usuario = self.usuario_nome
                meio = dropdown_meio.value
                oferta = dropdown_oferta.value
                resultado = dropdown_resultado.value
                anotacao_texto = anotacao_field.value
                data_agendada = datepicker.value
                data_contato = datetime.datetime.now().strftime("%Y-%m-%d")
                concluido = False if dropdown_resultado.value in ["Pediu para ligar depois", "Agendado visita"] else True

                # Incluir anotação no banco de dados
                nova_anotacao.inserir_anotações(row[0], row[1], usuario, meio, oferta, resultado, anotacao_texto, data_agendada, data_contato, concluido=concluido)

                self.page.update()

            def fechar_popup(e):
                print("Função fechar_popup chamada")
                popup_dialog.open = False
                self.page.update()

            popup_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Cooperado: {row[0]}"),
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.PHONE, size=18),
                                    ft.Text(f"{row[1]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.EMAIL, size=18),
                                    ft.Text(f"{row[2]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20  # Espaçamento entre os dois ft.Row()
                    ),
                    ## TIPO DE RENDA + RENDA + ENDEREÇO
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.MONEY, size=18),
                                    ft.Text(f"Tipo de Renda: {query['Tipo de Renda'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.ATTACH_MONEY, size=18),
                                    ft.Text(f"Renda Bruta Mensal: {query['Renda Bruta Mensal'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.HOME, size=18),
                                    ft.Text(f"Endereço: {query['Logradouro'].iloc[0]}, {query['Número Logradouro'].iloc[0]}, {query['Município'].iloc[0]}, {query['UF'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20
                    ),

                    ## IDADE + ESTADO CIVIL + GRUPO ECONOMICO
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.CAKE, size=18),
                                    ft.Text(f"Idade: {query['Idade'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.FAVORITE, size=18),
                                    ft.Text(f"Estado Civil: {query['Estado Civil'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.GROUP, size=18),
                                    ft.Text(f"Grupo Econômico: {query['Grupo Econômico'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20
                    ),

                    ## NUMERO CONTA CORRENTE + DATA MATRICULA + RISCO CRL
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.ACCOUNT_BALANCE, size=18),
                                    ft.Text(f"Número Conta Corrente: {query['Número Conta Corrente'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.CALENDAR_TODAY, size=18),
                                    ft.Text(f"Data Matrícula: {query['Data Matricula'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.WARNING, size=18),
                                    ft.Text(f"Risco CRL: {query['Risco CRL'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20
                    ),

                    ## ESCOLARIDADE + PROFISSAO + CNAE
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.SCHOOL, size=18),
                                    ft.Text(f"Escolaridade: {query['Escolaridade'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.WORK, size=18),
                                    ft.Text(f"Profissão: {query['Profissão'].iloc[0]}", expand=True)
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20
                    ),

                    ft.Row(
                        [
                            ft.Icon(ft.icons.LIST, size=18),
                            ft.Text(f"Listas de propensos: {', '.join(pd.read_sql('SELECT * FROM propensos', sqlite3.connect('bd_crm.db'))[pd.read_sql('SELECT * FROM propensos', sqlite3.connect('bd_crm.db'))['Nome Cliente'] == row[0]]['Origem'].unique().tolist())}", expand=True)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text("Adicionar Anotação:", size=12, weight=ft.FontWeight.BOLD, color="blue"),
                    dropdown_meio,
                    dropdown_oferta,
                    dropdown_resultado,
                    date_picker_button,
                    anotacao_field
                ],
                alignment=ft.MainAxisAlignment.CENTER),
                actions=[
                    ft.TextButton("Salvar", on_click=salvar_anotacao),
                    ft.TextButton("Fechar", on_click=fechar_popup)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )



        self.page.dialog = popup_dialog
        popup_dialog.open = True
        self.page.update()

    def abrir_resultado_agendamento(self, e, row=None):
        def change_date(e):
            selected_date.value = f"Selected date: {datepicker.value}"
            self.page.update()

        datepicker = ft.DatePicker(
            first_date=datetime.datetime(2024, 12, 2),
            last_date=datetime.datetime(2026, 12, 1),
            on_change=change_date
        )
        selected_date = ft.Text()

        def open_date_picker(e):
            self.page.overlay.append(datepicker)
            datepicker.open = True
            self.page.update()

        def did_mount():
            self.page.overlay.append(datepicker)
            self.page.update()

        def will_unmount():
            self.page.overlay.remove(datepicker)
            self.page.update()

        print("Função de abrir_resultado_agendamento chamada")
        if row:
            print(f"Abrindo resultado de agendamento do : {row[0]}")
            date_picker_button = ft.ElevatedButton(
                "Data de reagendamento",
                icon=ft.icons.CALENDAR_MONTH,
                on_click=lambda e: open_date_picker(e),
                width=400,
                on_blur=lambda e: format_data_hora_text(e)
            )           
            date_picker_button.visible = False
            def toggle_date_text_visibility():
                if dropdown_resultado.value in ["Pediu para ligar depois", "Agendado visita"]:
                    date_picker_button.visible = True
                else:
                    date_picker_button.visible = False
                self.page.update()

            dropdown_meio = ft.Dropdown(
                label="Meio:",
                options=[
                    ft.dropdown.Option("Agência"),
                    ft.dropdown.Option("Visita"),
                    ft.dropdown.Option("Ligação"),
                    ft.dropdown.Option("Whatsapp")
                ],
                width=300
            )

            dropdown_oferta = ft.Dropdown(
                label="Oferta:",
                options=[
                    ft.dropdown.Option("Oferta de Crédito"),
                    ft.dropdown.Option("Oferta de Produtos"),
                    ft.dropdown.Option("Cobrança"),
                    ft.dropdown.Option("Relacionamento")
                ],
                width=300
            )

            dropdown_resultado = ft.Dropdown(
                label="Resultado:",
                options=[
                    ft.dropdown.Option("Não tem interesse"),
                    ft.dropdown.Option("Pediu para ligar depois"),
                    ft.dropdown.Option("Aceitou oferta"),
                    ft.dropdown.Option("Reagendado a visita")
                ],
                width=300,
                on_change=lambda e: toggle_date_text_visibility()
            )

            anotacao_field = ft.TextField(
                label="Anotações:",
                multiline=True,
                width=400,
                height=100
            )

            def salvar_anotacao(e):
                print("Salvar anotação clicado")
                popup_dialog.open = False
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Anotação para o cooperado {row[0]} salva com sucesso", color="white"),
                    bgcolor="green"
                )
                self.page.snack_bar.open = True
                self.page.update()

            def fechar_popup(e):
                print("Função fechar_popup chamada")
                popup_dialog.open = False
                self.page.update()

            popup_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f" Como foi a visita/ligação com o cooperado: {row[0]}"),
                content=ft.Column([
                    ft.Text(f"Telefone: {row[1]}"),
                    ft.Text(f"Data de útimo contato: INSERIR DATA DE ULTIMO CONTATO"),
                    ft.Text(f"Descrição: {row[3]}"),
                    dropdown_meio,
                    dropdown_oferta,
                    dropdown_resultado,
                    date_picker_button,
                    anotacao_field,
                ],
                alignment=ft.MainAxisAlignment.CENTER),
                actions=[
                    ft.TextButton("Salvar", on_click=salvar_anotacao),
                    ft.TextButton("Fechar", on_click=fechar_popup)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

        self.page.dialog = popup_dialog
        popup_dialog.open = True
        self.page.update()

class SafeAreaPopup:
    def __init__(self, page):
        self.page = page

    def abrir_safearea_popup(self, e):
        def change_date(e):
            selected_date.value = f"Selected date: {datepicker.value}"
            self.page.update()
        
        datepicker = ft.DatePicker(
            first_date=datetime.datetime(2024, 12, 2),
            last_date=datetime.datetime(2026, 12, 1),
            on_change=change_date
        )
        selected_date = ft.Text()

        def open_date_picker(e):
            self.page.overlay.append(datepicker)
            datepicker.open = True
            self.page.update()

        def did_mount():
            self.page.overlay.append(datepicker)
            self.page.update()

        def will_unmount():
            self.page.overlay.remove(datepicker)
            self.page.update()

        print("Função de abrir_resultado_agendamento chamada")

        cpf_cnpj_field = ft.TextField(
            label="CPF/CNPJ",
            width=300
        )

        nome_field = ft.TextField(
            label="Nome",
            width=300
        )

        dropdown_meio = ft.Dropdown(
            label="Meio:",
            options=[
                ft.dropdown.Option("Agência"),
                ft.dropdown.Option("Visita"),
                ft.dropdown.Option("Ligação"),
                ft.dropdown.Option("Whatsapp")
            ],
            width=300
        )

        dropdown_oferta = ft.Dropdown(
            label="Oferta:",
            options=[
                ft.dropdown.Option("Oferta de Crédito"),
                ft.dropdown.Option("Oferta de Produtos"),
                ft.dropdown.Option("Cobrança"),
                ft.dropdown.Option("Relacionamento")
            ],
            width=300
        )

        dropdown_resultado = ft.Dropdown(
            label="Resultado:",
            options=[
                ft.dropdown.Option(" Não tem interesse"),
                ft.dropdown.Option("Pediu para ligar depois"),
                ft.dropdown.Option("Aceitou oferta"),
                ft.dropdown.Option("Reagendado a visita")
            ],
            width=300,
            on_change=lambda e: toggle_date_text_visibility()
        )

        anotacao = ft.TextField(
            label="Anotações:",
            multiline=True,
            width=400,
            height=100
        )

        def salvar_anotacao(e):
            print("Salvar anotação clicado")
            popup_dialog.open = False
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Anotação para o cooperado {row[0]} salva com sucesso", color="white"),
                bgcolor="green"
            )
            self.page.snack_bar.open = True
            self.page.update()

        def fechar_popup(e):
            print("Função fechar_popup chamada")
            popup_dialog.open = False
            self.page.update()

        popup_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f" Como foi seu contato?"),
            content=ft.Container(
                content=ft.Column([
                    cpf_cnpj_field,
                    nome_field,
                    dropdown_meio,
                    dropdown_oferta,
                    dropdown_resultado,
                    datepicker,
                    anotacao
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                width=600
                )),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_anotacao),
                ft.TextButton("Fechar", on_click=fechar_popup)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = popup_dialog
        popup_dialog.open = True
        self.page.update()

class PopupLead:
    def __init__(self, page):
        self.page = page

    def abrir_novo_lead(self, e):
        print("Função de abrir_novo_lead chamada")

        nome = ft.TextField(
            label="Nome",
            width=300,
            prefix_icon=ft.icons.PERSON
        )
        
        cpf_cnpj = ft.TextField(
            label="CPF/CNPJ",
            width=300,
            prefix_icon=ft.icons.BADGE
        )

        telefone = ft.TextField(
            label="Telefone",
            width=300,
            prefix_icon=ft.icons.PHONE
        )

        email = ft.TextField(
            label="Email",
            width=300,
            prefix_icon=ft.icons.EMAIL
        )

        estadocivil = ft.TextField(
            label="Estado Civil",
            width=300,
            prefix_icon=ft.icons.FAVORITE
        )

        profissao = ft.TextField(
            label="Profissão",
            width=300,
            prefix_icon=ft.icons.WORK
        )

        NomeConjuge = ft.TextField(
            label="Nome do Conjuge",
            width=300,
            prefix_icon=ft.icons.PEOPLE
        )

        endereco = ft.TextField(
            label="Endereço",    
            width=300,
            prefix_icon=ft.icons.HOME
        )

        renda_mensal = ft.TextField(
            label="Renda Mensal",
            width=300,
            prefix_icon=ft.icons.MONEY
        )

        indicado = ft.TextField(
            label="Indicado",
            width=300,
            prefix_icon=ft.icons.PERSON_ADD
        )

        dropdown_fonte = ft.Dropdown(
            label="Fonte:",
            options=[
                ft.dropdown.Option("Indicação"),
                ft.dropdown.Option("Lista Fria"),
                ft.dropdown.Option("Rede de Amigos"),
                ft.dropdown.Option("Familiar"),
                ft.dropdown.Option("Indicação de amigos/familia"),
                ft.dropdown.Option("Redes Sociais")
            ],
            width=300
        )

        anotacao = ft.TextField(
            label="Anotações:",
            multiline=True,
            width=400,
            height=100
        )

        def salvar_anotacao(e):
            print("Salvar anotação clicado")
            popup_dialog.open = False
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Anotação para o cooperado {row[0]} salva com sucesso", color="white"),
                bgcolor="green"
            )
            self.page.snack_bar.open = True
            self.page.update()

        def fechar_popup(e):
            print("Função fechar_popup chamada")
            popup_dialog.open = False
            self.page.update()

        popup_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f" Como foi seu contato?"),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([nome, cpf_cnpj]),
                    ft.Row([telefone, email]),
                    ft.Row([estadocivil, NomeConjuge]),
                    ft.Row([profissao, renda_mensal]),
                    endereco,
                    ft.Row([dropdown_fonte, indicado]),
                    anotacao
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                width=600
                )),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_anotacao),
                ft.TextButton("Fechar", on_click=fechar_popup)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = popup_dialog
        popup_dialog.open = True
        self.page.update()

class AniversariantesSemana:
    def __init__(self, db_path):
        self.db_path = db_path
        self.df_aniversariantes_semana = None
        self.aniversariantes_semana = []

    def carregar_dados(self):
        # Conectar ao banco de dados e carregar os dados
        conn = sqlite3.connect(self.db_path)
        self.df_aniversariantes_semana = pd.read_sql("SELECT * FROM associados_cadastro_geral", conn)
        conn.close()

    def processar_dados(self):
        # Converter a coluna 'Data Nascimento' para o formato de data legível
        self.df_aniversariantes_semana['Data Nascimento'] = pd.to_datetime(self.df_aniversariantes_semana['Data Nascimento'], unit='s')

        # Obtendo data da segunda-feira da semana atual
        hoje = datetime.datetime.today()
        inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + datetime.timedelta(days=6)

        # Criar colunas auxiliares para dia e mês, ignorando o ano
        self.df_aniversariantes_semana['Dia'] = self.df_aniversariantes_semana['Data Nascimento'].dt.day
        self.df_aniversariantes_semana['Mês'] = self.df_aniversariantes_semana['Data Nascimento'].dt.month

        # Filtrar os aniversariantes da semana e remover os com 'Estado Civil' como 'NÃO SE APLICA'
        self.df_aniversariantes_semana = self.df_aniversariantes_semana[
            (self.df_aniversariantes_semana['Data Nascimento'].dt.month == inicio_semana.month) &
            (self.df_aniversariantes_semana['Data Nascimento'].dt.day >= inicio_semana.day) &
            (self.df_aniversariantes_semana['Data Nascimento'].dt.day <= fim_semana.day) &
            (self.df_aniversariantes_semana['Estado Civil'] != 'NÃO SE APLICA')
        ]

        # Ordenar o DataFrame por mês e dia
        self.df_aniversariantes_semana = self.df_aniversariantes_semana.sort_values(by=['Mês', 'Dia'])

        # Criar uma coluna 'Data Nascimento Formatada' para mostrar apenas DD/MM
        self.df_aniversariantes_semana['Data Nascimento Formatada'] = self.df_aniversariantes_semana['Data Nascimento'].dt.strftime('%d/%m')

        # Puxando os aniversariantes da semana numa lista
        self.aniversariantes_semana = self.df_aniversariantes_semana[['Nome Cliente', 'Data Nascimento Formatada', 'Telefone_Unico', 'Município', 'Grupo Econômico']].values.tolist()

        return self.aniversariantes_semana
    def get_aniversariantes_containers(self):
        # Criando conteiner dos aniversariantes
        aniversariantes_containers = []
        for item in self.aniversariantes_semana:
            container = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(item[0], style="bodyMedium", weight="bold", width=300),
                        ft.Text(item[1], style="bodyMedium", width=150),
                        ft.Text(item[2], style="bodyMedium", width=150),
                        ft.Text(item[3], style="bodyMedium", width=300),
                        ft.Text(item[4], style="bodyMedium", width=300)
                    ],
                    spacing=10
                ),
                padding=5,
                expand=True,
                on_click=lambda e, row=item: abrir_popup(e, row),
                on_hover=lambda e: on_hover(e)
            )
            aniversariantes_containers.append(container)
        return aniversariantes_containers

class LembretesFuturos:
    def __init__(self, db_path):
        self.db_path = db_path
        self.df_lembretes = None
        self.lembretes = []

    def carregar_dados(self):
        # Conectar ao banco de dados e carregar os dados
        conn = sqlite3.connect(self.db_path)
        self.df_lembretes = pd.read_sql("SELECT * FROM anotacoes WHERE concluido = 0", conn)
        conn.close()

    def processar_dados(self):
        # Converter a coluna 'Data Nascimento' para o formato de data legível
        self.df_lembretes['data_agendada'] = pd.to_datetime(self.df_lembretes['data_agendada'])
        self.df_lembretes['data_contato'] = pd.to_datetime(self.df_lembretes['data_contato'])


        # Criar colunas auxiliares para dia e mês, ignorando o ano
        self.df_lembretes['Dia'] = self.lembretes['data_agendada'].dt.day
        self.df_lembretes['Mês'] = self.lembretes['data_agendada'].dt.month

        # Ordenar o DataFrame por mês e dia
        self.df_lembretes = self.df_lembretes.sort_values(by=['Mês', 'Dia'])

        # Criar uma coluna 'Data Nascimento Formatada' para mostrar apenas DD/MM
        self.df_lembretes['Data Agendada Formatada'] = self.df_['data_agendada'].dt.strftime('%d/%m')

        # Puxando os aniversariantes da semana numa lista
        self.lembretes = self.df_lembretes[['Data Agendada Formatada', 'Nome Cliente', 'oferta', 'anotacao']].values.tolist()

        return self.lembretes
    def get_lembretes_containers(self):
        # Criando conteiner dos aniversariantes
        lembretes_containers = []
        for item in self.lembretes:
            container = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(item[0], style="bodyMedium", weight="bold", width=150),
                        ft.Text(item[1], style="bodyMedium", width=250),
                        ft.Text(item[2], style="bodyMedium", width=150),
                        ft.Text(item[3], style="bodyMedium", width=300),
                    ],
                    spacing=10
                ),
                padding=5,
                expand=True,
                on_click=lambda e, row=item: abrir_resultado_agendamento(e, row),
                on_hover=lambda e: on_hover(e)
            )
            aniversariantes_containers.append(container)
        return aniversariantes_containers

