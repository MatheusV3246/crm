from flask import Flask, jsonify
import multiprocessing
import flet as ft
import main

app = Flask(__name__)

def start_flet_app():
    ft.app(target=main.splash_screen, view=ft.AppView.WEB_BROWSER, port=8000)

@app.route("/")
def index():
    return jsonify({"message": "Flet app is running on port 8889"})

if __name__ == "__main__":
    flet_process = multiprocessing.Process(target=start_flet_app)
    flet_process.start()
    app.run(host="0.0.0.0", port=8010)
    flet_process.join()
