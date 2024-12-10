import flet as ft
import time
import hashlib
import sqlite3
#import propensos
import Acompanhamento
import giro

usuario_email = ""
usuario_nome = ""

# Função para exibir a tela de splash
def splash_screen(page: ft.Page):
    page.clean()  # Limpa a tela antes de exibir a splash
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    logo = ft.Image(
        src='assets/Selo - Desenvolvimento de Produtos.png',  # Substitua pela URL ou caminho da sua logo
        width=400,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )
    texto_carregando = ft.Text("Carregando seu Aplicativo", size=24, weight=ft.FontWeight.BOLD)
    
    # AnimatedSwitcher para criar uma animação de transição
    switcher = ft.AnimatedSwitcher(
        content=ft.Column(
            [
                logo,
                texto_carregando,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=2000,  # Duração da animação em milissegundos
    )
    
    page.add(switcher)
    page.update()
    time.sleep(2)  # Simula um tempo de carregamento de 2 segundos
    login_screen(page)  # Depois, chama a função que inicializa o app principal

# Função para exibir a tela de login
def login_screen(page: ft.Page):
    page.clean()  # Limpa a tela antes de exibir a tela de login
    page.title = "Login - Gestão de Relacionamentos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    titulo_login = ft.Text("Bem-vindo ao Sistema de Gestão de Relacionamentos", size=24, weight=ft.FontWeight.BOLD)
    campo_usuario = ft.TextField(label="Usuário", width=300)
    campo_senha = ft.TextField(label="Senha", width=300, password=True)

    def validar_login(e):
        #Y:/BI/BD/SAM/bd_users.db
        conn = sqlite3.connect(r'bd_crm.db', check_same_thread=False)
        senha_hash = hashlib.sha256(campo_senha.value.encode()).hexdigest()
        result = conn.execute('SELECT senha_hash, nome, email FROM usuarios WHERE email = ?', (campo_usuario.value,)).fetchone()
        if result and result[0] == senha_hash:
            global usuario_nome  
            usuario_nome = result[1] # Aqui, para simplificação, estou usando a senha diretamente, mas idealmente, deve-se comparar o hash da senha
            global usuario_email  # Declara a variável como global
            usuario_email = result[2]
            page.clean()
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
            texto_carregando = ft.Text(f'Bem vindo ao Gestão de Relacionamentos, {usuario_nome}', size=24, weight=ft.FontWeight.BOLD)
            switcher = ft.AnimatedSwitcher(
                content=texto_carregando,
                transition=ft.AnimatedSwitcherTransition.SCALE,
                duration=2000,  # Duração da animação em milissegundos
            )
            page.add(switcher)
            page.update()
            time.sleep(2)  # Simula um tempo de transição de 1 segundo
            main_app_splash(page)
        else:
            mensagem_erro.value = "Usuário ou senha incorretos. Tente novamente."
            page.update()

    botao_login = ft.ElevatedButton(
        "Entrar",
        on_click=validar_login,
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    mensagem_erro = ft.Text(size=14, weight=ft.FontWeight.BOLD, color="red")

    page.add(
        ft.Column(
            controls=[titulo_login, campo_usuario, campo_senha, botao_login, mensagem_erro],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()

# Função para exibir a tela principal do aplicativo
def main_app_splash(page: ft.Page):
    page.clean()  # Limpa a tela da splash screen
    page.title = "Gestão de Relacionamentos"
    page.favicon = 'Selo - Desenvolvimento de Produtos.png'  # Substitua pela URL ou caminho do favicon
    page.theme_mode = ft.ThemeMode.LIGHT  # Define o modo do tema
    page.theme = ft.Theme()
    page.theme.color_scheme_seed = ft.colors.BLUE
    page.background_color = ft.colors.LIGHT_BLUE_ACCENT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    logo = ft.Image(
        src='Selo - Desenvolvimento de Produtos.png',  # Substitua pela URL ou caminho da sua logo
        width=200,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )
    titulo = ft.Text("Bem-vindo ao Gestão de Relacionamentos Credseguro", size=32, weight=ft.FontWeight.BOLD)
    
    botao_giro = ft.ElevatedButton(
        "Giro de Carteira",
        on_click=lambda e: [print(f'Usuario: {usuario_email}, Nome: {usuario_nome}'), giro.main(page, usuario_email, usuario_nome)],
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    botao_inicio_crm = ft.ElevatedButton(
        "Propensos",
        on_click=lambda e: propensos.main(page, usuario_email),
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    botao_historico_contatos = ft.ElevatedButton(
        "Ver Histórico de Contatos",
        on_click=lambda e: Acompanhamento.main(page),
        bgcolor="green",
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    botao_logout = ft.ElevatedButton(
        "Logout",
        on_click=lambda e: login_screen(page),
        bgcolor="red",
        color="white",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    
    copyright = ft.Text(
        "Desenvolvido por Leonardo Rodrigues Yotsui", 
        size=12, 
        weight=ft.FontWeight.NORMAL, 
        color=ft.colors.BLACK
    )
    
    page.add(
        ft.Column(
            controls=[logo, titulo, botao_giro,botao_inicio_crm, botao_historico_contatos, botao_logout, copyright],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()