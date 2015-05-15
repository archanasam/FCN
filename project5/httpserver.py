#! /usr/bin/python

import socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib2
from SocketServer import ThreadingMixIn
import sys
import math


# Server IP 
HTTP_SERVER_IP = 0

# Server Port
HTTP_SERVER_PORT = 0

# Origin for the server
ORIGIN = ''

# Dictionary to hold the contents of the cache
server_cache = {}

# Dictionary to hold the readcount of each URL
content_readcount = {}

# Current cache size
CACHE_SIZE = 0

# 10MB limit for the cache
CACHE_LIMIT = int(10 * math.pow(10, 6))


# This is the handler for HTTP requests coming from the client
class RequestHandler(BaseHTTPRequestHandler):

    # Handler for GET requests
    def do_GET(self):
        
        # Path of the requested content
        URLpath = self.path

	# If the path has been visited previously, return the contents from the cache
        if (str(URLpath) in server_cache.keys()):
	    # Increase the read count 
            content_readcount[str(URLpath)] = content_readcount[str(URLpath)] + 1
            
	    # Create the response
	    self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Write the contents to the response
            self.wfile.write(server_cache.get(str(URLpath)))
        else:
	    # Content not in the cache. Get if from the origin
            global ORIGIN
            request_url = "http://" + ORIGIN + str(URLpath)

            reply = None
            try:
                reply = urllib2.urlopen(request_url)
            except urllib2.HTTPError, error:
                self.send_response(error.code)
                return

            global CACHE_SIZE
            global CACHE_LIMIT

            contents = reply.read()

	    # If the cache cannot hold the contents, then remove the contents with the
            # the least read count to make room for the current read contents
            while ((len(contents) + CACHE_SIZE) > CACHE_LIMIT):
                to_be_removed = min(content_readcount, key=content_readcount.get)

                content_size = len(server_cache.get(to_be_removed))
                CACHE_SIZE = CACHE_SIZE - content_size

                del content_readcount[to_be_removed]
                del server_cache[to_be_removed]

            
            server_cache[str(URLpath)] = contents
            content_readcount[str(URLpath)] = 1
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(contents)
    
    # Override default logging method
    def log_message(self, formatmat, *args):
	    # Supress the logging by doing nothing
	    return	


# HttpServer
class MyHttpServer(ThreadingMixIn, HTTPServer):
    '''
    Do nothing
    '''


# Beginning of the program

if (len(sys.argv) < 5):
    print "Error. Too few arguments."
    print "Usage ./httpserver -p <port> -o <origin>"
    sys.exit(1)

if (len(sys.argv) == 5):
    if (sys.argv[1] != '-p' or sys.argv[3] != '-o'):
        print "Error in arguments.\n"
        print "Usage ./httpserver -p <port> -o <origin>"
        sys.exit(1)


    if ( 40000 <= int(sys.argv[2]) <= 65535 ):
        HTTP_SERVER_PORT = int(sys.argv[2])
    else:
        print "Wrong port number.\nPort number should be in the range (40000 - 65535)"
        sys.exit(1)

    ORIGIN = sys.argv[4]

    # Origin runs http server on 8080    
    if (ORIGIN == 'ec2-52-4-98-110.compute-1.amazonaws.com'):
	ORIGIN = ORIGIN + ":8080"

try:
    httpserver = MyHttpServer(('', HTTP_SERVER_PORT), RequestHandler)
    httpserver.serve_forever()
except KeyboardInterrupt:
    httpserver.socket.close()
