import os
import json
import motor.motor_tornado
import tornado.web
from datetime import datetime
from settings import settings as S
from tornado import gen
from bson.objectid import ObjectId

CODE ='utf-8'
ROWS_NAME = 'rows'
ERROR = 'error'
LENGTH = 'length'
ID = '_id'

DB_CONNECTION = (
    os.environ.get('MONGO_SERVICE_HOST'), 
    int(os.environ.get('MONGO_SERVICE_PORT')),
)
 
DB = motor.motor_tornado.MotorClient(
    *DB_CONNECTION
)[os.environ.get('MONGO_SERVICE_DB')]

JSON_HEADER = ('Content-Type', 'application/json')


def find_id(id_):
    return {ID: ObjectId(id_)}


def timer():
    start_time = datetime.now()
    def func():
        return round((datetime.now() - start_time).total_seconds(), 2)
    return func


class BaseHandler(tornado.web.RequestHandler):

    _db = DB

    def write_json(self, rows, length=None, error=None):
        self.set_header(*JSON_HEADER)
        
        if not length:
            length = len(rows)
        
        if not error:
            _ = json.dumps({ROWS_NAME: rows, LENGTH: length})
        else:
            _ = json.dumps({ERROR: error})
        self.write(_.encode(CODE))

    def write_json_error(self, **kwargs):
        self.write_json(rows=[], error=kwargs)
    
    def get_rows(self):
        return json.loads(self.request.body.decode(CODE))[ROWS_NAME]


class CollectionHandler(BaseHandler):

    @staticmethod
    def get_collection(collection, method):
        return getattr(S, collection)[method]
    
    @staticmethod
    def get_query(data, collection):
        for key, value in collection.items():
            if value:
                data[key] = value(key, data.get(key))
        return data

    @gen.coroutine
    def get(self, collection):
        id_ = self.get_argument(ID, None)
        rows = []
        if id_:
            _ = yield self._db[collection].find_one(find_id(id_))
            rows.append(_)
        else:
            query = dict()
            coll = self.get_collection(collection, S.FIND)
            for key, value in coll.items():
                val = self.get_query_argument(key, None)
                if val:
                    query[key] = value(val)
            cursor = self._db[collection].find(query)
            while (yield cursor.fetch_next):
                _ = cursor.next_object()
                rows.append(_)
        
        for row in rows:
            row[ID] = str(row[ID])
        self.write_json(rows)

    @gen.coroutine
    def post(self, collection):
        try:
            rows = self.get_rows()
            coll = self.get_collection(collection, S.INSERT)
            queryes = map(lambda row: self.get_query(row, coll), rows)
            _ = []
            for query in queryes:
                id_ = yield self._db[collection].insert(query)
                _.append(str(id_))
        except Exception as err:
            self.write_json_error(status=400, message=err.args)
        else:
            self.write_json(_)

    @gen.coroutine
    def delete(self, collection):
        id_ = self.get_argument(ID)
        _ = yield self._db[collection].remove(find_id(id_))
        self.write_json([], length=_['n'])
