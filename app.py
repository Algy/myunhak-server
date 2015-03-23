#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from tempy import Environment
from urllib import urlopen, urlencode

app = Flask(__name__)

tempy_env = Environment("tempy-templates", cache_module=False)
# tempy_env.compile_option.write_py = True 

@app.route("/", methods=["GET"])
def index():
    return str(tempy_env.module("introduction").Template())


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

@app.route("/policy", methods=["GET"])
def policy():
    return str(tempy_env.module("policy").Template())

@app.route("/photo", methods=["GET"])
def photo():
    return str(tempy_env.module("photo").Template())


@app.route("/entrance", methods=["GET"])
def entrance():
    return str(tempy_env.module("entrance").Template())


@app.route("/entrance_form", methods=["GET", "POST"])
def entrance_form():
    if request.method == "GET":
        return str(tempy_env.module("entrance_form").Template())
    else:
        z = str(request.form)
        resp = urlopen(url="https://www.google.com/recaptcha/api/siteverify",
                       data=urlencode({"secret": "6Lc92QMTAAAAALOZqZ15An9I5Jjf-f6SvEdDas5J",
                                       "response": request.form["g-recaptcha-response"]}))
        z += "<br />" + resp.read()
        z = z.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return z
@app.route("/withdrawal", methods=["GET", "POST"])
def withdrawal():
    return str(tempy_env.module("withdrawal").Template())

@app.route("/proposal", methods=["GET", "POST"])
def proposal():
    return str(tempy_env.module("proposal").Template())


@app.route("/canflaskscale", methods=["GET"])
def canflaskscale():
    return str(tempy_env.module("canflaskscale").MainTemplate())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


