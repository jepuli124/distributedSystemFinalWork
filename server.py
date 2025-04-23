
from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import threading
import requests

threadlock = threading.Lock()

# registable functions

def is_even(n):
    return n % 2 == 0

def receive_message(topic, note, text, datetime):
    thread = threading.Thread(target=write_xml, args=[topic, note, text, datetime])
    thread.start()

def send_topic(topic):
    global threadlock
    threadlock.acquire()
    tree = ET.parse('./xmlData.xml')
    root = tree.getroot()
    for child in root.iter("topic"):
        if(child.attrib["name"] == topic):
            threadlock.release()
            return ET.tostring(child)
    threadlock.release()
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
    thread = threading.Thread(target=write_xml, args=[topic, "article", article, datetime])
    thread.start()

# registable functions

# server functions

def open_connection():
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Listening on port 8000...")
    return server


def register_functions(server):
    server.register_function(is_even, "is_even")
    server.register_function(receive_message, "send_message")
    server.register_function(send_topic, "read_topic")
    server.register_function(query_wikipedia, "query_wikipedia")
    server.register_function(add_article_to_topic, "add_article_to_topic")

def create_xml_file():
    try:
        baseText = ET.Element("data")
        baseTree = ET.ElementTree(element=baseText)
        baseTree.write("xmlData.xml")
        return ET.parse('./xmlData.xml')
    except FileExistsError:
        print("XML file already exists")
        return None

def write_xml(topic, note, text, datetime):
    global threadlock

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


    threadlock.acquire()
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
    threadlock.release()


# server functions


# main loop

def main():
    

    server = open_connection()
    register_functions(server)

    server.serve_forever()

# main loop


if __name__ == "__main__":
   main()
    