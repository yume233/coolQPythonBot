from elasticsearch import TransportError
from elasticsearch_dsl.connections import create_connection
from elasticsearch_dsl.response import Response
from functools import wraps
from elasticsearch_dsl import Document,Integer

class ChatRecord(Document):
    id = Integer(required=True)
    