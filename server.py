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
        print ("Got a request of: %s\n" % self.data)

        # Split data to retrieve request method and request path
        self.request_method = b''
        self.request_path = b'..'
        if b'HTTP' in self.data:
            self.splitdata = self.data.splitlines()
            self.request_method = self.splitdata[0].split()[0]
            self.request_path = self.splitdata[0].split()[1]
        print(self.request_path)
        if not b'..' in self.request_path:
            if self.check_request_method():
                page = self.retrieve_page()
                #print("%s\n%s\n%s" % (self.splitdata, self.request_method, self.request_path))
                print("RESPONSE: \n", page)
                self.request.sendall(page)
            else:
                self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", 'utf-8'))
        else:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))

    def retrieve_page(self):
        result = b''
        if b'.' in self.request_path:
            try:
                print("Filename in path")
                page = open(b'./www' + self.request_path)
                if b'css' in self.request_path:
                    result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n" + page.read(), 'utf-8')
                else:
                    result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + page.read(), 'utf-8')
                page.close()
            except OSError as e:
                print("File Does not Exist")
                result = b'HTTP/1.1 404 Not Found\r\n\r\n'
        elif self.request_path.endswith(b'/'):
            try:
                self.request_path += b'index.html'
                page = open(b'./www' + self.request_path)
                result = bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + page.read(), 'utf-8')
                page.close()
            except OSError as e:
                result = b'HTTP/1.1 404 Not Found\r\n\r\n'
        else:
            result = b'HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080' + self.request_path + b'/\r\n\r\n'
                
        return result
    
    def check_request_method(self):
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
