from flask import Flask, request
from bleach import clean
from api.config import config
import random
import string
import time
import json
import redis
import uuid
app = Flask(__name__)
rds = redis.StrictRedis(host=config["redis"]["ip"], port=config["redis"]["port"],
                        db=config["redis"]["db"], password=config["redis"]["password"])



@app.route('/api/')
def index():
    return json.dumps({'status': 'ok', 'message': 'Hello World!'}, ensure_ascii=False)


#POST /api/comment_s
@app.route('/api/comment_s', methods=['POST', "GET"])
def comment_s():
    # 不可维护的代码awa
    content_length=len(request.json['content'])
    if content_length<1 or content_length>100:
        return json.dumps({'status': 'error', 'message': 'content length error'}, ensure_ascii=False)
    ip = request.remote_addr
    if ip in config["ip_blacklist"]:
        return {'status': 'error', 'message': 'ip is banned forever'}
    ipk = "connect_"+ip
    ipb = "isStop_"+ip
    ipban = "ip_"+ip
    if rds.exists(ipban) and int(rds[ipban].decode(encoding="utf-8")) >= 4:
        return json.dumps({'status': 'error', 'message': '你已经被禁了'}, ensure_ascii=False)
    if rds.exists(ipk) and int(rds[ipk].decode(encoding="utf-8")) >= 4:
        if rds.exists(ipban) and not rds.exists(ipb):
            rds.set(ipban, int(rds[ipban].decode(encoding="utf-8"))+1)
            rds.expire(ipban, 60*60*24)
        elif not rds.exists(ipban) and not rds.exists(ipb):
            rds.set(ipban, 1)
            rds.expire(ipban, 60*60*24)
        rds.set(ipb,1)
        rds.expire(ipb, 60)
        return json.dumps({'status': 'error', 'message': '请求过于频繁，请稍后再试'}, ensure_ascii=False)
    elif not rds.exists(ipk):
        rds.set(ipk, '1')
        rds.expire(ipk, 60)
    else:
        rds.set(ipk, str(int(rds[ipk].decode(encoding="utf-8"))+1))
        rds.expire(ipk, 60)
    try:
        if request.json.get("comment_type")==None or request.json.get("comment_type")=="":
            return json.dumps({'status': 'error', 'message': 'type is required'}, ensure_ascii=False)
        comment_content = clean(request.json['content'], tags=[
                                "strong", "em", "mark", "del", "u", "a", "img", "blockquote"], strip=True)
        if request.json["comment_type"]=="normal":
            cid = "comment_"+uuid.uuid5(uuid.NAMESPACE_DNS,comment_content+str(time.time())).hex
            rds[cid] = comment_content
        elif request.json["comment_type"]=="destroy":
            cid = "destroy_"+uuid.uuid5(uuid.NAMESPACE_DNS,comment_content+str(time.time())).hex
            rds[cid] = comment_content
        elif request.json["comment_type"]=="timed":
            rds[cid] = comment_content
            rds.expireat(datetime.datetime.fromtimestamp(request.json["time"]))
        return json.dumps({'status': 'ok', 'message': 'Comment Commited', 'id': cid}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)


@app.route('/api/comment_g/<string:id>')
def get_comment(id):
    id=id.strip()
    id_type=id.split("_")[0]
    if rds.exists(id):
        content=rds[id].decode(encoding="utf-8")
        if id_type=="destroy":
            rds.delete(id)
            return json.dumps({'status': 'ok', 'message': 'Comment found(destroy after read)', 'content': content}, ensure_ascii=False)
        return json.dumps({'status': 'ok', 'message': 'Comment found', 'content': content}, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': 'Comment not found'}, ensure_ascii=False)


@app.route('/api/comment_d/<string:id>')
def delete_comment(id):
    if rds.exists(id):
        rds.delete(id)
        return json.dumps({'status': 'ok', 'message': 'Comment deleted'}, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': 'Comment not found'}, ensure_ascii=False)


@app.route('/api/data/<string:key>')
def get_data(key):
    if key != config["control"]["find_all_data"]:
        return json.dumps({'status': 'error', 'message': 'wrong password'}, ensure_ascii=False)
    ret = {}
    for a in rds.keys():
        ret[a.decode()] = rds[a.decode()].decode()
    return json.dumps({'status': 'ok', 'message': 'Data found', 'data': ret}, ensure_ascii=False)


@app.route('/api/clear_db/if_you_know_what_you_are_doing/<string:password>')
def clear_db(password):
    if password != config["control"]["clear_db"]:
        return json.dumps({'status': 'error', 'message': 'Wrong password'}, ensure_ascii=False)
    for a in rds.keys():
        if str(a, "utf-8").split("_")[0] == "comment":
            rds.delete(a)

    return json.dumps({'status': 'ok', 'message': 'Data cleared'}, ensure_ascii=False)

# unbanned
@app.route('/api/unban/<string:ipk>/<string:password>')
def unban(ipk, password):
    if password != config["control"]["ban_ip"]:
        return json.dumps({'status': 'error', 'message': 'Wrong password'}, ensure_ascii=False)
    if rds.exists(ipk):
        rds.delete(ipk)
        return json.dumps({'status': 'ok', 'message': 'unbanned'}, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': 'ip not found'}, ensure_ascii=False)



if __name__ == "__main__":
    app.run(debug=True)
