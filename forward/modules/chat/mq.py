# -*- encoding: utf-8 -*-

__author__ = 'htfang'

import pika
import threading
import tornado.ioloop
from pika.adapters.tornado_connection import TornadoConnection
from mq_callback import getProcessor 

try:
    from settings import *
except:
    MQ_HOST = 'localhost'
    MQ_EXCHANGE_NAME = 'forward'


class MQ():
    def __init__(self):
        self.connected = False
        self.connecting = False

        self.channel = None
        self.queue_name = "queue-%s"%(id(self),)

    def connect(self):
        if self.connecting:
            MQ_LOG.info('mq already connecting to RabbitMQ')
            return

        MQ_LOG.info('connecting to RabbitMQ ... host:%s',MQ_HOST)

        self.connecting = True

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWD)
        param = pika.ConnectionParameters(host=MQ_HOST, credentials=credentials)

        self.connection = pika.TornadoConnection(param,
                                            on_open_callback=self.on_conn_open,
                                            on_close_callback=self.on_conn_close,
                                            on_open_error_callback=self.on_conn_error
                                            )

    def on_conn_open(self, connection):
        MQ_LOG.info("on connection open")
        self.connected  = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        MQ_LOG.info("on channel open:%s",self.channel)
        self.channel.exchange_declare(exchange=MQ_EXCHANGE_NAME, 
                                      exchange_type='topic',
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        MQ_LOG.info("exchange declared")
        self.channel.queue_declare(exclusive=True, 
                                   queue=self.queue_name,
                                   durable=True,
                                   callback=self.on_queue_declared)
        

    def on_queue_declared(self, frame, key='none_key'):
        MQ_LOG.info("queue declared")
        self.channel.queue_bind(exchange=MQ_EXCHANGE_NAME,
                                queue=self.queue_name,
                                routing_key=key,
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        self.channel.basic_consume(consumer_callback=MQ.callback,
                                   queue=self.queue_name,
                                   )

    def on_conn_close(self):
        MQ_LOG.warn("mq connection close")
        self.connected = False
        self.connecting = False
        self.connect()

    def on_conn_error(self):
        MQ_LOG.error("mq connection error")

    def _bind(self, key):
        self.on_queue_declared(None, key)

    def _unBind(self, key):
        self.channel.queue_unbind(exchange=MQ_EXCHANGE_NAME, queue=self.queue_name, routing_key=key)

    def _publish(self, routing_key, message):
        self.channel.basic_publish(exchange=MQ_EXCHANGE_NAME, routing_key=routing_key, body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,
                                   ))

    @staticmethod
    def callback(ch, method, properties, body):
        MQ_LOG.debug("call back routing_key:%s,body:%s",method.routing_key, body)

        p = getProcessor(method.routing_key, body)
        if p:
            p.callback()

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def publish(self, routing_key, message):
        MQ_LOG.debug("publish routing_key:%s,message:%s",routing_key, message)
        self._publish(routing_key, message)

    def subscribe(self, binding_key):
        MQ_LOG.debug("subscribe routing_key:%s",binding_key)
        self._bind(binding_key)

    def resubscribe(self, binding_key):
        self._unBind(binding_key)

rabbit_mq = MQ()
rabbit_mq.connect()
print "mq start"
