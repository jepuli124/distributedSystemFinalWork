# Echo client program
import socket

# template and some of code from documentation https://docs.python.org/3.9/library/socketserver.html#module-socketserver

ip, port = "127.0.0.1", 5002

def setNickname(connection):
    username = input("select your username:")
    connection.send(bytes("1" + username, 'ascii'))
    response = str(connection.recv(1024), 'ascii')
    print("response from server:", response)
    if(response == "usernametaken"):
        print("username taken, select another one")
        return setNickname(connection)
    return username

def sendMessageToAll(connection, username):
    message = input("input message: ")
    connection.send(bytes("2" + username + ": " + message , 'ascii'))
    response = str(connection.recv(1024), 'ascii')
    print("response from server:", response)

def sendPrivateMessage(connection, username):
    message = input("input message: ")
    to = input("input receiver's nickname: ")
    connection.send(bytes("3"+ to + "\n" + username + ": " + message, 'ascii'))
    response = str(connection.recv(1024), 'ascii')
    print("response from server:", response)

def readMessages(connection, username):
    connection.send(bytes("4" + username, 'ascii'))
    response = str(connection.recv(1024), 'ascii')
    print("response from server:", response)

def disconnect(connection):
    connection.send(bytes("5" + username, 'ascii'))
    connection.close()

def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock

def client(ip, port, message): # example from documentation
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes("T" + message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))
        sock.close()

if __name__ == "__main__":
    connection = connect()
    username = setNickname(connection)
    while True:
        userInput = input("1: send global message, 2: send private message, 3: disconnect:\n")
        print()
        if(userInput == "1"):
            sendMessageToAll(connection, username)
        elif(userInput == "2"):
            sendPrivateMessage(connection, username)
        elif(userInput == "3"):
            disconnect(connection)
            break
        else:
            print("\nNo action was done (invalid input) reading messages: \n")
        readMessages(connection, username)
        print()