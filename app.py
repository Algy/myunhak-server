#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from tempy import Environment

app = Flask(__name__)

tempy_env = Environment("tempy-templates", cache_module=False)
tempy_env.compile_option.write_py = True 

@app.route("/", methods=["GET"])
def index():
    return str(tempy_env.module("index").Template())


@app.route("/introduction", methods=["GET"])
def introduction():
    from time import time
    st = time()

    s1 = time()
    t = tempy_env.module("introduction")
    e1 = time()
    s2 = time()
    temp = t.Template()
    e2 = time()
    s3 = time()
    result = str(temp)
    e3 = time()
    ed = time()
    print "Elapsed time: ", "%.2f"%((ed - st)*1000), "(ms)"
    print "  module import: " , "%.2f"%((e1 - s1)*1000), "(ms)"
    print "  runing template: ", "%.2f"%((e2 - s2)*1000), "(ms)"
    print "  stringify: ", "%.2f"%((e3 - s3)*1000), "(ms)"
    return result

@app.route("/entrance", methods=["GET"])
def entrance():
    return str(tempy_env.module("entrance").Template())

@app.route("/entrance_form", methods=["GET"])
def entrance_form():
    return str(tempy_env.module("entrance_form").Template())

@app.route("/canflaskscale", methods=["GET"])
def canflaskscale():
    return str(tempy_env.module("canflaskscale").MainTemplate())

if __name__ == "__main__":
    app.run(port=8192, debug=True)


