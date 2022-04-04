from flask import Flask, request
from bleach import clean
from api.config import config
import datetime
import time
import json
import redis
import uuid
app = Flask(__name__)
rds = redis.StrictRedis(host=config["redis"]["ip"], port=config["redis"]["port"],
                        db=config["redis"]["db"], password=config["redis"]["password"])

def json_route(*args1, **kwargs1):
    def ret_func(func):
        @json_route(*args1, **kwargs1)
        def ret_func2(*args2, **kwargs2):
            return json.dumps(func(*args2, **kwargs2), ensure_ascii=False)
        return ret_func2
    return ret_func

@json_route('/api/')
def index():
    return {'status': 'ok', 'message': 'Hello World!'}


#POST /api/comment_s
@json_route('/api/comment_s', methods=['POST', "GET"])
def comment_s():
    # 不可维护的代码awa
    content_length=len(request.json['content'])
    if content_length < 1 or content_length > 100:
        return {'status': 'error', 'message': 'content length error'}
    ip = request.remote_addr
    if ip in config["ip_blacklist"]:
        return {'status': 'error', 'message': 'ip is banned forever'}
    ipk = f"connect_{ip}"
    ipb = f"isStop_{ip}"
    ipban = f"ip_{ip}"
    if rds.exists(ipban) and int(rds[ipban].decode(encoding="utf-8")) >= 4:
        return {'status': 'error', 'message': '你已经被禁了'}
    if rds.exists(ipk) and int(rds[ipk].decode(encoding="utf-8")) >= 4:
        if rds.exists(ipban) and not rds.exists(ipb):
            rds.set(ipban, int(rds[ipban].decode(encoding="utf-8"))+1)
            rds.expire(ipban, 60*60*24)
        elif not rds.exists(ipban) and not rds.exists(ipb):
            rds.set(ipban, 1)
            rds.expire(ipban, 60*60*24)
        rds.set(ipb,1)
        rds.expire(ipb, 60)
        return {'status': 'error', 'message': '请求过于频繁，请稍后再试'}
    elif not rds.exists(ipk):
        rds.set(ipk, '1')
        rds.expire(ipk, 60)
    else:
        rds.set(ipk, str(int(rds[ipk].decode(encoding="utf-8"))+1))
        rds.expire(ipk, 60)
    try:
        if request.json.get("comment_type")==None or request.json.get("comment_type")=="":
            return {'status': 'error', 'message': 'type is required'}
        comment_content = request.json['content']
        if request.json["comment_type"]=="normal":
            cid = f"comment_{uuid.uuid5(uuid.NAMESPACE_DNS,comment_content+str(time.time())).hex}"
            rds[cid] = comment_content
        elif request.json["comment_type"]=="destroy":
            cid = f"destroy_{uuid.uuid5(uuid.NAMESPACE_DNS,comment_content+str(time.time())).hex}"
            rds[cid] = comment_content
        elif request.json["comment_type"]=="timed":
            rds[cid] = comment_content
            if not rds.expireat(datetime.datetime.fromtimestamp(request.json["time"])):
                return {'status': 'error', 'message': 'time error'}
        return {'status': 'ok', 'message': 'Comment Commited', 'id': cid}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@json_route('/api/comment_g/<string:id>')
def get_comment(id):
    id=id.strip()
    id_type=id.split("_")[0]
    if rds.exists(id):
        content=rds[id].decode(encoding="utf-8")
        if id_type=="destroy":
            rds.delete(id)
            return {'status': 'ok', 'message': 'Comment found(destroy after read)', 'content': content}
        return {'status': 'ok', 'message': 'Comment found', 'content': content}
    else:
        return {'status': 'error', 'message': 'Comment not found'}


@json_route('/api/comment_d/<string:id>')
def delete_comment(id):
    if rds.exists(id):
        rds.delete(id)
        return {'status': 'ok', 'message': 'Comment deleted'}
    else:
        return {'status': 'error', 'message': 'Comment not found'}


@json_route('/api/data/<string:key>')
def get_data(key):
    if key != config["control"]["find_all_data"]:
        return {'status': 'error', 'message': 'wrong password'}
    ret = {}
    for a in rds.keys():
        ret[a.decode()] = rds[a.decode()].decode()
    return {'status': 'ok', 'message': 'Data found', 'data': ret}


@json_route('/api/clear_db/if_you_know_what_you_are_doing/<string:password>')
def clear_db(password):
    if password != config["control"]["clear_db"]:
        return {'status': 'error', 'message': 'Wrong password'}
    for a in rds.keys():
        if str(a, "utf-8").split("_")[0] == "comment":
            rds.delete(a)

    return {'status': 'ok', 'message': 'Data cleared'}

# unbanned
@json_route('/api/unban/<string:ipk>/<string:password>')
def unban(ipk, password):
    if password != config["control"]["ban_ip"]:
        return {'status': 'error', 'message': 'Wrong password'}
    if rds.exists(ipk):
        rds.delete(ipk)
        return {'status': 'ok', 'message': 'unbanned'}
    else:
        return {'status': 'error', 'message': 'ip not found'}



if __name__ == "__main__":
    app.run(debug=True)
