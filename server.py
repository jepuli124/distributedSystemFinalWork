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
    
def save_users(list_of_users):
    global threadlock_xml
    

    user_nodes = []
    for a_user in list_of_users:
        temp_user = ET.Element("user")
        temp_user.text = a_user.username

        temp_pass = ET.Element("password")
        temp_pass.text = a_user.password

        temp_messages = ET.Element("messages")

        temp_user.append(temp_pass)
        temp_user.append(temp_messages)

        user_nodes.append(temp_user)

    threadlock_xml.acquire()
    
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False

    root = tree.getroot()
    usersNode = root.find("users")

    if usersNode == None:
        usersNode = ET.Element("users")
        root.append(usersNode)
    else:
        usersNode.clear()
    
    for node in user_nodes:
        usersNode.append(node)

    tree.write('./xmlData.xml')

    threadlock_xml.release()
    return True

def load_users():
    global threadlock_xml
    list_of_users = []

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return []

    root = tree.getroot()
    usersNode = root.find("users")

    if usersNode == None:
        usersNode = ET.Element("users")
        root.append(usersNode)
    
    for a_user in usersNode.iter("user"):
        a_password = a_user.find("password")
        list_of_users.append(user(a_user.text, a_password.text))

    threadlock_xml.release()

    return list_of_users

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
        threadlock_xml.release()
        return False

    root = tree.getroot()
    userNode = root.find("users")

    if userNode == None:
        userNode = ET.Element("users")
        root.append(userNode)
    found = False
    for a_user in userNode.iter():
        if(a_user.text == username):
            found = True
            break
    if(not found): #writes new user only if user doesn't exist (this should never be run when user already exist but is here to ensure that)
        userNode.append(userElement)
        tree.write('./xmlData.xml')

    threadlock_xml.release()
    return True

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
        threadlock_xml.release()
        return False

    root = tree.getroot()
    userNode = root.find("users")

    if userNode != None: # makes sure there is users
        receiver = None  
        for a_user in userNode.iter():
            if(a_user.text == to):
                receiver = a_user
                break
        if(receiver != None):
            messages_node = receiver.find("messages")
            if(messages_node == None):
                messages_node = ET.Element("messages")
                receiver.append(messages_node)
            category_node = None
            for category in messages_node.iter("category"):
                if(category.text == sender_name):
                    category_node = category
            if(category_node == None):
                category_node = ET.Element("category")
                category_node.text = sender_name
                messages_node.append(category_node)
            message_node = ET.Element("message")
            message_node.text = message
            category_node.append(message_node)
            success = True
        else:
            print("receiver error")
    else:
        print("users error")

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
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    usersNode = root.find("users")
    if(usersNode == None):
        threadlock_xml.release()
        return False
    
    userNode = None
    for a_user in usersNode.iter("user"):
        if(a_user.text == username):
            userNode = a_user
            break

    if(userNode == None):
        threadlock_xml.release()
        return False
    
    messagesNode = userNode.find("messages")

    messages = ""
    for categoryNode in messagesNode.iter("category"):
        messages += categoryNode.text + "\n;"
        for message in categoryNode.iter("message"):
            messages += message.text + ";"
        messages += "\n;"

    threadlock_xml.release()
    return messages

def users_of_an_event(eventName):
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    events_node = root.find("events")
    if(events_node == None):
        threadlock_xml.release()
        return False
    
    event_node = None
    for event in events_node.iter("event"):
        if(event.text == eventName):
            event_node = event
            break

    if(event_node == None):
        threadlock_xml.release()
        return False
    
    listOfUsersInEvent = []
    
    for user in event_node.iter("user"): 
        listOfUsersInEvent.append(user.text)
        
    threadlock_xml.release()
    return listOfUsersInEvent

def all_events():
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    events_node = root.find("events")
    if(events_node == None):
        threadlock_xml.release()
        return False
    
    listOfEvents = []
    
    for event in events_node.iter("event"):
        listOfEvents.append(event.text)
        
    threadlock_xml.release()
    return listOfEvents

def add_event(event_name):
    global threadlock_xml

    event_node = ET.Element("event")
    users_node = ET.Element("users")
    event_node.text = event_name

    event_node.append(users_node)

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    events_node = root.find("events")
    if(events_node == None):
        events_node = ET.Element("events")
        root.append(events_node)
    
    events_node.append(event_node)
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
    return True

def join_event(username, event_name):
    global threadlock_xml

    user_node = ET.Element("user")
    user_node.text = username

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    events_node = root.find("events")
    if(events_node == None):
        threadlock_xml.release()
        return False
    
    event_node = None
    for event in events_node.iter("event"):
        if(event.text == event_name):
            event_node = event
    if(event_node == None):
        threadlock_xml.release()
        return False
    
    users_node = event_node.find("users")
    if(users_node == None):
        threadlock_xml.release()
        return False

    users_node.append(user_node)
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
    return True


