import xmlrpc.client
import message_coder

# communication

def open_connection():
    return xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

def delete_user(proxy): # deletes user.
    username = input("who to delete?:")

    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        proxy.delete_user(username)
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
    except xmlrpc.client.ProtocolError as err: 
        print("A protocol error occurred")
        print("URL: %s" % err.url)
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)

def read_messages(proxy): # reads all messages that target user has received.
    username = input("whose messages?:")
    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        messages = proxy.users_messages(username)
        response = message_coder.decode(messages)
        for message in response[1::]:
            print(message)
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
    except xmlrpc.client.ProtocolError as err: 
        print("A protocol error occurred")
        print("URL: %s" % err.url)
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)

def read_ancient_knowledge(proxy): # search most ancient, secret, and cryptic knowledge from library of babel (mostly wizardly nonsense).
    hexagon = input("which hexagon, only (a-z, 0-9)?")
    wall = input("which hexagon, only (1-4)?")
    shelf = input("which hexagon, only (1-5)?")
    volume = input("which hexagon, only (1-32)?")
    data = None
    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        data = proxy.secret_wizard_knowlegde((hexagon, wall, shelf, volume))

        print(data)
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
    except xmlrpc.client.ProtocolError as err: 
        print("A protocol error occurred")
        print("URL: %s" % err.url)
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)
    return True

def release_threadlock(proxy): # in case of wizard (client) crash, release threadlock to let server contiune without restarting


    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        proxy.release_threadlock()
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
    except xmlrpc.client.ProtocolError as err: 
        print("A protocol error occurred")
        print("URL: %s" % err.url)
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)

# main loop

def main():
    proxy = open_connection() # open connection
    
    while True: # main loop
        userChoice = input("\nDelete user (1), Read messages (2), search ancient knowledge (3), release threadlock (4), exit (e):\n")
        if(len(userChoice) == 0): # decision tree
            print("plz make a input")
            continue
        if(userChoice[0] == "1"):
            delete_user(proxy)
        elif(userChoice[0] == "2"):
            read_messages(proxy)
        elif(userChoice[0] == "3"):
            read_ancient_knowledge(proxy)
        elif(userChoice[0] == "4"):
            release_threadlock(proxy)
        elif(userChoice[0] == "e"):
            break
        else:
            print("invalid input")
    return 0
if __name__ == "__main__":
   main()
# main loop
