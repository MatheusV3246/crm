import pandas as pd
import flet as ft
import datetime
import os
import main

# Caminho do arquivo de anotações
anotacoes_df_path = 'anotacoes.csv'

# Função principal
def main(page: ft.Page):
    page.clean()  # Limpar a página antes de carregar o conteúdo
    page.title = "Histórico de Contatos e Progresso"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.spacing = 20

    # Carregar o arquivo CSV de anotações
    if os.path.exists(anotacoes_df_path):
        anotacoes_df = pd.read_csv(anotacoes_df_path, sep=';', encoding='utf-8')
    else:
        anotacoes_df = pd.DataFrame()

    # Componente de seleção de data
    def mostrar_filtro_data(e):
        filtro_data.visible = True
        page.update()

    def filtrar_data(e):
        data_selecionada = filtro_data.value
        if data_selecionada:
            registros_filtrados = anotacoes_df[anotacoes_df['Data e Hora'].str.contains(data_selecionada, na=False)]
        else:
            registros_filtrados = anotacoes_df
        mostrar_resultados(registros_filtrados)

    filtro_data = ft.TextField(
        label="Filtrar por Data (dd/mm/aaaa):",
        width=300,
        border_radius=10,
        filled=True,
        border_color="blue",
        label_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
        on_submit=filtrar_data,
        visible=False
    )

    botao_mostrar_filtro = ft.ElevatedButton(
        "Filtrar por Data",
        on_click=mostrar_filtro_data,
        bgcolor="#49479D",  # Cor roxo do Sicoob
        color="white"
    )

    # Função para mostrar os resultados filtrados
    def mostrar_resultados(df):
        historico_container.controls.clear()
        if not df.empty:
            historico_container.controls.append(
                ft.Row(
                    controls=[
                        ft.Text("Nome Cliente", width=200, weight=ft.FontWeight.BOLD),
                        ft.Text("CPF/CNPJ", width=150, weight=ft.FontWeight.BOLD),
                        ft.Text("Meio", width=150, weight=ft.FontWeight.BOLD),
                        ft.Text("Resultado", width=150, weight=ft.FontWeight.BOLD),
                        ft.Text("Data e Hora", width=150, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            for _, row in df.iterrows():
                historico_container.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{row['Nome Cliente']}", width=200),
                                ft.Text(f"{row['CPF/CNPJ']}", width=150),
                                ft.Text(f"{row['Meio']}", width=150),
                                ft.Text(f"{row['Resultado']}", width=150),
                                ft.Text(f"{row['Data e Hora']}", width=150)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        border_radius=5,
                        ink=True
                    )
                )
        else:
            historico_container.controls.append(
                ft.Text("Nenhum histórico de contato encontrado.", size=16, weight=ft.FontWeight.BOLD, color="red")
            )
        page.update()

    # Filtrar registros do dia atual
    hoje = datetime.datetime.now().strftime('%d/%m/%Y')
    registros_do_dia = anotacoes_df[anotacoes_df['Data e Hora'] == hoje]

    # Meta de contatos diária
    meta_diaria = 10
    contatos_realizados = len(registros_do_dia)
    progresso = contatos_realizados / meta_diaria * 100

    # Cálculo dos resultados
    total_aceitos = len(anotacoes_df[anotacoes_df['Resultado'] == 'Aceitou oferta'])
    total_recusados = len(anotacoes_df[anotacoes_df['Resultado'] == 'Não tem interesse'])
    total_outros = len(anotacoes_df) - (total_aceitos + total_recusados)
    percentual_aceitos = (total_aceitos / len(anotacoes_df) * 100) if len(anotacoes_df) > 0 else 0

    # Componentes visuais para exibir o histórico de contatos
    historico_container = ft.Column(spacing=10, width=800, height=400, scroll=ft.ScrollMode.ALWAYS)
    mostrar_resultados(anotacoes_df)

    # Barra de progresso para a meta de contatos
    barra_progresso = ft.ProgressBar(value=progresso / 100, width=400, height=20, color="green")
    texto_progresso = ft.Text(f"Progresso da meta diária: {contatos_realizados}/{meta_diaria} contatos realizados", size=16, weight=ft.FontWeight.BOLD)

    # Dashboard prático de contagem
    dashboard_container = ft.Column(
        controls=[
            ft.Text(f"Total Aceitos: {total_aceitos}", size=14, weight=ft.FontWeight.BOLD, color="green"),
            ft.Text(f"Total Recusados: {total_recusados}", size=14, weight=ft.FontWeight.BOLD, color="red"),
            ft.Text(f"Outros: {total_outros}", size=14, weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"Percentual de Aproveitamento: {percentual_aceitos:.2f}%", size=14, weight=ft.FontWeight.BOLD, color="purple")
        ],
        spacing=5
    )

    # Mensagem de parabenização se atingiu a meta
    if contatos_realizados >= meta_diaria:
        mensagem_parabens = ft.Text(
            "Parabéns! Você atingiu sua meta de contatos diária!",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="blue"
        )
        animacao_parabens = ft.Icon(name=ft.icons.STAR, color="gold", size=40)
    else:
        mensagem_parabens = None
        animacao_parabens = None

    # Botão para voltar à página inicial
    botao_voltar = ft.ElevatedButton(
        "Voltar à Página Inicial",
        on_click=lambda e: main.main_app_splash(page),
        bgcolor="#49479D",  # Cor roxo do Sicoob
        color="white"
    )

    # Layout principal
    layout = ft.Column(
        controls=[
            botao_mostrar_filtro,
            filtro_data,
            ft.Row(
            controls=[
                botao_voltar,
                dashboard_container,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
texto_progresso,
            barra_progresso,
            mensagem_parabens if mensagem_parabens else ft.Container(),
            animacao_parabens if animacao_parabens else ft.Container(),
            ft.Divider(height=20, color="grey"),
            ft.Text("Histórico de Contatos", size=24, weight=ft.FontWeight.BOLD),
            historico_container
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(layout)

# Exemplo de uso
if __name__ == '__main__':
    ft.app(target=main)
