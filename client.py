import socket

import message_coder

# template and some of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

class client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.username = ""
        self.password = ""
    
    def intro(self): # cool introduction for client
        try:
            file = open("./introText.txt", "r")
            for line in file.readlines():
                print(line)
        except FileNotFoundError:
            print("welcome to\nWizard's\nDungeon")
            return

    def bye(self): # nice message when client shutdowns
        try:
            file = open("./bye.txt", "r")
            for line in file.readlines():
                print(line)
        except FileNotFoundError:
            print("welcome to\nWizard's\nDungeon")
            return

    def send_to_server(self, *message) -> str: # simple function that handles almost all (not connection init) communication with server.
        message_tuple = (self.username, self.password) + message # this is done due to package all of the properly for encoding.
        try:
            self.connection.send(bytes(message_coder.encode(message_tuple), 'ascii'))
            return message_coder.decode(str(self.connection.recv(1024), 'ascii'))
        except:
            return ["messagefailure", "connection to server failed"]

    def select_new_username_and_password(self): # choose new username and password
        self.username = input("username: ")
        self.password = input("password: ")

    def login(self): # handles login.
        self.select_new_username_and_password()
        response = self.send_to_server("login")
        if(response[0] == "usernametaken"): # if username is taken, select another one, this should happen here.
            print("username taken, select another one")
            return self.login()
        if(response[0] == "usernamenotfound"): # if given username doesn't exist
            answer = input("User doesn't exist, do you want to register? (Yes/No)")
            if(answer[0].lower() == "y"):
                return self.register()
            else:
                return self.login()
        if(response[0] != "ok"): # if unexpected error occurs
            print("something went wrong, retry")
            return self.login()
        else:
            print("login successful: ", response[1])

    def register(self): # handles register
        response = self.send_to_server("register")
        print("response from server:", response[1])
        if(response[0] == "ok"): 
            print("successfully registered", self.username, self.password)
            return
        elif(response[0] == "usernametaken"): #if username is already taken
            print("Username was taken, select another one")
            self.select_new_username_and_password()
        else:
            print("server error", response[1])
        return self.register() # in all error cases, retry

    def sendMessageToAll(self): # send message to all
        message = input("input message: ")
        response = self.send_to_server("send_global", message)
        print("response from server:", response[1])
    
    def sendMessageToEvent(self): # send message all that are in a event
        message = input("input message: ")
        to = input("input event name: ")
        response = self.send_to_server("send_event", to, message)
        print("response from server:", response[1])

    def sendPrivateMessage(self): # send message to specific wizard.
        message = input("input message: ")
        to = input("input receiver's nickname: ")
        response = self.send_to_server("send_private", to, message)
        print("response from server:", response[1])

    def attackAnotherWizard(self): # punch another wizard. this might delete their account
        response = self.send_to_server("cur_online")
        print("People online: ", response[1])
        to = input("input who are you going to punch?: ")
        response = self.send_to_server("attack", to)
        print("response from server:", response[1])

    def addEvent(self): # add event
        message = input("input event name: ")
        response = self.send_to_server("add_event", message)
        print("response from server:", response[1])

    def joinEvent(self): # join event
        response = self.send_to_server("cur_events")
        print("Current events: ", response[1])
        to = input("Which are you going to join? Name of event/No: ")
        if(len(to) == 0): 
            return
        if(to[0].lower() == "n"):
            return
        response = self.send_to_server("join_event", to)
        print("response from server:", response[1])

    def readMessages(self): # read all messages you have received, here response contains more as actual messages are coming through.
        response = self.send_to_server("read")
        print("response from server:", )
        for message in response[1::]:
            print(message)

    def disconnect(self): # handles closing of connection
        self.send_to_server("disconnect")
        self.connection.close()

    def connect(self): # handles opening of connection
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))

def main(): # main
    cl = client("127.0.0.1", 5002) # create client
    cl.connect() # init connection
    cl.intro() # display intro
    cl.login() # login/register
    while True: # main loop
        print("logged as:", cl.username) # some info
        userInput = input("MG: send global message, MP: send private message, ME: send message to event, JE: join to event, AE: add event, D: disconnect, A: attack wizard that's online, R: read messages, L: logout: \n")
        print()
        if(userInput.upper() == "MG"): # choise tree, could have been switch case
            cl.sendMessageToAll()
        elif(userInput.upper() == "MP"):
            cl.sendPrivateMessage()
        elif(userInput.upper() == "ME"):
            cl.sendMessageToEvent()
        elif(userInput.upper() == "JE"):
            cl.joinEvent()
        elif(userInput.upper() == "AE"):
            cl.addEvent()
        elif(userInput.upper() == "D"):
            cl.disconnect()
            break
        elif(userInput.upper() == "A"):
            cl.attackAnotherWizard()
        elif(userInput.upper() == "R"):
            cl.readMessages()
        elif(userInput.upper() == "L"):
            cl.disconnect()
            return main()
        else:
            print("\nNo action was done (invalid input) \n")
        
        print()
    cl.bye()

if __name__ == "__main__":
    main()