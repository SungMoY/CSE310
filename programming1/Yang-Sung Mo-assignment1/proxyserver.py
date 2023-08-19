#accept HTTP requests
#forward HTTP requests to web server
#be able to handle objects (images, HTMl pages, etc)

from functools import cache
from socket import *
from signal import *
from numpy import save
import requests
from PIL import Image
cacheDict = {}

# sets up ctrl-c to exit via SIGINT
signal(SIGINT, SIG_DFL)

# sets up the server socket
proxyServerSocket = socket(AF_INET, SOCK_STREAM)
# binds socket to port 8888
proxyServerSocket.bind(('', 8888))
# listens for connections
proxyServerSocket.listen()

while True:
    try:
        # serverSocket accepts clientSocket
        print('"Listening for connections...\n')
        clientSocket, addr = proxyServerSocket.accept()
        
        # receive request from client and parse it
        clientRequest = clientSocket.recv(1024)
        requestTypeHTTP = clientRequest.split()[0].decode("utf-8") 
        requestURL = clientRequest.split()[1][1:].decode("utf-8")
        requestVersionHTTP = clientRequest.split()[2].decode("utf-8")

        requestURLCopy = requestURL

        print(requestURL)
    
        # remove the http:// from the URL and https://
        if requestURL.startswith("http://"):
            requestURL = requestURL[7:]
        
               # if the url starts with www., remove it
        if requestURL.startswith("www."):
            requestURL = requestURL[4:]

        requestURLCacheDictCopy = requestURL

        print("requestURLCacheDictCopy: ", requestURLCacheDictCopy)
        print("keys: ", cacheDict.keys())

        if requestURLCacheDictCopy in cacheDict:
            #print each key and value in the cache dictionary separated by a line
            # in the cache is an html file. send it to the client socket as an http response
            clientSocket.send('HTTP/1.1 200 OK\r\n\r\n'.encode())
            # if type of cacheDict[requestURLCacheDictCopy] is byte, then dont encode it. else, encode it
            if type(cacheDict[requestURLCacheDictCopy]) is bytes:
                print(cacheDict[requestURLCacheDictCopy])
                clientSocket.send(cacheDict[requestURLCacheDictCopy])
            else:
                print(cacheDict[requestURLCacheDictCopy])
                clientSocket.send(cacheDict[requestURLCacheDictCopy].encode())
            clientSocket.send("\r\n".encode())
            clientSocket.close()
            continue
        
        print("Sending From Web Server")
        # given a request URL, get the url up to the .com or .edu or .org or .gov
        if (requestURL.find(".com") != -1):
            requestURL = requestURL[:requestURL.find(".com")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".com")+4:]
            print("is a .com")
            #print(requestURLCopy)
        elif (requestURL.find(".edu") != -1):
            requestURL = requestURL[:requestURL.find(".edu")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".edu")+4:]
            print("is a .edu")
            #print(requestURLCopy)
        elif (requestURL.find(".org") != -1):
            requestURL = requestURL[:requestURL.find(".org")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".org")+4:]
            print("is a .org")
            #print(requestURLCopy)
        elif (requestURL.find(".gov") != -1):
            requestURL = requestURL[:requestURL.find(".gov")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".gov")+4:]
            print("is a .gov")
            #print(requestURLCopy)
        elif (requestURL.find(".net") != -1):
            requestURL = requestURL[:requestURL.find(".net")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".net")+4:]
            print("is a .net")
            #print(requestURLCopy)
        elif (requestURL.find(".mil") != -1):
            requestURL = requestURL[:requestURL.find(".mil")+4]
            requestURLCopy = requestURLCopy[requestURLCopy.find(".mil")+4:]
            print("is a .mil")
            #print(requestURLCopy)
        
        #get ip address and connect to its socket
        webServerEyePee = gethostbyname(requestURL)
        webServerSocket = socket(AF_INET, SOCK_STREAM)
        webServerSocket.connect((webServerEyePee, 80))

        proxyRequest = "GET /"+requestURLCopy+" HTTP/1.1\r\nHost:%s\r\n\r\n" % requestURL
        if requestURL == requestURLCopy:
            proxyRequest = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % requestURL
        # print("proxyRequest: ", proxyRequest.encode())
        webServerSocket.send(proxyRequest.encode())
        webServerResponse = webServerSocket.recv(4096)
        # print("Web server response: ", webServerResponse)
        webServerSocket.close()

        #send client the response from the web server and close connection
        print("THE PROXY GOT THE IMAGE AND SENT IT TO THE CLIENT")
        clientSocket.send(webServerResponse)
        clientSocket.close()

        #check if webServerResponse was not 200. if it was not, then continue to next while loop iteration
        if webServerResponse.split()[1].decode("utf-8") != "200":
            continue
        #instead of the saving the webServerResponse, download the files from that webServerResponse and store them in the cacheDict
        saveContent = []

        #print(webServerResponse.split())
        #find the content-type of the webServerResponse
        
        for x in range(len(webServerResponse.split())):
            if webServerResponse.split()[x].decode("utf-8") == "Content-Type:":
                contentType = webServerResponse.split()[x+1].decode("utf-8")
                print(contentType)
                break

        if contentType == "text/html;":
            # print("text/html")
            htmlDoc = webServerResponse.decode("utf-8")
            htmlDoc = htmlDoc[htmlDoc.find("\r\n\r\n")+4:]
            print("saved to cacheDict")

            #in the contentFile, replace the word France with England: this is a test to see if caching servers up the saved HTML file
            #contentFile = contentFile.replace("France", "England")
            cacheDict[requestURLCacheDictCopy] = htmlDoc

        # iterate through the htmlDoc and find all occurences of "src="
        # when found an "src=", append the link that follows it to the saveContent list
        for x in range(len(htmlDoc)):
            if htmlDoc[x:x+5] == "src=\"":
                saveContent.append(htmlDoc[x+5:htmlDoc.find("\"", x+5)])
        
        print('Initial srcs to examine: ', saveContent)

        cacheDict[requestURLCacheDictCopy] = htmlDoc
        #print("HTMLDOC: ", htmlDoc)
        #print(saveContent)

        saveContentCopy = saveContent.copy()

        for object in saveContentCopy:
            objectCopy = object
            print("iterating on object: ", object)
            if object.startswith("http://"):
                object = object[7:]
            if object.startswith("www."):
                object = object[4:]

            objectURL = object
            objectHost = object
            
            if (object.find(".com") != -1):
                objectHost = object[:object.find(".com")+4]
                objectURL = object[object.find(".com")+4:]
            elif (object.find(".edu") != -1):
                objectHost = object[:object.find(".edu")+4]
                objectURL = object[object.find(".edu")+4:]
            elif (object.find(".org") != -1):
                objectHost = object[:object.find(".org")+4]
                objectURL = object[object.find(".org")+4:]
            elif (object.find(".gov") != -1):
                objectHost = object[:object.find(".gov")+4]
                objectURL = object[object.find(".gov")+4:]
            elif (object.find(".net") != -1):
                objectHost = object[:object.find(".net")+4]
                objectURL = object[object.find(".net")+4:]
            elif (object.find(".mil") != -1):
                objectHost = object[:object.find(".mil")+4]
                objectURL = object[object.find(".mil")+4:]
            

            print(objectURL, objectHost)
            try: 
                getObjectEyePee = gethostbyname(objectHost)
                getObjectSocket = socket(AF_INET, SOCK_STREAM)
                getObjectSocket.connect((getObjectEyePee, 80))

                getObjectRequest = "GET /"+objectURL+" HTTP/1.1\r\nHost:%s\r\n\r\n" % objectHost
                getObjectSocket.send(getObjectRequest.encode())
                getObjectResponse = getObjectSocket.recv(4096)
                getObjectSocket.close()
                #convert getOBjectResponse to a bytearray split by \r\n this isolates just the bodycontent of the http response
                getObjectResponseContent = getObjectResponse.split(b'\r\n\r\n')[1]
                # this tests if the image was properly saved
                #import io
                #img = Image.frombytes("L", (253, 199), getObjectResponseContent)
                #im = Image.open(io.BytesIO(getObjectResponseContent))
                #im.show()

                # save the bytes of the image to the cacheDict with the key as the url of the image
                saveContentCopyDict = objectHost+objectURL
                cacheDict[saveContentCopyDict] = getObjectResponseContent

                #after the image is saved, replace the url of the image in the html file with the url of the image in the cacheDict

                if objectCopy in saveContent:
                    print("Object: ", object, " is in saveContent")
                    print("Replacing this object's URL in the HTML DOM with: ", saveContentCopyDict)
                    htmlDoc = htmlDoc.replace(object, "localhost:8888/"+saveContentCopyDict)
                    cacheDict[requestURLCacheDictCopy] = htmlDoc
                else:
                    print("NOT IN SAVECONTENT")
            except Exception as e:
                print(e)
                #remove this object from the saveContent list
                print('Removing current object bc getaddrinfo failed - these are in now: ', saveContent)
                saveContent.remove(object)
                print('Removing current object bc getaddrinfo failed - these are left: ', saveContent)
                continue

        

            
        # # print each key value pair with three lines in between
        # for key, value in cacheDict.items():
        #     print(key)
        #     print(value)
        #     print("")
        #     print("")
        #     print("")
        

    except Exception as e:
        print(e)
        clientSocket.close()