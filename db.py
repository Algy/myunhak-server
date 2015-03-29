#!/usr/bin/env python

import hashlib
import os
import json
import base64

from bson.objectid import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from redis import WatchError
from datetime import datetime


def _redis_cache_least_score(pipe, key):
    t = pipe.zrangebyscore(key,
                           min="-inf",
                           max="+inf",
                           start=0,
                           num=1,
                           withscores=True)
    if len(t) == 0:
        # No slots are in the cache. Thus, cache miss should occur
        return None
    return t[0][1]


def _redis_range_strs(_from, until, exclusive=(False, False)):
    start = "(" if exclusive[0] else ""
    end = "(" if exclusive[1] else ""

    if _from is None:
        start += "-inf"
    else:
        start += str(_from)
    
    if until is None:
        end += "+inf"
    else:
        end += str(until)
    return start, end


class RedisCache(object):
    def __init__(self, redis, key, cache_size, score_getter, cond_filter, loads=json.loads, dumps=json.dumps):
        self.redis = redis
        self.key = key
        self.cache_size = cache_size
        self.score_getter = score_getter
        self.cond_filter = cond_filter # string x object generator -> bool
        self.loads = loads
        self.dumps = dumps


    def _filter_cache_chunk(self, cache_chunk, cond, limit):
        result = []
        count = 0
        for x in cache_chunk:
            suitable = self.cond_filter(cond, s, (x for x in [self.loads(s)]))
            if not suitable:
                continue
            if count >= limit:
                break
            result.append(self.loads(x))
            count += 1
        return result


    def add(self, obj_list):
        list_len = len(obj_list)
        cache_size = self.cache_size
        with self.redis.pipeline() as pipe:
            # cache update
            key = self.key
            while True:
                try:
                    pipe.watch(key)
                    cache_count = pipe.zcard(key)
                    if cache_count + list_len > cache_size:
                        rem = cache_count + list_len - cache_size
                        # evicting cache slots
                        dest = pipe.zrangebyscore(key,
                                                  min="-inf",
                                                  max="+inf",
                                                  withscores=True,
                                                  start=rem-1,
                                                  num=1)
                        if len(dest) > 0:
                            score = dest[0][1]
                            pipe.zremrangebyscore(key,
                                                  min="-inf",
                                                  max=score)
                            cached_elem_num = list_len
                        else:
                            # TOO MANY ELEMENTS FROM FRESH LIST
                            pipe.zremrangebyscore(key,
                                                   min="-inf", 
                                                   max="+inf")
                            cached_elem_num = cache_size
                    else:
                        cached_elem_num = list_len
                    zadd_args = []
                    for d in obj_list:
                        pipe.zadd(key, self.score_getter(d), self.dumps(d))
                    pipe.execute()
                    break
                except WatchError:
                    continue

    def query(self, cond, limit, _from, until, exclusive, desc):
        key = self.key
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    least_recent_slot_time = _redis_cache_least_score(pipe, key)
                    start, end = _redis_range_strs(_from, until, exclusive)
                    if desc:
                        redis_fun = pipe.zrevrangebyscore
                    else:
                        redis_fun = pipe.zrangebyscore
                    cache_chunk = redis_fun(key, min=start, max=end)
                    return (self._filter_cache_chunk(cache_chunk, cond, limit), 
                            least_recent_slot_time)
                except WatchError:
                    continue



    def flush(self):
        raise NotImplementedError




class PagedDataAdapter(object):
    def __init__(self, data, cache=None):
        self.data = data
        self.cache = cache # LRU-style cache


    def _cache_miss(self, cond, limit, _from, until, exclusive, desc):
        return self.data.query(cond, limit, _from, until, exclusive, desc)


    def query_desc(self, cond, limit, _from=None, until=None, exclusive=(False, False)):
        if self.cache:
            cache_result = self.cache.query(cond, limit, _from, until, exclusive, True)
            if cache_result is not None: # if cache contains all or some amount of data
                cache_line, least_recent = cache_result
                cache_len = len(cache_line)
                if cache_len < limit and (_from is None or _from < least_recent):
                    # cache miss occured partially
                    cache_line.extend(self._cache_miss(cond,
                                                       limit - cache_len,
                                                       _from,
                                                       min(least_recent, until),
                                                       (exclusive[0], True),
                                                       desc=True))
                elif cache_len <= limit:
                    return cache_line
                else:
                    return cache_line[:limit]
        return self._cache_miss(cond, limit, _from, until, exclusive, desc=True)

    def query_asc(self, cond, limit, _from=None, until=None, exclusive=(False, False)):
        if self.cache:
            cache_result = self.cache.query(cond, limit, _from, until, exclusive, False)
            if cache_result:
                cache_line, least_recent = self.cache.query(cond, limit, _from, until, exclusive)
                cache_len = len(cache_line)
                if _from is not None and _from >= least_recent:
                    return cache_line

        return self._cache_miss(cond, limit, _from, until, exclusive, desc=False)

    def add(self, obj_list):
        self.data.add(obj_list)
        if self.cache:
            self.cache.add(obj_list)


    def flush_cache(self):
        self.cache.flush()


