import flet as ft
import pandas as pd
import re
import datetime
import locale
import sqlite3
import main
from DataConect import Anotações
from popup import PopupHandler, SafeAreaPopup, PopupLead, AniversariantesSemana, LembretesFuturos


try:
    import locale
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass
    
def main(page: ft.Page, usuario_email, usuario_nome):
    print(f'Abrindo Giro de Carteira - Usuario: {usuario_email}, Nome: {usuario_nome}')

    page.clean()
    page.title = "Página Inicial - Gerente Comercial"
    page.scroll = None
    page.padding = 20
    page.spacing = 20
    page.theme_mode = "light"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#005522",   # Verde Sicoob
            secondary="#007d45", # Verde Secundário Sicoob
            background="#f0f0f0",
            surface="#ffffff",
            on_primary="#ffffff",
            on_secondary="#ffffff",
            on_background="#000000",
            on_surface="#000000"
        )
    )
     
    # Visualização da Carteira
    carteira_info = {
        "Quantidade de Cooperados": 150,
        "Contatos Realizados na Semana": 20,
        "Prospecções Realizadas": 10,
        "Prospecções Faltando": 5
    }

    # Criando drawer (menu lateral)
    drawer = ft.NavigationDrawer(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Sua prospecção", style="titleMedium", weight="bold", color="#005522"),
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.icons.GROUP, color="#005522", size=20),
                                        ft.Text(key, style="titleSmall", weight="bold")
                                    ], spacing=5),
                                    ft.Text(str(value), style="bodyMedium", size=20)
                                ], spacing=5),
                                padding=10,
                                border_radius=10,
                                bgcolor="#ffffff",
                                width=400,
                                alignment=ft.alignment.center_left
                            ) for key, value in carteira_info.items()
                        ],
                        spacing=10
                    ),
                    ft.ElevatedButton(icon=ft.icons.ADD_TO_HOME_SCREEN_SHARP, text="Lista de Propensos", on_click=lambda e: main.main_app_splash(page)),
                ],
                spacing=10
            )
        ]
    )

    def open_drawer(e):
        page.drawer = drawer
        drawer.open = True
        page.update()

    
    # Metas da Semana
    metas_semana = [
        "500 mil em Consórcios",
        "300 mil em Crédito Pessoal",
        "5 novos cooperados"
    ]
    
    # Campanhas Existentes
    campanhas_existentes = [
        "Campanha de Capitalização",
        "Campanha de Investimentos",
        "Campanha de Seguros"
    ]
    
    # Giro da Semana - Buscando dados diretamente do banco de dados
    conn = sqlite3.connect('bd_crm.db')
    df_giro_semana = pd.read_sql("SELECT * FROM giro_semanal", conn)
    giro_semana = df_giro_semana[['Nome.Cliente', 'Telefone_Unico', 'E.mail','Município','Grupo.Econômico']].values.tolist()
    
    ####################################### A PARTIR DAQUI COMEÇA O LAYOUT DA ESTRUTURA DA PAGINA ########################################
    
    # Header com nome do gerente
    header = ft.Row(
        controls=[
            ft.Text(f"Bem-vindo, {usuario_nome}", style= "headlineMedium", weight="bold", color="#005522"),
            ft.ElevatedButton( # Botão de Menu de Novo Lead
                icon=ft.icons.ADD_CIRCLE_ROUNDED,
                text="Novo Lead",
                on_click=lambda e: abrir_popup_novo_lead(e),                   
                ),
            ft.ElevatedButton( # Botão de Menu de Prospecção
                icon=ft.icons.MORE_HORIZ_ROUNDED,
                text="Minha prospecção",
                on_click=open_drawer,
                style=ft.ButtonStyle(
                    bgcolor="#007d45", # Verde Sicoob
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.only(left=20, right=20, top=10, bottom=10)
                )
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    # Titulo com parte onde vai estar informações de carteira
    titulo_carteira = ft.Text("Carteira - Resumo e Curiosidades", style="titleMedium", weight="bold", color="#005522")
    

    
    # Painel de expansão da lista de metas da semana e campanhas existentes
    metas_campanhas_panel = ft.ExpansionPanelList(
        expand_icon_color=ft.colors.AMBER,
        elevation=8,
        divider_color=ft.colors.AMBER,
        controls=[
            ft.ExpansionPanel(
                header=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Metas da Semana", style="titleMedium", weight="bold")
                            ]
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Campanhas Existentes", style="titleMedium", weight="bold")
                            ]
                        )
                    ],
                    spacing=50
                ),
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(name=ft.icons.CHECK_CIRCLE_OUTLINE, color="#007d45"),
                                        ft.Text(meta, style="bodyMedium")
                                    ],
                                    spacing=10,
                                ) for meta in metas_semana
                            ],
                            spacing=10,
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(name=ft.icons.CAMPAIGN, color="#007d45"),
                                        ft.Text(campanha, style="bodyMedium")
                                    ],
                                    spacing=10,
                                ) for campanha in campanhas_existentes
                            ],
                            spacing=10,
                        )
                    ],
                    spacing=50
                )
            )
        ]
    )

    # Função para chamar a classe onde está inserido os popup de anotações 
    popup_handler = PopupHandler(page, usuario_nome=usuario_nome, usuario_email=usuario_email)
    safe_area_popup = SafeAreaPopup(page)
    popup_novo_lead = PopupLead(page)
    def abrir_popup(e, row=None):
        popup_handler.abrir_nova_anotacao(e, row)
        page.update()

    def abrir_popup_resultado(e, row=None):
        popup_handler.abrir_resultado_agendamento(e, row)

    def abrir_safearea(e):
        safe_area_popup.abrir_safearea_popup(e)

    def abrir_popup_novo_lead(e):
        popup_novo_lead.abrir_novo_lead(e)

    def on_hover(e):
        e.control.bgcolor = "lightblue" if e.data == "true" else None
        e.control.update()
    
    # Classe para chamar o popup de anotação para um cooperado a parte
    class FloatingButtonExample(ft.Container):
        def __init__(self, page, on_click):
            super().__init__()
            self.page = page
            self.on_click = on_click
            self.content = ft.Column()

        def did_mount(self):
            self.page.floating_action_button = ft.FloatingActionButton(
                icon=ft.icons.ADD_COMMENT,
                bgcolor="#007d45",
                data=0,
                on_click=self.on_click,
            )
            self.page.update()

        def will_unmount(self):
            self.page.floating_action_button = None
            self.page.update()

    # Botao que chama a classe que chama a classe. Não sei porque, mas funciona
    botao_nova_anotacao = FloatingButtonExample(page, abrir_safearea)

    # Conteiner do giro
    giro_containers = []
    header_giro = ft.Row(
        controls=[
            ft.Text("Nome", style="bodyMedium", weight="bold", width=300),
            ft.Text("Telefone", style="bodyMedium", width=150),
            ft.Text("E-mail", style="bodyMedium", width=300),
            ft.Text("Cidade", style="bodyMedium", width=300),
            ft.Text("Grupo Econômico", style="bodyMedium", width=300)
        ]
    )
    giro_containers.append(header_giro)    
    for item in giro_semana[:50]:
        container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(item[0], style="bodyMedium", weight="bold", width=300),
                    ft.Text(item[1], style="bodyMedium", width=150),
                    ft.Text(item[2], style="bodyMedium", width=300),
                    ft.Text(item[3], style="bodyMedium", width=150),
                    ft.Text(item[4], style="bodyMedium", width=300)
                ],
                spacing=10
            ),
            padding=5,
            expand=True,
            on_click=lambda e, row=item: abrir_popup(e, row),
            on_hover=lambda e: on_hover(e)
        )
        giro_containers.append(container)

    # Container dos lembretes
    lembretes = LembretesFuturos('bd_crm.db')
    lembretes.carregar_dados()
    lembretes_semana = lembretes.processar_dados()
    # Criando container dos lembretes
    lembrete_containers = []

    # Cabeçalho
    header_lembrete = ft.Row(
        controls=[
            ft.Text("Data Agendada", style="bodyMedium", weight="bold", width=300),
            ft.Text("Nome", style="bodyMedium", width=400),
            ft.Text("O que ofertar?", style="bodyMedium", width=150),
            ft.Text("Anotação", style="bodyMedium", width=300)
        ]
    )
    lembrete_containers.append(header_lembrete)    
    for item in lembretes_semana:
        container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(item[0], style="bodyMedium", weight="bold", width=300),
                    ft.Text(item[1], style="bodyMedium", width=400),
                    ft.Text(item[2], style="bodyMedium", width=150),
                    ft.Text(item[3], style="bodyMedium", width=600)
                ],
                spacing=10
            ),
            padding=5,
            expand=True,
            on_click=lambda e, row=item: abrir_popup_resultado(e, row),
            on_hover=lambda e: on_hover(e)
        )
        lembrete_containers.append(container)


    # Criando conteiner dos aniversariantes
    aniversariantes = AniversariantesSemana('bd_crm.db')
    aniversariantes.carregar_dados()
    aniversariantes_semana = aniversariantes.processar_dados()

    # Criando container dos aniversariantes
    aniversariantes_containers = []

    # Cabeçalho
    header_aniversario = ft.Row(
        controls=[
            ft.Text("Nome", style="bodyMedium", weight="bold", width=300),
            ft.Text("Dia/Mês Aniversário", style="bodyMedium", width=150),
            ft.Text("Telefone", style="bodyMedium", width=150),
            ft.Text("Cidade", style="bodyMedium", width=300),
            ft.Text("Grupo Econômico", style="bodyMedium", width=300)
        ],
        spacing=10
    )
    aniversariantes_containers.append(header_aniversario)

    for item in aniversariantes_semana[:50]:
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
    
    # Container dos Leads
    leads_containers = []

    # Container de campanhas (Aqui serão alocados os propensos para alguma campanha específica, se houver)
    campanha_containers = []

    ### Tabs que levam os containers 
    tabs = ft.Tabs(
        height=500,
        selected_index=0,
        tabs=[
            ft.Tab( ### GIRO DA SEMANA
                text="Giro da Semana",
                content=ft.Column(scroll=ft.ScrollMode.ALWAYS,
                    controls=giro_containers,
                    spacing=10,
                )
            ),
            ft.Tab( ### LEMBRETES
                text="Lembretes",
                content=ft.Column(scroll=ft.ScrollMode.ALWAYS,
                    controls=lembrete_containers,
                    spacing=10,
                ),
            ),
            ft.Tab( ### ANIVERSARIANTES
                text="Aniversariantes",
                content=ft.Column(scroll=ft.ScrollMode.ALWAYS,
                    controls=aniversariantes_containers,
                    spacing=10,
                ),
            ),
            ft.Tab( ### LEADS
                text="Leads",
                content=ft.Column(scroll=ft.ScrollMode.ALWAYS,
                    controls=leads_containers,
                    spacing=10,
                ),
            ),
            ft.Tab( ### CAMPANHAS
                text="Campanhas",
                content=ft.Column(scroll=ft.ScrollMode.ALWAYS,
                    controls=campanha_containers,
                    spacing=10,
                ),
            ),
        ],
        expand=True,
    )

    layout = ft.Column(
        controls=[
            header,
            titulo_carteira,
            metas_campanhas_panel,
            botao_nova_anotacao,
            tabs,
        ],
        height=1600,
        spacing=20
    )    
    
    page.add(layout)
    page.update()

if __name__ == '__main__':
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
