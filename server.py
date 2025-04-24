import socket
import threading
import socketserver
import datetime

from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import threading
import requests

import message_coder

threadlock_xml = threading.Lock()
# template and some marked of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

#user class
class user:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

# universal server functions


def create_xml_file():
    try:
        baseText = ET.Element("data")
        baseTree = ET.ElementTree(element=baseText)
        baseTree.write("./xmlData.xml")
        return ET.parse('./xmlData.xml')
    except FileExistsError:
        print("XML file already exists")
        return None
    
def save_users():
    global threadlock_xml, listOfUsers
    pass

def load_users():
    global threadlock_xml, listOfUsers
    pass

def write_user_data(username, password): # handles adding user to data base. 
    global threadlock_xml

    userElement = ET.Element("username")
    userElement.set("password", password)

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        return

    root = tree.getroot()
    userNode = root.find("users")

    if userNode == None:
        userNode = ET.Element("users")
        root.append(userNode)
    if (userNode.find(username) == None): #writes new user only if user doesn't exist (this should never be run when user already exist but is here to ensure that)
        userNode.append(userElement)
        tree.write('./xmlData.xml')

    threadlock_xml.release()

def write_message(sender_name, to, message):
    global threadlock_xml

    success = False #return value if operation succeeded

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        return False

    root = tree.getroot()
    userNode = root.find("users")

    if userNode != None: # makes sure there is users
        receiver = userNode.find(to)
        if(receiver != None):
            messages_node = receiver.find("messages")
            if(messages_node == None):
                messages_node = ET.Element("messages")
                receiver.append(messages_node)
            category_node = messages_node.find(sender_name)
            if(category_node == None):
                category_node = ET.Element(sender_name)
                messages_node.append(category_node)
            message_node = ET.Element("message")
            message_node.text = message
            category_node.append(message_node)
            success = True

    tree.write('./xmlData.xml')

    threadlock_xml.release()
    return success

def read_messages(username):
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        return False
    
    root = tree.getroot()
    usersNode = root.find("users")
    if(usersNode == None):
        threadlock_xml.release()
        return False
    
    userNode = usersNode.find(username)
    if(userNode == None):
        threadlock_xml.release()
        return False
    
    messagesNode = userNode.find("messages")
    return ET.tostring(messagesNode)

def attack_wizard(attacker, defender):
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        return False
    
    root = tree.getroot()
    users_node = root.find("users")
    if(users_node == None):
        threadlock_xml.release()
        return False
    
    user_node = users_node.find(defender)
    if(user_node == None):
        threadlock_xml.release()
        return False
    
    log_node = user_node.find("log")
    if(log_node == None):
        log_node = ET.Element("log")
    if(log_node.find(attacker)):
        threadlock_xml.release()
        return False
    attack_node = ET.Element(attacker)
    log_node.append(attack_node)

    if(log_node.__len__ >= 5): # user "dies"
        users_node.remove(user_node)
        
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
    if(log_node.__len__ >= 5): # this is here to update the dynamic memory and correctly return a value
        return "dead"
    else:
        return True



def write_xml_topic(topic, note, text, datetime): #old code 
    global threadlock_xml
    threadlock_xml.acquire()

    #stuff that doesn't need xml file 
    topicElement = ET.Element("topic")
    noteElement = ET.Element("note")

    topicElement.set("name", topic)
    noteElement.set("name", note)
    
    textElement = ET.Element("text")
    textElement.text = text
    noteElement.append(textElement)

    datetimeElement = ET.Element("datetime")
    datetimeElement.text = str(datetime)
    noteElement.append(datetimeElement)


    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        return

    if(tree == None):
        print("gettin a file to read failed")
        return 
    
    root = tree.getroot()
    topicExist = False
    for node in root.iter("topic"):
        if node.attrib["name"] == topic:
            topicExist = True
            node.append(noteElement)
            break
    
    if(not topicExist):
        topicElement.append(noteElement)
        root.append(topicElement)
    tree.write("xmlData.xml")
    threadlock_xml.release()


# server functions

