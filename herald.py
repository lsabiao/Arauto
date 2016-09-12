import socket
import datetime
import mimetypes
import os

version = "1.0"

mimetypes.init()


class response():
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
        self.serverName  = "herald-"+version
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
            self.contentType = mimetypes.types_map[file_extension]
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
            
def getURL(url):
    #get the file name and path from the get URL
    url = url.split("\r\n")[0]
    arg = url[5:url.rfind(" ")]
    return arg
    
def main(host="",port=8081):
    #python's socket magic
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(10)

    ip = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))
    ip = ip[2][0]
    
    print "Hello, Master"
    print "Serving at: {ip}:{port}".format(ip= ip , port=port)
    print 

    #application main loop
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)

        #get the file name from the URL
        fileRequested = getURL(data)

        #create a response object
        c = response(addr)
        #add a file to the response
        c.addFile(fileRequested)

        #send the file as a string.
        conn.sendall(str(c))
        conn.close()

if __name__ == "__main__":
    main()



