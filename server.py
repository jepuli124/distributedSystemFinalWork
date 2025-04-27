import socket
import threading
import socketserver
import datetime

from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import threading
import requests

import message_coder

# code (programming) is a beautiful form of commands to modern rocks (cpu:s) and we here at wizard's closet treat it as such with atmost respect.

threadlock_xml = threading.Lock()
# some marked of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

#user class
class user: # simple class to store data
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

# universal server functions


def create_xml_file(): # in case of xml file doesn't exist.
    try:
        baseText = ET.Element("data")
        baseTree = ET.ElementTree(element=baseText)
        baseTree.write("./xmlData.xml")
        return ET.parse('./xmlData.xml')
    except FileExistsError: 
        print("XML file already exists")
        return None
    
def save_users(list_of_users): # save users from RAM memory to xml file  
    global threadlock_xml
    
    user_nodes = []
    for a_user in list_of_users: # create necessary elements before acquiring threadlock to reduce unnecessary threadlock keep time.
        temp_user = ET.Element("user")
        temp_user.text = a_user.username

        temp_pass = ET.Element("password")
        temp_pass.text = a_user.password

        temp_messages = ET.Element("messages")

        temp_user.append(temp_pass)
        temp_user.append(temp_messages)

        user_nodes.append(temp_user)

    threadlock_xml.acquire()
    
    try: # try accessing xmlData file
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError: # if not found, create new one.
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError: # if the file is damaged, panic in wizard
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return False

    root = tree.getroot() # get first node
    usersNode = root.find("users") # get users node

    if usersNode == None: # if it doesn't exist create one
        usersNode = ET.Element("users")
        root.append(usersNode)
    else: # if it exist, empty it. 
        usersNode.clear() 
    
    for node in user_nodes: # add users to it
        usersNode.append(node)

    tree.write('./xmlData.xml') # write it down

    threadlock_xml.release() # release lock
    return True # return true for success.

def load_users(): # load users to from xml to RAM memory
    global threadlock_xml
    list_of_users = [] 

    threadlock_xml.acquire() 
    try: # access to xml file
        tree = ET.parse('./xmlData.xml')
    except FileNotFoundError:
        print("File not found: creating a new file")
        tree = create_xml_file()
    except ET.ParseError:
        print("\noh noes, parse error\n")
        threadlock_xml.release()
        return []

    root = tree.getroot() # get first node
    usersNode = root.find("users") # get users node

    if usersNode == None: # make sure it exist
        usersNode = ET.Element("users")
        root.append(usersNode)
    
    for a_user in usersNode.iter("user"): # go through all user nodes and store them to ram 
        a_password = a_user.find("password")
        list_of_users.append(user(a_user.text, a_password.text))

    threadlock_xml.release()

    return list_of_users

def write_user_data(username, password): # handles adding a singular user to data base. 
    global threadlock_xml

    userElement = ET.Element("user") # create user element
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

    root = tree.getroot() # get first node
    userNode = root.find("users")

    if userNode == None: 
        userNode = ET.Element("users")
        root.append(userNode)
    found = False
    for a_user in userNode.iter("user"): # go through all user nodes to find if it already exists
        if(a_user.text == username):
            found = True
            break
    if(not found): #writes new user only if user doesn't exist (this should never be run when user already exist but is here to ensure that)
        userNode.append(userElement)
        tree.write('./xmlData.xml')

    threadlock_xml.release()
    return True

def write_message(sender_name, to, message): # handles all message writing
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
        for a_user in userNode.iter("user"): # find the receiving wizard  
            if(a_user.text == to):
                receiver = a_user
                break
        if(receiver != None): # check if it was found
            messages_node = receiver.find("messages") # go through messages tree to find correct place for the message
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
            message_node.text = message # write the message
            category_node.append(message_node)
            success = True # mark that operation was success
        else:
            print("receiver error")
    else:
        print("users error")

    tree.write('./xmlData.xml')

    threadlock_xml.release()
    return success

def read_messages(username): # processes all messages user has received and returns them.
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
    for categoryNode in messagesNode.iter("category"): # the messages are encoded here to make the message decoder decode them properly
        messages += categoryNode.text + "\n;"
        for message in categoryNode.iter("message"):
            messages += message.text + ";"
        messages += "\n;"

    threadlock_xml.release()
    return messages

def users_of_an_event(eventName): # gets all users from a event and returns them in a list
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

