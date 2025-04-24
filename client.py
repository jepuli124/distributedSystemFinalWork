import socket

import message_coder

# template and some of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

class client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.username = ""
        self.password = ""
    
    def intro(self):
        try:
            file = open("./introText.txt", "r")
            for line in file.readlines():
                print(line)
        except FileNotFoundError:
            print("welcome to\nWizard's\nDungeon")
            return

    def bye(self):
        try:
            file = open("./bye.txt", "r")
            for line in file.readlines():
                print(line)
        except FileNotFoundError:
            print("welcome to\nWizard's\nDungeon")
            return

    def send_to_server(self, *message) -> str:
        message_tuple = (self.username, self.password) + message # this is done due to package all of the properly for encoding.
        self.connection.send(bytes(message_coder.encode(message_tuple), 'ascii'))
        return message_coder.decode(str(self.connection.recv(1024), 'ascii'))
        

    def select_new_username_and_password(self):
        self.username = input("username: ")
        self.password = input("password: ")

    def login(self):
        self.select_new_username_and_password()
        response = self.send_to_server("login")
        if(response[0] == "usernametaken"):
            print("username taken, select another one")
            return self.login()
        if(response[0] == "usernamenotfound"):
            answer = input("User doesn't exist, do you want to register? (Yes/No)")
            if(answer[0].lower() == "y"):
                return self.register()
            else:
                return self.login()
        if(response[0] != "ok"):
            print("something went wrong, retry")
            return self.login()
        else:
            print("login successful: ", response[1])

    def register(self):
        response = self.send_to_server("register")
        print("response from server:", response[1])
        if(response[0] == "ok"):
            print("successfully registered", self.username, self.password)
            return
        elif(response[0] == "usernametaken"):
            print("Username was taken, select another one")
            self.select_new_username_and_password()
        else:
            print("server error", response[1])
        return self.register()

    def sendMessageToAll(self):
        message = input("input message: ")
        response = self.send_to_server("send_global", message)
        print("response from server:", response[1])
    
    def sendMessageToEvent(self):
        message = input("input message: ")
        to = input("input event name: ")
        response = self.send_to_server("send_event", to, message)
        print("response from server:", response[1])

    def sendPrivateMessage(self):
        message = input("input message: ")
        to = input("input receiver's nickname: ")
        response = self.send_to_server("send_private", to, message)
        print("response from server:", response[1])

    def attackAnotherWizard(self):
        response = self.send_to_server("cur_online")
        print("People online: ", response[1])
        to = input("input who are you going to punch?: ")
        response = self.send_to_server("attack", to)
        print("response from server:", response[1])

    def joinEvent(self):
        response = self.send_to_server("cur_events")
        print("Current events: ", response[1])
        to = input("Which are you going to join? Name of event/No: ")
        if(to.lower() == "no"):
            return
        response = self.send_to_server("join_event", to)
        print("response from server:", response[1])

    def readMessages(self):
        response = self.send_to_server("read")
        print("response from server:", response[1])

    def disconnect(self):
        self.send_to_server("disconnect")
        self.connection.close()

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))

if __name__ == "__main__":
    cl = client("127.0.0.1", 5002)
    cl.connect()
    cl.intro()
    cl.login()
    while True:
        print("logged as:", cl.username)
        userInput = input("MG: send global message, MP: send private message, ME: send message to event, JE: join to event, D: disconnect, A: attack wizard that's online: \n")
        print()
        if(userInput == "MG"):
            cl.sendMessageToAll()
        elif(userInput == "MP"):
            cl.sendPrivateMessage()
        elif(userInput == "ME"):
            cl.sendMessageToEvent()
        elif(userInput == "JE"):
            cl.joinEvent()
        elif(userInput == "D"):
            cl.disconnect()
            break
        elif(userInput == "A"):
            cl.attackAnotherWizard()
        else:
            print("\nNo action was done (invalid input) -> reading messages: \n")
        cl.readMessages()
        print()
    cl.bye()