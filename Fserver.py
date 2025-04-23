import socket
import threading
import socketserver
import datetime

from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import threading
import requests


threadlock_xml = threading.Lock()
# template and some marked of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

#user class
class user:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.lastLogin = datetime.datetime.now()

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
        print(defender, "died")
        users_node.remove(user_node)
        for x, user in enumerate(listOfUsers):
            if user.username == defender:
                listOfUsers.pop(x)
                break
        for x, user in enumerate(listOfActiveUsers):
            if user.username == defender:
                listOfActiveUsers.pop(x)
                break
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
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
    
    def usernamePasswordParser(self, data):
        name = ""
        password = ""
        index = 1
        for x, letter in enumerate(data[1::]):
            if letter == ';':
                index = x + 2
                break
            name += letter
        for letter in data[index::]:
            if letter == ';':
                break
            password += letter
        return name, password

    def userExists(self, name: str, password: str) -> bool:
        found = False
        for a_user in listOfUsers:
            if(a_user.username == name and a_user.password == password):
                found = True
                break
        return found
     
    def handle(self):
        run = True
        while run:
            data = str(self.request.recv(1024), 'ascii')

            name, password = self.usernamePasswordParser(data)
            userAuth = self.userExists(name, password)
            
                
            if(data[0] == "T"): # test from documentation
                cur_thread = threading.current_thread()
                response = bytes("{}: {}".format(cur_thread.name, data), 'ascii').upper()
            
            elif(data[0] == "1"): # login
                

                found = False
                for a_user in listOfActiveUsers:
                    if(a_user.username == name):
                        a_user.lastLogin = datetime.datetime.now()
                        found = True
                        break
                if not found:
                    listOfActiveUsers.append(user(name, password))
                response = bytes("Welcome to the wizard's lair: " + name, 'ascii')
            elif(data[0] == "2"): # register
                if(name in listOfUsers):
                    response = bytes("usernametaken", 'ascii')
                else:
                    listOfUsers.append(user(name, password))
                    listOfActiveUsers.append(user(name, password))
                    response = bytes("ok: " + name + " " + password, 'ascii')
            elif(userAuth): # security is our passion.

                if(data[0] == "3"): # send message global
                    for a_user in listOfUsers:
                        a_user.messages.append(data[1::]) 
                    response = bytes("ok: " + data[1::], 'ascii')
                elif(data[0] == "4"): # send message private
                    to = ""
                    index = 1
                    for x, letter in enumerate(data[1::]):
                        if letter == '\n':
                            index = x + 2
                            break
                        to += letter
                    for a_user in listOfUsers:
                        if a_user.username == to:
                            a_user.messages.append(data[index::]) 
                            break
                    response = bytes("ok: " + data[1::], 'ascii')
                elif(data[0] == "5"): # read messages
                    for a_user in listOfUsers:
                        if (a_user.username == data[1::]):
                            response = bytes(str(a_user.messages), 'ascii')
                            break
                        else:
                            response = bytes("Server error: " + data, 'ascii')
                elif(data[0] == "6"): # disconnect
                    for a_user in listOfUsers:
                        if (a_user.username == name):
                            listOfActiveUsers.remove(a_user)
                    break
                else:
                    response = bytes("Server error: " + data, 'ascii')
            else:
                response = bytes("Server error: " + data, 'ascii')
            self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
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

listOfUsers = []
listOfActiveUsers = []
if __name__ == "__main__":
    main()