def all_events(): # gets all events
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

def add_event(event_name): # add a event 
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

def join_event(username, event_name): # joins a user to event
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


def attack_wizard(attacker, defender): # better than snapchat. Here wizards may punch each other to show "dislike", if they get punched enough (here 5 times) their acconut is deleted. 
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
    
    log_node = user_node.find("log") # writes a punches to log file 
    if(log_node == None):
        log_node = ET.Element("log")
        user_node.append(log_node)
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
    users_node = root.find("users")
    if(users_node == None):
        threadlock_xml.release()
        return
    for a_user in users_node.iter("user"): # deletes user 
        if(a_user.text == account_name):
            users_node.remove(a_user)
    
    tree.write('./xmlData.xml')
    threadlock_xml.release()
    return True

def release_thread_lock(): #admin action if a crash causes threadlock to be hold locked
    global threadlock_xml
    try:
        threadlock_xml.release()
    except RuntimeError:
        print("threadlock was already free")
    return True



# Rest section



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler): # class for client connection
    listOfUsers = load_users() #store whole user from xml to memory
    listOfActiveUsers = [] #store only username
    def userExists(self, name: str, password: str) -> bool: # checks if username exist and if given info matches that
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
     
    def handle(self): # main handles of client requests
        
        run = True
        while run: # main loop
            data = str(self.request.recv(1024), 'ascii')
            if(len(data) == 0): # happens when connection is made, other cases shouldn't hit here.  
                continue
            parsedData = message_coder.decode(data) # ideally index 0 is username, 1 is password, 2 is action, and rest is action specific.
            try: # tries parcing client request
                name = parsedData[0]
                password = parsedData[1]
                action = parsedData[2]
                other = []
                if(len(parsedData) >= 3):
                    other = parsedData[3::]
            except IndexError:
                print("invalid message arrived,\ndata:", data, "\nparcedData:", parsedData)
                continue
            userAuth, nameExists = self.userExists(name, password) # checks if username exist and if passwords match
            
                
            if(action == "test"): # test from documentation, currently not used
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
                    response = self.form_response("ok", "U R now connected  to the wizard's counsil: " + name )
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
                        if(result == "dead"): # if user account is deleted from a punch, it is removed from ram
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



# custom thread to return values from here: https://medium.com/@birenmer/threading-the-needle-returning-values-from-python-threads-with-ease-ace21193c148

class CustomThread(threading.Thread): # this makes a thread wrapper that holds values from target function given in to it.
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        # Initializing the Thread class
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    # Overriding the Thread.run function
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return


# RPC section


def delete_user(username): #admin action to delete user
    thread = threading.Thread(target=delete_account, args=[username])
    thread.start()

def read_user_messages(username): #admin action to read user
    thread = CustomThread(target=read_messages, args=[username])
    thread.start()
    return(message_coder.encode(thread.join()))

def release_threadlock_admin(): #admin action to release the threadlock
    thread = threading.Thread(target=release_thread_lock, args=[])
    thread.start()

def read_secret_wizard_knowlegde(params): # old texts from library of babel
    # https://libraryofbabel.info/
    # some code from https://github.com/victor-cortez/Library-of-Babel-Python-API/blob/master/pybel.py 
    hexagon, wall, shelf, volume = params
    if(int(wall) > 4): # makes sure the params are in correct range 
        wall = "4"
    elif(int(wall) < 1):
        wall = "1"
    
    if(int(shelf) > 5):
        shelf = "5"
    elif(int(shelf) < 1):
        shelf = "1"

    if(int(volume) > 32):
        volume = "32"
    elif(int(volume) < 1):
        volume = "1"
    
    if int(volume) <= 9:
        volume = "0" + volume

    form = {"hex":hexagon,"wall":wall,"shelf":shelf,"volume":volume,"page":"1","title":"startofthetext"}
    url = "https://libraryofbabel.info/download.cgi"
    text = requests.post(url,data=form) # makes the request to the library of babel.


    return(text)



# registable functions

# RPC setup and configurable values

def open_connection(): # connection
    port = 8000
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    print("Listening on port " + str(port) + " for RPC requests...")
    return server


def register_functions(server): # RPC functions
    server.register_function(delete_user, "delete_user")
    server.register_function(read_user_messages, "users_messages")
    server.register_function(read_secret_wizard_knowlegde, "secret_wizard_knowlegde")
    server.register_function(release_threadlock_admin, "release_threadlock")


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