# Rest section



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    listOfUsers = [] #store whole user from xml to memory
    listOfActiveUsers = [] #store only username
    def userExists(self, name: str, password: str) -> bool:
        found = False
        nameExist = False
        for a_user in self.listOfUsers:
            if(a_user.username == name and a_user.password == password):
                found = True
                nameExist = True
                break
            elif(a_user.username == name and a_user.password != password):
                nameExist = True
                break
        return found, nameExist
    
    def form_response(self, message0 = "MessageError", message1 = ""): #message 0 is meant for mechanical messages, message 1 is for user. Message 1 is not always needed.
        return bytes(message_coder.encode(message0, message1), 'ascii')
     
    def handle(self):
        
        run = True
        while run:
            data = str(self.request.recv(1024), 'ascii')
            if(len(data) == 0):
                continue
            parsedData = message_coder.decode(data) # ideally index 0 is username, 1 is password, 2 is action, and rest is action specific.
            try:
                name = parsedData[0]
                password = parsedData[1]
                action = parsedData[2]
                other = []
                if(len(parsedData) >= 3):
                    other = parsedData[3::]
            except IndexError:
                print("invalid message arrived,\ndata:", data, "\nparcedData:", parsedData)
                continue
            userAuth, nameExists = self.userExists(name, password)
            
                
            if(action == "test"): # test from documentation
                cur_thread = threading.current_thread()
                response = self.form_response("ok", "{}: {}".format(cur_thread.name, data).upper())
            
            elif(action == "login"): # login
                if(not userAuth):
                    if(nameExists):
                        response = self.form_response("autherror", "Incorrect password")
                    else:
                        response = self.form_response("usernamenotfound", "Incorrect username")  
                else:
                    if(name not in self.listOfActiveUsers):
                        self.listOfActiveUsers.append(name)
                    response = self.form_response("ok", "U R now connected  to the wizard's counsil: " + name)

            elif(action == "register"): # register
                if(nameExists):
                    response = self.form_response("usernametaken", "Username is already taken")
                else:
                    self.listOfUsers.append(user(name, password))
                    self.listOfActiveUsers.append(name)
                    response = self.form_response("ok", "U R now connected  to the wizard's counsil: " + name + " " + password)

            elif(userAuth): # security is our passion. Only logged in users can access these actions.

                if(action == "send_global"): # send message global
                    
                    response = self.form_response("ok", "Message send")

                elif(action == "send_private"): # send message private, other 0 = to, 1 = message
                    
                    response = self.form_response("ok", "Message send to " + other[0])
                elif(action == "read"): # read messages

                     response = self.form_response("ok", )
                elif(action == "send_event"): # 
                    pass
                elif(action == "cur_online"): # 
                    pass
                elif(action == "cur_events"): # 
                    pass
                elif(action == "join_event"): # 
                    pass
                elif(action == "attack"): # 
                    pass
                elif(action == "disconnect"): # disconnect
                    for a_user in self.listOfActiveUsers:
                        if (a_user == name):
                            self.listOfActiveUsers.remove(a_user)
                    break
                else:
                    response = self.form_response("invalidaction", "Invalid action, problem in client software and server mail wizard")
            else:
                response = self.form_response("autherror", "Wizard is not authorizised corretly, login again")
            self.request.sendall(response) # response should be that 0 index has mechanical message and 1 index user readable message.

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): # something from documentation, needs to be.
    pass

# Rest section

# RPC section

def is_even(n):
    return n % 2 == 0

def receive_message(topic, note, text, datetime):
    thread = threading.Thread(target=write_xml_topic, args=[topic, note, text, datetime])
    thread.start()

def send_topic(topic):
    global threadlock_xml
    threadlock_xml.acquire()
    tree = ET.parse('./xmlData.xml')
    root = tree.getroot()
    for child in root.iter("topic"):
        if(child.attrib["name"] == topic):
            threadlock_xml.release()
            return ET.tostring(child)
    threadlock_xml.release()
    return "No topic found" 

def query_wikipedia(topic):
    # https://www.mediawiki.org/wiki/API:Opensearch 
    S = requests.Session() 
    URL = "https://en.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "opensearch",
        "namespace": "0",
        "search": topic,
        "limit": "9",
        "format": "json"
    }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()

    return(DATA)

def add_article_to_topic(topic, article, datetime):
    thread = threading.Thread(target=write_xml_topic, args=[topic, "article", article, datetime])
    thread.start()

# registable functions


def open_connection():
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Listening on port 8000 for RPC requests...")
    return server


def register_functions(server):
    server.register_function(is_even, "is_even")
    server.register_function(receive_message, "send_message")
    server.register_function(send_topic, "read_topic")
    server.register_function(query_wikipedia, "query_wikipedia")
    server.register_function(add_article_to_topic, "add_article_to_topic")


# RPC section

# main

def main(): 
    HOST, PORT = "localhost", 5002
    
    rpcServer = open_connection()
    register_functions(rpcServer)

    rpc_server_thread = threading.Thread(target=rpcServer.serve_forever)
    rpc_server_thread.daemon = True
    rpc_server_thread.start()

    # from documentation
    restServer = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with restServer:
        # from documentation
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=restServer.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        
        input("press enter to exit\n")


if __name__ == "__main__":
    main()