class MongoData(object):
    def __init__(self, db, coll_name, keyfield, cond_converter, obj_converter, fields=None):
        self.db = db
        self.coll_name = coll_name
        self.keyfield = keyfield
        self.fields = fields
        self.cond_converter = cond_converter
        self.obj_converter = obj_converter


    def add(self, obj_list):
        self.db[self.coll_name].insert(map(self.obj_converter, obj_list))


    def query(self, cond, limit, _from, until, exclusive, desc):
        range_cond = None
        if _from is not None or until is not None:
            range_cond = {}
            if _from is not None:
                if exclusive[0]:
                    range_cond["$gt"] = _from
                else:
                    range_cond["$gte"] = _from
            if until is not None:
                if exclusive[1]:
                    range_cond["$lt"] = until
                else:
                    range_cond["$lte"] = until
        spec = self.cond_converter(cond)
        if range_cond:
            spec.update({self.keyfield: range_cond})
        sort = [(self.keyfield, (DESCENDING if desc else ASCENDING))]
        return list(self.db[self.coll_name].find(spec=spec,
                                                 fields=self.fields,
                                                 limit=limit,
                                                 sort=sort))



ENTRANCE_KEYS = [
    "ip",

    "name",
    "grade",
    "class",
    "email",
    "address",
    "religion",
    "desired_date",
    "motive",
    "motive_etc_content",
    "middle_school",
    "hobby",
    "worry",
    "healthy",
    "desired_univ",
    "desired_job",
    "family", 
    "inschool_rel", 
    "outschool_rel",
]

def generate_random():
    return dict(zip(ENTRANCE_KEYS, ["ang"] * len(ENTRANCE_KEYS)))


def entrance_dict_converter(d):
    assert all((key in d) for key in ENTRANCE_KEYS)
    ins = dict(d)
    ins["created_at"] = datetime.utcnow()
    return ins


    
class LoginFailureError(Exception):
    pass

class DuplicationError(Exception):
    pass


def hash_password(pwd, salt):
    return hashlib.sha256("".join([salt, pwd, salt])).hexdigest()

def generate_salt():
    return base64.b16encode(os.urandom(16))

class DBCommonData(object):
    def __init__(self, db):
        self.db = db
        entrance_mongo_data =  \
            MongoData(db, 
                      "entrance", 
                      "created_at", 
                      lambda cond: cond or {},
                      entrance_dict_converter,
                      None)
        # public
        self.paged_entrance_data = PagedDataAdapter(entrance_mongo_data) 

            

    def ensure_indices(self):
        self.db.user.ensure_index([("username", ASCENDING)],
                                  unique=True,
                                  dropDups=True)

    def add_user(self, username, password, realname, email, phone, role=None):
        salt = generate_salt()
        try:
            self.db.user.insert(
                    {"username": username,
                     "salt": salt,
                     "receive_email": True,
                     "password": hash_password(password, salt),
                     "realname": realname,
                     "email": email,
                     "phone": phone,
                     "role": role or []})
        except DuplicateKeyError:
            raise DuplicationError

    def add_admin(self, username, password, realname, email, phone):
        return self.add_user(username, password, realname, email, phone, ["admin"])


    def rm_user(self, username):
        self.db.user.remove({"username": username})


    def get_user_by_login(self, username, raw_password):
        rec = self.db.user.find_one({"username": username})
        if rec is None:
            raise LoginFailureError
        salt = rec["salt"]
        if hash_password(raw_password, salt) == rec["password"]:
            return rec
        else:
            raise LoginFailureError

    def get_entrance(self, oid):
        return self.db.entrance.find_one(ObjectId(oid))

    def get_user_by_username(self, username, fields=None):
        return self.db.user.find_one({"username": username}, fields=fields)


if __name__ == "__main__":
    client = MongoClient("/tmp/mongodb-27017.sock")
    try:
        data = DBCommonData(client.myunhak)
        print data.paged_entrance_data.query_desc({}, 2)
    finally:
        client.close()

