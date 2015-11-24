import thread
import json
import uuid

import pika

from forward.config import MQ_HOST, MQ_USERNAME, MQ_PASSWD, MQ_TYPE, BS_NAME
from forward.log.fdlog import log


mq_log = log.getLogger("fd")


class ActiveMQ(object):
    """docstring for activeMQ"""

    def __init__(self, arg):
        super(activeMQ, self).__init__()
        self.arg = arg


class RabbitMQ(object):
    """useage of rabbitMQ document
    receiver get request call this method when your regist it to commandHandleDict,
       like this:
       mq.registCommand("echoAge",echoAge)
    def echoAge(message):
        docstring for echoAge
        print message
        return "i am 24"

    your send a request ,and care about the response,this method handle response when
       your regist it in uuidHandleDict,
       like this:
       mq.MQSend("bs","hello","echoAge",gotResponse)
    def gotResponse(message):
        docstring for gotResponse
        print "\nyour say:" + message



    mq = MQ("www")
    mq.registCommand("echoAge",echoAge)

    thread.start_new(mq.MQStart,())


    while(1):
        receiver = raw_input("input receiver>")
        message = "my name is " + mq.modulName + " how old are you?"
        print mq.modulName  + "---> " + receiver + " : " + message
        mq.MQSend(receiver,message,"echoAge",gotResponse)
    document end """

    """save key:uuid value:Handle,when receiver response,sender know how to
       handle it"""
    uuidHandleDict = {}
    """save key:command value:Handle,when receive a request ,receiver according to 
       command to handle it"""
    commandHandleDict = {}

    def __init__(self, modulName="www"):
        self.modulName = modulName

        pika.connection.Parameters.DEFAULT_USERNAME = MQ_USERNAME
        pika.connection.Parameters.DEFAULT_PASSWORD = MQ_PASSWD

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=MQ_HOST))

        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='forward',
                                      exchange_type='topic')

        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='forward',
                                queue=self.queue_name,
                                routing_key=self.modulName)

        self.channel.basic_consume(self.MQRecv,
                                   queue=self.queue_name,
                                   no_ack=True)

    def registCommand(self, command, method=None):
        try:
            self.commandHandleDict[command] = method
            return True
        except:
            mq_log.error("regist request handle failed" + command)
            return False


    """when got response will call method"""

    def MQSend(self, receiver="bs", message="hello", command=None, method=None):
        """docstring for MQSend"""
        corr_id = str(uuid.uuid4())
        self.uuidHandleDict[corr_id] = method

        messageDict = {"command": command, "message": message}
        message = json.dumps(messageDict)

        """TODO add command in body"""

        self.channel.basic_publish(exchange="forward",
                                   routing_key=receiver,
                                   properties=pika.BasicProperties(
                                       reply_to=self.modulName,
                                       correlation_id=corr_id,
                                   ),
                                   body=message)


    def MQRecv(self, ch, method, props, body):
        """docstring for MQRecv"""

        # handle request
        if props.reply_to:
            bodyDict = eval(body)
            """according to command handle something"""
            res = self.commandHandleDict[bodyDict["command"]](bodyDict["message"])

            mq_log.debug(self.modulName + "---->" + props.reply_to + ":" + res)
            # response
            self.channel.basic_publish(exchange="forward",
                                       routing_key=props.reply_to,
                                       properties=pika.BasicProperties(
                                           reply_to=None,
                                           correlation_id=props.correlation_id,
                                       ),
                                       body=res
                                       )
        # handle response
        else:
            self.uuidHandleDict[props.correlation_id](body)
            del self.uuidHandleDict[props.correlation_id]

    def MQStart(self):
        """docstring for MQStart"""
        self.channel.start_consuming()


class MQFactory(object):
    """docstring for MQFactory"""

    @staticmethod
    def MQCreator(mq_type):
        """docstring for MQCreator"""
        return {"rabbitMQ": RabbitMQ, "activeMQ": ActiveMQ}[mq_type]


class MQInterface(object):
    Mq = MQFactory.MQCreator(MQ_TYPE)
    # use this object to handle message queue
    mq = Mq(BS_NAME)
    # logger.info("mq thread start..." + MQ_HOST+ MQ_USERNAME+ MQ_PASSWD+ MQ_TYPE+ BS_NAME)
    thread.start_new(mq.MQStart, ())
    mq_log.info("message queue thread start")

    """sub class just care about this two method, visit other member,is not reasonable"""

    @staticmethod
    def registCommand(command, method=None):
        return MQInterface.mq.registCommand(command, method)

    """when got response will call method"""

    @staticmethod
    def MQSend(receiver="bs", message="hello", command=None, method=None):
        return MQInterface.mq.MQSend(receiver, message, command, method)
