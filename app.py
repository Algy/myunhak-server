#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from tempy import Environment

app = Flask(__name__)

tempy_env = Environment("tempy-templates", cache_module=False)

@app.route("/introduction", methods=["GET"])
def index():
    return str(tempy_env.module("introduction").Template())


if __name__ == "__main__":
    app.run(port=8192, debug=True)


