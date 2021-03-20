#UTILS
from app import app
from bson import ObjectId
from umongo import Document
from umongo import fields
import datetime
# from functools import wraps
import jwt
import configparser
import traceback
import json
import traceback
from sanic.response import json as sanicjson
from pytz import timezone
import requests
import time

SECRET_SHARED_TOKEN = '@54#s'
FUSO_HORARIO = timezone('America/Sao_Paulo')

HTTP_CREATED = 201
HTTP_BADREQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOTFOUND = 404

@app.lazy_umongo.register
class BaseDocument(Document):
    createdAt = fields.DateTimeField(required=False)
    updatedAt = fields.DateTimeField(required=False)
    class Meta:
        abstract = True

    def pre_insert(self):
        self.createdAt = now()
        self.updatedAt = now()

    def pre_update(self):
        self.updatedAt = now()


# FUNCOES GENERICAS

"""converter cursor motor mongo em json"""
async def _cur_to_json(cursor):
    data = []
    #https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
    #https://motor.readthedocs.io/en/stable/api-asyncio/cursors.html
    for document in await cursor.to_list(length=None):
        #item = json.loads(json.dumps(document.dump(), default=_json_default))
        item = document.dump()
        data.append(item)
    return data

"""formatação dump json"""
def _json_default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.astimezone(FUSO_HORARIO).isoformat()
    if isinstance(o, ObjectId):
        return str(o)
    else:
        return o

"""override response json sanic"""
def jsonify(body,
    status=200,
    headers=None,
    content_type="application/json"):
    result = json.loads(json.dumps(body, default=_json_default))
    return sanicjson(body=result,status=status,headers=headers,content_type=content_type)

"""data e horario atual"""
def now():
    time_difference = FUSO_HORARIO.utcoffset(datetime.datetime.utcnow()).total_seconds()
    return datetime.datetime.utcnow() + datetime.timedelta(0, time_difference)

"""ObjectID do mongo"""
def _to_objid(data):
    try:
        return ObjectId(data)
    except:
        # traceback.print_exc()
        return ''

"""filtro de objectId do mongo"""
def _id_lookup(id):
    return  {'_id': _to_objid(id)}

"""filtro objectID ou noderef"""
def _id_lookup_or_noderef(id_or_noderef):
    return {'$or': [{'noderef': id_or_noderef}, {'_id': _to_objid(id_or_noderef)}]}


""" logic json to mongodb"""
""" http://jsonlogic.com/ """
""" ja esta vindo no formato mongo, so ajustes"""
def searchjson_decode(strJson):
    import urllib.parse
    strJson = urllib.parse.unquote(strJson)
    data = json.loads(strJson)
    return data

"""gera token de compartilhamento por 24 horas"""
def getTokenFile(filename,time):
    import jwt
    token = jwt.encode({'f':filename,'exp' : datetime.datetime.now() + datetime.timedelta(hours=time)},SECRET_SHARED_TOKEN)
    return token

"""descriptografar conteudo do JWT"""
def getDataAuth(request):
    token = None
    if 'authorization' in request.headers.keys():
        token = request.headers['authorization'].replace("Bearer ","")
    if token:
        try:
            config = configparser.ConfigParser()
            config.read('config/configuration.cfg')
            secret_key = config.get('jwt', 'secret_key', fallback='abcdefg')
            data = jwt.decode(token, secret_key)
            data = data['login']
            return data
        except:
            print( traceback.format_exc())
            return {}
    return {}