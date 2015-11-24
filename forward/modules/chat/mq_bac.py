# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import pika
import threading
from mq_callback import getProcessor 

try:
    from settings import MQ_HOST, MQ_EXCHANGE_NAME,MQ_LOG
except:
    MQ_HOST = 'localhost'
    MQ_EXCHANGE_NAME = 'forward'


class MQ():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=MQ_EXCHANGE_NAME, exchange_type='topic')
    result = channel.queue_declare(exclusive=True, durable=True)
    queue_name = result.method.queue

    def __init__(self):
        self.binding_keys = set()

    def _bind(self, key):
        self.channel.queue_bind(exchange=MQ_EXCHANGE_NAME, queue=self.queue_name, routing_key=key)

    def _unBind(self, key):
        self.channel.queue_unbind(exchange=MQ_EXCHANGE_NAME, queue=self.queue_name, routing_key=key)

    def _publish(self, routing_key, message):
        self.channel.basic_publish(exchange=MQ_EXCHANGE_NAME, routing_key=routing_key, body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,
                                   ))

    @staticmethod
    def callback(ch, method, properties, body):
        """
        :param method: ['consumer_tag=ctag1.fe37cc6edbbf4c4595445bddb8b8a1e0', 'delivery_tag=1', 'exchange=forward',
        'redelivered=False', 'routing_key=forward.jack.info']
        :param properties: pika.spec.BasicProperties
        print properties.content_type
        print properties.content_encoding
        print properties.headers
        print properties.delivery_mode
        print properties.priority
        print properties.correlation_id
        print properties.reply_to
        print properties.expiration
        print properties.message_id
        print properties.timestamp
        print properties.type
        print properties.user_id
        print properties.app_id
        print properties.cluster_id
        """
        MQ_LOG.debug("call back routing_key:%s,body:%s",method.routing_key, body)

        p = getProcessor(method.routing_key, body)
        if p:
            p.callback()

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def publish(self, routing_key, message):
        MQ_LOG.debug("publish routing_key:%s,message:%s",routing_key, message)
        self._publish(routing_key, message)

    def subscribe(self, binding_key):
        if binding_key not in self.binding_keys:
            MQ_LOG.debug("subscribe routing_key:%s",binding_key)
            self.binding_keys.add(binding_key)
            self._bind(binding_key)

    def resubscribe(self, binding_key):
        if binding_key in self.binding_keys:
            self.binding_keys.remove(binding_key)
            self._unBind(binding_key)

    @staticmethod
    def listen():
        MQ.channel.basic_consume(MQ.callback, queue=MQ.queue_name)
        RecThread(MQ.channel).start()


class RecThread(threading.Thread):

    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.channel = channel

    def run(self):
        self.channel.start_consuming()

MQ.listen()
print "mq start"
