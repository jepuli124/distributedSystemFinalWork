import client
from threading import Thread

#thread

def runThread(x):
    try:
        proxy = client.open_connection()

        userInputSend = client.userInputObject()
        userInputSend.topic = "n clients3"
        userInputSend.note = "test " + str(x) 
        userInputSend.text = "woah"

        client.send_message(proxy, userInputSend)
    except ConnectionResetError:
        return runThread(x)
    return 0

#thread

# main loop

def main():
    
    threadList = []

    for x in range(500):
        thread = Thread(target=runThread, args=[x])
        threadList.append(thread)
        
    for thread in threadList:
        thread.start()

    for thread in threadList:
        thread.join()

    return 0

if __name__ == "__main__":
   main()
# main loop