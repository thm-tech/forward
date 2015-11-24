import tornado.websocket
import tornado.web

from forward.log.fdlog import fd_log
"""
class PushToPos(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/push" method="POST">'
                '<input type="text" name="shop_id">'
                '<input type="text" name="pos_id">'
                '<input type="text" name="message">'
                '<input type="submit" value="Submit">'
                '</form></body></html>')

    def post(self):
        shop_id = self.get_argument("shop_id")
        pos_id = self.get_argument("pos_id")
        message = self.get_argument("message")
        print shop_id,pos_id,message

        LjionHandler.pushPos(shop_id,pos_id,message)
"""

class LJoinBase(tornado.websocket.WebSocketHandler):
    key_self = {}

    def open(self):
        """
        Invoking when websocket linking is opened. Child class overwrite this method
        """
        pass

    def registKeySelf(self,key):
        self.key = key 

        try:
            self.key_self[self.key] = self
        except:
            fd_log.error("ljion key already exist" + self.key)

    def on_close(self):
        try:
            del self.key_self[self.key]
        except:
            fd_log.error("del ljion key not exist" + self.key)
        
    @staticmethod
    def pushMessage(key, message):
        try:
            LJoinBase.key_self[key].write_message(message)
        except:
            fd_log.error("ljion write message error" + message)
