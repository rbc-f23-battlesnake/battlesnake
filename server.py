import typing

from flask import Flask
from flask import request
from waitress import serve

import os

def run_server(handlers: typing.Dict):

    app = Flask("Battlesnake")

    @app.get("/")
    def on_info():
        return handlers["info"]()

    @app.post("/start")
    def on_start():
        game_state = request.get_json()
        handlers["start"](game_state)
        return "ok"

    @app.post("/move")
    def on_move():
        game_state = request.get_json()
        print("-------------------------------------")
        return handlers["move"](game_state)

    @app.post("/end")
    def on_end():
        game_state = request.get_json()
        handlers["end"](game_state)
        return "ok"

    @app.after_request
    def identify_server(response):
        response.headers.set(
            "server", "battlesnake/github/starter-snake-python"
        )
        return response
    port = int(os.environ["PORT"]) if "PORT" in os.environ else 8000
    print(f"Starting Server on Port {port}")
    serve(app, port=port)
    
    
