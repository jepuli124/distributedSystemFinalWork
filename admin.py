import datetime
import xmlrpc.client
import xml.etree.ElementTree as ET

# data object

class userInputObject:
    topic:str = ""
    note:str = ""
    text:str = ""

# data object

# communication

def open_connection():
    return xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

def send_message(proxy, userInput: userInputObject):
    date = datetime.datetime.now()

    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        proxy.send_message(userInput.topic, userInput.note, userInput.text, date)
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

def read_topic(proxy, userInput: userInputObject):

    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        xml = proxy.read_topic(userInput.topic)
        xmlDoc = ET.XML(str(xml))
        for topic in xmlDoc.iter("topic"):
            print("\n Topic: " + topic.attrib["name"])
            for note in topic.iter("note"):
                print("\n title: " +note.attrib["name"] + "\n")
                text = note.find("text")
                datetime = note.find("datetime")
                print(text.text)
                print(datetime.text)

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

def search_wikipedia(proxy, userInput: userInputObject):
    data = None
    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        data = proxy.query_wikipedia(userInput.topic)
        #print("data[3]:", data[3])
        for topic in data:
            if(type(topic) == list):
                for note in topic:
                    if(len(note) != 0):
                        print(note)
            else:
                print("\n Topic: " + topic)
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
    return data

def add_wikipedia_article(proxy, wiki_number, data, userInput: userInputObject):
    date = datetime.datetime.now()

    try: # error handling from https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
        proxy.add_article_to_topic(userInput.topic, data[3][wiki_number-1], date)
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

# communication

# client stuff

def user_input_send() -> userInputObject:
    userInput = userInputObject()
    userInput.topic = input("Select Topic: \n")
    userInput.note = input("select note title: \n")
    userInput.text = input("Insert Text: \n")

    return userInput

def user_input_read_topic() -> userInputObject:
    userInput = userInputObject()
    userInput.topic = input("Select Topic: \n")
    return userInput

def user_input_add_wiki_article() -> int:
    try:
        return int(input("Would you like to add any of these articles to the topic? (1-9 = yes) (0 = No): \n"))
    except:
        print("please select a number")
        return user_input_add_wiki_article()

# client stuff

# main loop

def main():
    proxy = open_connection()
    
    while True:
        userChoice = input("\nSend message (1), read topic (2), search wikipedia(3), exit (e):\n")
        if(len(userChoice) == 0):
            print("plz make a input")
            continue
        if(userChoice[0] == "1"):
            userInputSend = user_input_send()
            send_message(proxy, userInputSend)
        elif(userChoice[0] == "2"):
            userInputRead = user_input_read_topic()
            read_topic(proxy, userInputRead)
        elif(userChoice[0] == "3"):
            userInputRead = user_input_read_topic()
            data = search_wikipedia(proxy, userInputRead)
            if(data == None):
                print("data doesn't exist")
                continue
            userInputNumber = user_input_add_wiki_article()
            if(userInputNumber == 0):
                continue
            userInputRead = user_input_read_topic()
            add_wikipedia_article(proxy, userInputNumber, data, userInputRead)
        elif(userChoice[0] == "e"):
            break

    return 0
if __name__ == "__main__":
   main()
# main loop
