#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json

from functools import wraps
from flask import Flask, render_template, request, jsonify
from tempy import Environment 
from urllib import urlopen, urlencode

from pymongo import MongoClient
from db import DBCommonData

app = Flask(__name__)
app.config.from_object('config')


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

def with_common_data(fun):
    @wraps(fun)
    def inner(*args, **kwds):
        with MongoClient(host=app.config["DB_HOST"], 
                         port=app.config["DB_PORT"]) as client:
            dbname = app.config["DB_NAME"]
            db = client[dbname]
            data = DBCommonData(db)
            return fun(data=data, *args, **kwds)
    return inner


@with_common_data
def add_entrance_data(kwds, data):
    data.paged_entrance_data.add([kwds])


def rest_error_response(error_reason="", error_msg=""):
    return jsonify(success=False,
                   error_reason=error_reason,
                   error_msg=error_msg)
                  

                   


def valid_recaptcha(recaptcha_response):
    resp = urlopen(url=app.config["RECAPTCHA_API_URL"],
                   data=urlencode({"secret": app.config["RECAPTCHA_APP_SECRET_KEY"],
                                   "response": recaptcha_response}))
    t = json.load(resp)
    return t["success"]


def broadcast_entrance(kwds):
    pass


import pprint
@app.route("/rest/entrance", methods=["POST"])
def rest_entrance():
    form = request.form
    kwds = {}
    for key in ["name", "grade", "class", 
                "email", "address", "religion", 
                "worry", "hobby", "healthy"]:
        kwds[key] = form[key]

    for key in ["desired-date", "middle-school"]:
        kwds[key.replace("-", "_")] = form[key]
    motive = []
    motive_etc_content = None
    for x in ["himself", "parent", "friend", "etc"]:
        key = 'motive-%s' % x
        if key in form:
            motive.append(x)
            if x == "etc":
                motive_etc_content = form["motive-etc-content"]
    kwds["motive"] = motive
    kwds["motive_etc_content"] = motive_etc_content

    kwds["desired_univ"] = [form["desired-univ%d"%idx] for idx in range(1, 4)]
    kwds["desired_job"] = [form["desired-job%d"%idx] for idx in range(1, 4)]

    fam_imd_list = filter(any,
                          zip(form.getlist("fam-rel"), 
                              form.getlist("fam-name"), 
                              form.getlist("fam-age"),
                              form.getlist("fam-scholarship"),
                              form.getlist("fam-job"),
                              form.getlist("fam-phone")))

    family = []
    for rel, name, age, scholarship, job, phone in fam_imd_list:
        family.append({
            "rel": rel,
            "name": name,
            "age": age,
            "scholarship": scholarship,
            "job": job,
            "phone": phone
        })
    kwds["family"] = family

    inschool_rel_imd_list = filter(any,
                                   zip(form.getlist("inschoolrel-grade"),
                                       form.getlist("inschoolrel-class"),
                                       form.getlist("inschoolrel-name")))
    inschool_rel = []
    for grade, class_, name in inschool_rel_imd_list:
        inschool_rel.append({
            "grade": grade,
            "class": class_,
            "name": name
        })
    kwds["inschool_rel"] = inschool_rel


    outschool_rel_imd_list = filter(any,
                                    zip(form.getlist("outschoolrel-school"),
                                        form.getlist("outschoolrel-phone"),
                                        form.getlist("outschoolrel-name")))
    outschool_rel = []
    for school, phone, name in outschool_rel_imd_list:
        outschool_rel.append({
            "school": school,
            "phone": phone,
            "name": name
        })
    kwds["outschool_rel"] = outschool_rel
    kwds["ip"] = request.remote_addr

    recaptcha_response = form["g-recaptcha-response"]
    if not recaptcha_response:
        return rest_error_response(error_reason="recaptcha", 
                                   error_msg="\"로봇이 아닙니다\" "
                                             "상자를 체크 한 뒤 "
                                             "다시 시도하세요.")
    if not valid_recaptcha(recaptcha_response):
        return rest_error_response(error_reason="recaptcha", 
                                   error_msg="인증에 실패하였습니다."
                                             " 다시 시도하세요.")

    pprint.pprint(kwds)
    # success!
    add_entrance_data(kwds)
    return jsonify(success=True)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
