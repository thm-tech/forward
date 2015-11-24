import websocket
import thread
import time
import sys
import json
import hashlib

def on_message(ws, message):
    print "got message:",message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def sendShopGname():
    shop_id = raw_input("enter shop id>")
    msg = json.dumps({
        'c':'SHOP_GNAME',
        'sid':shop_id
    })
    ws.send(msg)

def enterShop():
    shop_gname = raw_input("enter shop gname>")
    msg = json.dumps({
        'c':'ENTR_SHOP',
        'user':user,
        'gname':shop_gname
    })
    ws.send(msg)


def getE2eGroupName(u1, u2):
    if u1 > u2:
        return 'e2e' + '_' + u1 + '_'+ u2
    else:
        return 'e2e' + '_' + u2 + '_' + u1


def chat():
    msg = raw_input("enter your message>")
    type = raw_input("enter you message type>")
    body = {
        'user':user,
        'time':time.time(),
        'mtype':type,
        'm':msg
    }
    group = raw_input("enter group name>")
    message = {
        'c':'CHAT_M',
        'gname':group,
        'body':body
    }
    if group[0:3] == 'e2e':
        recevier = raw_input("enter recevier name>")
        message['e2e'] = recevier
        message["gname"] = getE2eGroupName(recevier, user) 

    print "you send:",message

    ws.send(json.dumps(message))

def exitGroup():
    gname = raw_input('enter group name>')
    msg = json.dumps({
        'c':'EXIT_G',
        'user':user,
        'gname':gname
    })
    ws.send(msg)

def pullUsersInGroup():
    clients = raw_input("enter clients split by ' '>")
    clients_list = clients.split(' ')
    msg = json.dumps({
        'c':'PULL_US',
        'master':user,
        'clients':clients_list
    })
    ws.send(msg)

def accept():
    gname = raw_input('enter group name>')
    msg = json.dumps({
        'c':'ACCEPT',
        'gname':gname
    })
    ws.send(msg)

def pullUsersInExistGroup():
    gname = raw_input('enter group name>')
    clients = raw_input('enter clients>')
    clients_list = clients.split(' ')
    msg = json.dumps({
        'c':'PULL_IN_G',
        'gname':gname,
        'clients':clients_list
    })
    ws.send(msg)

def getRecord():
    gname = raw_input('enter group name>')
    msg = json.dumps({
        'c':'GET_RECORD',
        'gname':gname,
        'stime':time.time(),
        'limit':30
    })
    ws.send(msg)

def shake():
    msg = json.dumps({
        'c': 'SHAKE',
        'user': user,
        })
    ws.send(msg)

def getUserGroups():
    msg = json.dumps({
        'c':'USER_GROUPS',
        'user':user
        })
    ws.send(msg)

def getGroupUsers():
    gname = raw_input('enter group name>')
    msg = json.dumps({
        'c':'GROUP_USERS',
        'gname':gname
        })
    ws.send(msg)


def on_open(ws):
    def run(*args):
        while(1):
            print """ SHOP_GNAME, ENTR_SHOP, CHAT_M, EXIT_G, PULL_US, ACCEPT, PULL_IN_G, GET_RECORD, USER_GROUPS,GROUP_USERS"""
            command = raw_input("enter your command:")
            if command == 'SHOP_GNAME':
                sendShopGname()
            if command == 'ENTR_SHOP':
                enterShop()
            if command == 'CHAT_M':
                chat()
            if command == 'EXIT_G':
                exitGroup()
            if command == 'PULL_US':
                pullUsersInGroup()
            if command == 'ACCEPT':
                accept()
            if command == 'PULL_IN_G':
                pullUsersInExistGroup()
            if command == 'GET_RECORD':
                getRecord()
            if command == 'SHAKE':
                shake()
            if command == 'USER_GROUPS':
                getUserGroups()
            if command == 'GROUP_USERS':
                getGroupUsers()

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    user = sys.argv[1]
    passwd = sys.argv[2]
    m = hashlib.md5()
    m.update(passwd)
    if not user:
        user = "fht"
    print "hello",user
    ws = websocket.WebSocketApp("ws://115.28.143.67:8889/chat/?u="+ user + "&p=" +m.hexdigest(),
    on_message = on_message,
    on_error = on_error,
    on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()

