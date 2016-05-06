"""
Test run "python -m tornado.test.runtests test.main" 
"""
import os
import json
from query import *
from tornado import testing, httpclient


class MyTestCase(testing.AsyncTestCase):

    @testing.gen_test
    def test_query(self):
        str_validate = 'some string'
        str_ = STR()
        str_ = str_('field_1', str_validate)
        self.assertEqual(str_, str_validate)
        int_validate = '1'
        int_ = INT(blank=False)
        int_1 = int_('field_2', int_validate)
        self.assertEqual(int_1, int(int_validate))
        with self.assertRaises(ValueError):
            int_2 = int_('field_2', None)
        with self.assertRaises(ValueError):
            int_2 = int_('field_2', 'some')

    @testing.gen_test
    def test_http_fetch(self):
        
        # Insert documents
        docs = {'rows': [
            {'field_1': 'record 1', 'field_2': 1},
            {'field_1': 'record 2', 'field_2': 2},
            {'field_1': 'record 3', 'field_2': 2},
            {'field_2': 100}
        ]}
        docs_json = json.dumps(docs)
        path = 'http://{}:{}/test_collection'.format(
            os.environ.get('TORNADO_SERVER_HOST'),
            os.environ.get('TORNADO_SERVER_PORT'),
            )
        client = httpclient.AsyncHTTPClient(self.io_loop)
        response = yield client.fetch(path, method='POST', body=docs_json)
        self.assertEqual(response.code, 200)
        insert_docs = json.loads(response.body.decode('utf-8'))
        self.assertEqual(insert_docs['length'], 4)
        
        # Get docs
        for doc in insert_docs['rows']:
            response = yield client.fetch(
                '{}?_id={}'.format(path, doc), method='GET'
            )
            self.assertEqual(response.code, 200)
            get_doc = json.loads(response.body.decode('utf-8'))
            self.assertEqual(get_doc['length'], 1)

        response = yield client.fetch(
            '{}?field_2=2'.format(path), method='GET'
        )
        self.assertEqual(response.code, 200)
        get_doc = json.loads(response.body.decode('utf-8'))
        self.assertEqual(get_doc['length'], 2)

        response = yield client.fetch(
            '{}?field_2=4'.format(path), method='GET'
        )
        self.assertEqual(response.code, 200)
        get_doc = json.loads(response.body.decode('utf-8'))
        self.assertEqual(get_doc['length'], 0)
        
        # Update document
        new_doc = {'rows': [
            {'field_1': 'record updated', 'field_2': 1},
        ]}
        new_doc_json = json.dumps(new_doc)
        response = yield client.fetch(
            '{}?field_2=1'.format(path), method='PUT', body=new_doc_json)
        self.assertEqual(response.code, 200)
        new_doc_response = json.loads(response.body.decode('utf-8'))
        self.assertEqual(new_doc_response['length'], 1)
        response = yield client.fetch(
            '{}?_id={}'.format(
                path, new_doc_response['rows'][0]
            ),
            method='GET'
        )
        self.assertEqual(response.code, 200)
        get_doc = json.loads(response.body.decode('utf-8'))
        self.assertEqual(get_doc['length'], 1)
        self.assertEqual(get_doc['rows'][0]['field_1'], 'record updated')

        # Delete documents
        for doc in insert_docs['rows']:
            response = yield client.fetch(
                '{}?_id={}'.format(path, doc), method='DELETE'
            )
            self.assertEqual(response.code, 200)
            delete_doc = json.loads(response.body.decode('utf-8'))
            self.assertEqual(delete_doc['length'], 1)
        
        # Insert invalid documents
        invalid_docs = {'rows': [
            {'field_1': 'record 4'}
        ]}
        invalid_docs_json = json.dumps(invalid_docs)
        response = yield client.fetch(
            path, method='POST', body=invalid_docs_json)
        self.assertEqual(response.code, 200)
        invalid_insert = json.loads(response.body.decode('utf-8'))
        self.assertEqual(invalid_insert['error']['status'], 400)
        self.assertEqual(invalid_insert['error']['message'][0],
        'Value field_2 must be present')