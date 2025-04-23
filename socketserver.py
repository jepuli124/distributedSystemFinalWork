import socket
import threading
import socketserver

# template and some marked of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

class user:
    def __init__(self, username: str):
        self.username = username
        self.messages = []

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        run = True
        while run:
            data = str(self.request.recv(1024), 'ascii')
            if(data[0] == "T"): # test from documentation
                cur_thread = threading.current_thread()
                response = bytes("{}: {}".format(cur_thread.name, data), 'ascii').upper()
            
            elif(data[0] == "1"):
                if(data[1::] in listOfUsers):
                    response = bytes("usernametaken", 'ascii')
                else:
                    listOfUsers.append(user(data[1::]))
                    response = bytes("ok: " + data[1::], 'ascii')
            elif(data[0] == "2"):
                for a_user in listOfUsers:
                    a_user.messages.append(data[1::]) 
                response = bytes("ok: " + data[1::], 'ascii')
            elif(data[0] == "3"):
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
            elif(data[0] == "4"):
                for a_user in listOfUsers:
                    if (a_user.username == data[1::]):
                        response = bytes(str(a_user.messages), 'ascii')
                        break
                    else:
                        response = bytes("Server error: " + data, 'ascii')
            elif(data[0] == "5"):
                break
            else:
                response = bytes("Server error: " + data, 'ascii')
            self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


listOfUsers = []
if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 5002
    
    # from documentation
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        # from documentation
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        
        input("press enter to exit\n")


    
