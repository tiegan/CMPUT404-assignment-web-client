#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002,
#                https://github.com/treedust and Tiegan Bonowicz
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=500, body=""):
        self.code = code
        self.body = body

# Stuff starts being changed here.
class HTTPClient(object):

    # Lab 2 all over again. Use the port (or 80 if not given) to connect to
    # the given host.
    def connect(self, host, port):
        if port is None:
            port = 80
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    # Get the code by splitting the response and taking the first
    def get_code(self, data):
        try:
            code = int(data.split(" ")[1])
        except:
            code = 404
        return code

    # It's not used so it doesn't get changed.
    def get_headers(self,data):
        return None

    # Return the body by splitting the data by the two line breaks then taking
    # the second part of the split.
    def get_body(self, data):
        return data.split("\r\n\r\n", 1)[1]

    # This remains the same.
    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # Get websites.
    def GET(self, url, args=None):
        # Use urlparse to split the url up for convenience
        parseResult = urlparse.urlparse(url)
        host = parseResult.hostname # i.e. "www.google.ca"
        port = parseResult.port # i.e. "8080"
        path = parseResult.path # i.e. "/abc/def"

        # Get the client to connect using the host and port.
        clientSocket = self.connect(host, port)

        # GET header.
        request = "GET %s HTTP/1.1\r\n" %path
        request += "Host: %s\r\n" %host
        request += "Accept: */*\r\n\r\n"

        # Use the socket to send the request, get the response from recvall
        # then close the socket as it's done its job.
        clientSocket.sendall(request)
        response = self.recvall(clientSocket)
        clientSocket.close()

        # Print the response, get the code/body and return it.
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    # I think like 75% of this is repeated from the GET function. I really
    # should just make a function that can handle both to reduce redundancies
    # but eh, it's not required for this assignment.
    def POST(self, url, args=None):
        # Use urlparse to split the url up for convenience
        parseResult = urlparse.urlparse(url)
        host = parseResult.hostname
        port = parseResult.port
        path = parseResult.path
        input = ""
        contentLength = 0

        # If we have args to use in the POST then encode them into input and
        # get the length.
        if(args != None):
            input = urllib.urlencode(args)
            contentLength = len(input)

        # Get the client to connect using the host and port.
        clientSocket = self.connect(host, port)

        # POST header + input.
        request = "POST %s HTTP/1.1\r\n" %path
        request += "Host: %s\r\n" %host
        request += "Accept: */*\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: %d\r\n\r\n" %contentLength
        
        # Good idea to add the if just so we don't have yet another \r\n with
        # no input.
        if(input != ""):
            request += input + "\r\n"

        # Use the socket to send the request, get the response from recvall
        # then close the socket as it's done its job.
        clientSocket.sendall(request)
        response = self.recvall(clientSocket)
        clientSocket.close()

        # Print the response, get the code/body and return it.
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        # Need to add HTTP to the url if necessary, else it just goes "lol nope"
        if(url[0:5] != "http"):
            url = "http://" + url

        # Everything below is left the same.
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
