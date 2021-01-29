#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(2048).strip()
        # Remove following comment marker to print incoming requests
        #print ("Got a request of: %s\n" % self.data)

        # Split data to retrieve request method and request path
        self.request_method = b''
        self.request_path = b'..'

        # Check if we are receiving an HTTP request and then split by newline and then by spaces to isolate the path and method
        if b'HTTP' in self.data:
            self.splitdata = self.data.splitlines()
            self.request_method = self.splitdata[0].split()[0]
            self.request_path = self.splitdata[0].split()[1]

        # If request is empty or contains a '..', automatically send a 404 response
        if not b'..' in self.request_path:
            # Check to make sure that request is GET method, otherwise return 405 response
            if self.check_request_method():
                # Attempt to retrieve the document located at the path
                page = self.retrieve_page()

                # Send response generated from trying to retrieve the document located at the path
                self.request.sendall(page)
            else:
                content = '405 Method Not Allowed'
                content_length = len(content)
                self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\nContent-Length: " + str(content_length) + "\r\nConnection: close\r\n\r\n" + content, 'utf-8'))
        else:
            content = '404 Not Found'
            content_length = len(content)
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(content_length) + '\r\nConnection: close\r\n\r\n' + content, 'utf-8'))

    def retrieve_page(self):
        result = b''

        # If request path contains a '.', then we know they are trying to access a specific file
        if b'.' in self.request_path:
            try:
                # Attempt to open document at the requested path
                page = open(b'./www' + self.request_path)
                content = page.read()
                content_length = len(content)
                # Differentiate whether a css or html file is being requested and format response correctly
                if b'css' in self.request_path:
                    result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: " + str(content_length) + "\r\nConnection: close\r\n\r\n" + content, 'utf-8')
                else:
                    result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(content_length) + "\r\nConnection: close\r\n\r\n" + content, 'utf-8')
                page.close()
            except OSError as e:
                # If we are unable to retrieve a file, then we assume they requested a file that is not located on the webserver and return 404
                content = '404 Not Found'
                content_length = len(content)
                result = bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(content_length) + '\r\nConnection: close\r\n\r\n' + content, 'utf-8')
        # If request path ends in '/', retrieve the html file located in the specified directory
        elif self.request_path.endswith(b'/'):
            try:
                self.request_path += b'index.html' # If no file is specified, add index.html and try to retrieve the file
                page = open(b'./www' + self.request_path)
                content = page.read()
                content_length = len(content)
                result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(content_length) + "\r\nConnection: close\r\n\r\n" + content, 'utf-8')
                page.close()
            except OSError as e:
                content = '404 Not Found'
                content_length = len(content)
                result = bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(content_length) + '\r\nConnection: close\r\n\r\n' + content, 'utf-8')
        # If request path does not contain a '.' and does not end in a '/' then the path is not ended correctly, send a 301 to correct path to end in a '/'
        else:
            content = '301 Moved Permanently, Location: http://127.0.0.1:8080' + self.request_path.decode() + '/'
            content_length = len(content)
            result = bytearray('HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080' + self.request_path.decode() + '/\r\nContent-Type: text/plain\r\nContent-Length: ' + str(content_length) + '\r\n\r\n' + content + '\r\n', 'utf-8')
                
        return result
    
    def check_request_method(self):
        # Return True if HTTP method is GET
        if b'GET' in self.request_method:
            return True
        else:
            return False

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
