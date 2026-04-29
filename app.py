import json
import os
from flask import Flask, render_template

app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


@app.get("/")
def index():
    config = load_config()
    return render_template("index.html", sections=config["sections"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