def attack_wizard(attacker, defender): # better than snapchat. Here wizards may punch each other to show "dislike", if you get punched enough (here 5 times) your acconut is deleted. 
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot()
    users_node = root.find("users")
    if(users_node == None):
        threadlock_xml.release()
        return False
    
    user_node = None
    for a_user in users_node.iter("user"):
        if(a_user.text == defender):
            user_node = a_user
            break
        
    if(user_node == None):
        threadlock_xml.release()
        return False
    
    log_node = user_node.find("log")
    if(log_node == None):
        log_node = ET.Element("log")
        user_node.append(log_node)
        print("log not found")
    if(log_node.find(attacker)): # same user can't punch another multiple times
        threadlock_xml.release()
        return False
    attack_node = ET.Element(attacker)
    log_node.append(attack_node)

    if(log_node.__len__() >= 5): # user "dies" -> account is deleted. 
        users_node.remove(user_node)
        
    
    tree.write('./xmlData.xml')
    if(log_node.__len__() >= 5): # this is here to update the dynamic memory and correctly return a value
        threadlock_xml.release()
        return "dead"
    else:
        threadlock_xml.release()
        return True

def delete_account(account_name): # delete account
    global threadlock_xml

    threadlock_xml.acquire()
    try:
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False
    
    root = tree.getroot() 
    for a_user in root.iter("user"): # deletes all user references to that user 
        if(a_user.text == account_name):
            root.remove(a_user)
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
    return True

def release_thread_lock(): #admin action if a crash causes threadlock to be hold locked
    global threadlock_xml
    threadlock_xml.release()
    return True

# server functions

# Rest section



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    listOfUsers = load_users() #store whole user from xml to memory
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
            if(len(data) == 0): # happens when connection is made, other cases shouldn't hit here.  
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
                    save_users(self.listOfUsers)
                    response = self.form_response("ok", "U R now connected  to the wizard's counsil: " + name + " " + password)
            elif(action == "disconnect"): # disconnect
                for a_user in self.listOfActiveUsers:
                    if (a_user == name):
                        self.listOfActiveUsers.remove(a_user)
                break
            elif(userAuth): # security is our passion. Only logged in users can access these actions.
                
                if(action == "send_global"): # send message global, other 0 = message
                    for a_user in self.listOfUsers:
                        write_message(name, a_user.username, other[0])
                    response = self.form_response("ok", "Message send")

                elif(action == "send_private"): # send message private, other 0 = to, 1 = message
                    if(write_message(name, other[0], other[1])):
                        response = self.form_response("ok", "Message send to " + other[0])
                    else:
                        response = self.form_response("messagefail", "Failed to message " + other[0])
                elif(action == "read"): # read messages
                    response = self.form_response("ok", read_messages(name))

                elif(action == "send_event"): # send message to all in the event channel, other, 0 = event, 1 = message
                    temp_users = users_of_an_event(other[0])
                    if(temp_users):
                        for a_user in temp_users:
                            write_message(other[0], a_user, other[1])
                        response = self.form_response("ok", "Message send")
                    else:
                        response = self.form_response("eventnotfound", "Event couldn't be found")

                elif(action == "cur_online"): # current online wizards
                    response = self.form_response("ok", self.listOfActiveUsers)

                elif(action == "cur_events"): # current events
                    temp = all_events()
                    if(temp):
                        response = self.form_response("ok", temp)
                    else:
                        response = self.form_response("eventsnotfound", "events not found")
                elif(action == "add_event"): # add event other 0 = name of the event
                    if(add_event(other[0])):
                        response = self.form_response("ok", "Event created")
                    else:
                        response = self.form_response("unknown", "Event not created")

                elif(action == "join_event"): # other [0] = event name
                    if(join_event(name, other[0])):
                        response = self.form_response("ok", "Joined to event")
                    else:
                        response = self.form_response("eventnotfound", "Event not found")

                elif(action == "attack"): # other 0 = who you are going to punch
                    result = attack_wizard(name, other[0])
                    if(result):
                        if(result == "dead"):
                            self.listOfActiveUsers.remove(other[0])
                            for x, a_user in enumerate(self.listOfUsers):
                                if(a_user.username == other[0]):
                                    self.listOfUsers.pop(x)
                                    break
                            response = self.form_response("ok", "You threw a glorious punch at " + other[0] + "and they are OUT")
                        else:
                            response = self.form_response("ok", "You threw a glorious punch at " + other[0])
                    else:
                        response = self.form_response("usernotfound", "You threw a glorious punch at NOTHING (either user doesn't exist or you already punched them)")
                else:
                    response = self.form_response("invalidaction", "Invalid action, problem in client software and server mail wizard")
            else:
                response = self.form_response("autherror", "Wizard is not authorizised corretly, login again")
            self.request.sendall(response) # response should be that 0 index has mechanical message and 1 index user readable message.

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): # something from documentation, needs to be.
    pass

# Rest section

# RPC section


def delete_user(username): #admin action to delete user
    thread = threading.Thread(target=delete_account, args=[username])
    thread.start()

def read_user_messages(username): #admin action to read user
    thread = threading.Thread(target=read_messages, args=[username])
    thread.start()

def release_threadlock_admin(): #admin action to release the threadlock
    thread = threading.Thread(target=release_thread_lock, args=[])
    thread.start()

def query_wikipedia(topic): # old codes
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



# registable functions

# RPC setup and configurable values

def open_connection():
    port = 8000
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    print("Listening on port " + str(port) + " for RPC requests...")
    return server


def register_functions(server):
    server.register_function(delete_user, "delete_user")
    server.register_function(read_user_messages, "read_users_messages")



# RPC section

# main

def main(): 
    HOST, PORT = "localhost", 5002 # for client rest side of the server
    
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