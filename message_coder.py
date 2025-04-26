def encode(*data: str) -> str:
    encodedData = ""

    if(len(data) == 1 and type(data[0]) != type("") and data[0] != None): # in case incoming data is inside of a list
        data = data[0]

    for text in data: # goes through given list through and makes them a string seperating different messages with ;
        encodedData += str(text) + ";"

    return encodedData


def decode(data: str) -> list[str]:
    decodedData = []
    temp = ""

    for letter in data: # goes through given text through and makes them a list seperating messages from ;
        if letter == ';':
            decodedData.append(temp)
            temp = ""
            continue
        temp += letter

    return decodedData

if __name__ == "__main__": #some testing
    print(encode("hello world"))
    print(encode("hello", "world"))
    print(decode(encode("woah")))
    print(decode(encode(decode(encode("woah", "is", "this", "some", "wizard's", "doing")))))