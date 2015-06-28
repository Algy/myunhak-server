#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json

from bson.objectid import ObjectId
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tempy import Environment 
from urllib import urlopen, urlencode, quote

from pymongo import MongoClient
from db import DBCommonData, LoginFailureError

app = Flask(__name__)
app.config.from_object('config')


tempy_env = Environment("tempy-templates", cache_module=False)
# tempy_env.compile_option.write_py = True 

def make_MongoSessionInterface():
    from uuid import uuid4
    from datetime import datetime, timedelta

    from flask.sessions import SessionInterface, SessionMixin
    from werkzeug.datastructures import CallbackDict
    from pymongo import MongoClient


    class MongoSession(CallbackDict, SessionMixin):

        def __init__(self, initial=None, sid=None):
            CallbackDict.__init__(self, initial)
            self.sid = sid
            self.modified = False


    class MongoSessionInterface(SessionInterface):
        def __init__(self, host='localhost', port=27017,
                     db='', collection='sessions'):
            client = MongoClient(host, port)
            self.store = client[db][collection]

        def open_session(self, app, request):
            sid = request.cookies.get(app.session_cookie_name)
            if sid:
                stored_session = self.store.find_one({'sid': sid})
                if stored_session:
                    if stored_session.get('expiration') > datetime.utcnow():
                        return MongoSession(initial=stored_session['data'],
                                            sid=stored_session['sid'])
            sid = str(uuid4())
            return MongoSession(sid=sid)

        def save_session(self, app, session, response):
            domain = self.get_cookie_domain(app)
            if not session:
                response.delete_cookie(app.session_cookie_name, domain=domain)
                return
            if self.get_expiration_time(app, session):
                expiration = self.get_expiration_time(app, session)
            else:
                expiration = datetime.utcnow() + timedelta(hours=1)
            self.store.update({'sid': session.sid},
                              {'sid': session.sid,
                               'data': session,
                               'expiration': expiration}, True)
            response.set_cookie(app.session_cookie_name, session.sid,
                                expires=self.get_expiration_time(app, session),
                                httponly=True, domain=domain)
    return MongoSessionInterface



MongoSessionInterface = make_MongoSessionInterface()
app.session_interface = MongoSessionInterface(
    db=app.config["DB_NAME"], 
    host=app.config["DB_HOST"],
    port=app.config["DB_PORT"])

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

def redirect_to_login(next_url=None, login_failed=False):
    url = url_for("login") + "?next_url=%s"%quote(next_url)
    if login_failed:
        url += "&login_failed="

    return redirect(url)


@with_common_data
def login_required(data, required_roles=[], hard_refusal=True, 
                   break_session=True, when_not_granted=None):
    def wrapper(fun):
        @wraps(fun)
        def inner(*args, **kwds):
            username = session.get("username")
            success = True

            if username is None:
                success = False
            else:
                user_dict = data.get_user_by_username(username, fields={"_id": False, "role": True})
                if user_dict is None:
                    success = False
                else:
                    user_role = user_dict.get("role", [])
                    if any((role not in user_role) for role in required_roles):
                        success = False
                        if when_not_granted:
                            gres = when_not_granted()
                            if gres is not None:
                                return gres
            if not success:
                if break_session:
                    session.clear()

                if hard_refusal:
                    resp = Response("잘못된 접근입니다.")
                    resp.status_code = 404
                    return resp
                else:
                    return redirect_to_login(request.url)
            return fun(*args, **kwds)
        return inner
    return wrapper


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


@with_common_data
def tell_if_valid_user(username, raw_password, next_url, data):
    try:
        res = data.get_user_by_login(username, raw_password)
        session["username"] = res["username"]
        return redirect(next_url)
    except LoginFailureError:
        return redirect_to_login(next_url, True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        next_url = request.args.get("next_url")
        login_failed = "login_failed" in request.args
        return str(tempy_env.module("login").Template(next_url, login_failed))
    else:
        next_url = request.form.get("next_url", url_for("index"))
        username = request.form["username"]
        raw_password = request.form["password"]

        return tell_if_valid_user(username, raw_password, next_url)



import pytz
local_tz = pytz.timezone('Asia/Seoul') # use your local timezone name here
def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

@with_common_data
def render_all_data(data):
    dicts = data.paged_entrance_data.query_desc({}, 1000)
    for d in dicts:
        d["created_at"] = utc_to_local(d["created_at"])

    return str(tempy_env.module("manage_index").Template(dicts))

@with_common_data
def render_data(oid, data):
    d = data.get_entrance(oid)
    if d:
        return "구현이 안되었어요.."
    else:
        return ("잘못된 데이터.", 404, ())


@app.route("/manage", methods=["GET"])
@login_required(required_roles=["admin"], hard_refusal=False)
def manage():
    return render_all_data()


@app.route("/manage/<elem_id>", methods=["GET"])
@login_required(required_roles=["admin"], hard_refusal=False)
def manage_id(elem_id):
    return render_data(elem_id)







@app.route("/canflaskscale", methods=["GET"])
def canflaskscale():
    return str(tempy_env.module("canflaskscale").MainTemplate())



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

    '''
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
    '''

    # success!
    add_entrance_data(kwds)
    return jsonify(success=True)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
