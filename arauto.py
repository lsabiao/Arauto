import socket
import datetime
import mimetypes
import os

#TODO migrar para o python3

version = "1.10"

mimetypes.init()

#mimetypes not supported in default python
mimetypes.add_type("application/font-woff2",".woff2")

class Arauto():
    
    def __init__(self,port=8088):
        self.host = ""
        self.port = port 

    def run(self):
        #python's socket magic
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host,self.port))
        self.s.listen(10)

        self.ip = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))
        self.ip = self.ip[2][0]


        #TODO modo silencioso
        print "*Hello, Master*"
        print "Serving at: {ip}:{port}".format(ip = self.ip, port = self.port)
        print

        while True:
            #TODO multi-threaded server?
            self.conn, self.addr = self.s.accept()
            self.data = self.conn.recv(1024)

            try:
                #get the file name from the URL
                self.fileRequested = self.getUrl(self.data)
                
                #create a response object
                self.c = Response(self.addr)
                
                #add a file to the response
                self.c.addFile(self.fileRequested)

                #send the file as a string
                self.conn.sendall(str(self.c))
                self.conn.close()
            except:
                self.conn.close()
        

    def getUrl(self,url):
        #get the file name and path from the get URL
        url = url.split("\r\n")[0]
        arg = url.split(" ")[1]
        arg = arg.lstrip("/")
        if(arg == ""):
            arg = "index.html"
            return arg
        if("." not in arg):
            arg= arg.rstrip("/")
            arg+="/index.html"
            return arg
        return arg


class Response():
    '''
        the response class
        for every request, we need a response
        just instantiate a response and add a file with (addFile())
        and return the object to the browser

    '''
    
    #default http header
    template = ("{protocol} {status} {nl}"
                "Location: {location}{nl}"
                "Date:{date}{nl}"
                "Server: {servername}{nl}"
                "Content-Type: {contentType}{nl}"
                "Content-Length: {contlen}{nl}"
                "Connection: {con}{nl}{nl}"
                "{payload}")

    
    def __init__(self,addr):
        self.protocol    = "HTTP/1.1"
        self.status      = 200
        self.location    = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        self.date        = datetime.datetime.now()
        self.serverName  = "Arauto-"+version
        self.contentType = ""
        self.contentLen  = ""
        self.connection  = "close"
        self.payload     = ""
        self.addr        = addr

    def __str__(self):
        return self.template.format(protocol = self.protocol,
                                    status = self.status,
                                    location = self.location,
                                    date = self.date,
                                    servername = self.serverName,
                                    contentType = self.contentType,
                                    contlen = self.contentLen,
                                    con = self.connection,
                                    payload = self.payload,
                                    nl = "\r\n")

    def addFile(self,file):
        ''' add a file to the response object '''
        
        try:
            if(file == os.path.basename(__file__)):
                raise
            temp = open(file,"rb").read()
            filename, file_extension = os.path.splitext(file)
	    try:
                self.contentType = mimetypes.types_map[file_extension]
	    except:
	        print "Files '{0}' not supported yet".format(file_extension)
            self.contentLen  = len(temp)
            self.payload = temp
            stat = "served (200)"
        except:
            self.status = 404
            self.contentType = ""
            self.contentLen  = ""
            self.payload     = "<h1>File {} not found</h1>".format(file)
            stat = "not found (404)"
        finally:
            print "{time} - File: '{file}' requested by: {addr} {status}".format(time = datetime.datetime.now(),file=file,status=stat,addr=self.addr[0])
            
if __name__ == "__main__":
    import sys
    try:
        newPort = int(sys.argv[1])
        s = Arauto(port = newPort)
    except:
        print "[You need admin permissions to run this port, using 8088]"
    s = Arauto()
    s.run()
