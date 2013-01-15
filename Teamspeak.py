#import TeamSpeak stuff
import telnetlib
from threading import Lock

class TeamSpeak:
    def __init__(self, host='localhost', port=10011):
        self.host   = host
        self.port   = port
        self.ioLock = Lock()
        self.connected = False
        self.listenThread = None
        self.encoding = {
            "\\":"\\\\", "/":"\\/",
            " ":"\\s", "|":"\\p",
            "\a":"\\a", "\b":"\\b",
            "\f":"\\f", "\n":"\\n",
            "\r":"\\r", "\t":"\\t",
            "\v":"\\v"
         }

    def decode(self, result):
        """
        Decodes the result
        """
        decodable = result.split()
        decoded = {}
        for decodeme in decodable:
            expl = decodeme.split('=',1)
            if len(expl) != 2:
                decoded[decodeme]=''
                continue
            for o,r in self.encoding.iteritems():
                expl[0] = expl[0].replace(r,o)
                expl[1] = expl[1].replace(r,o)
            decoded[expl[0]]=expl[1]
        return decoded

    def encode(self, args={}):
        """
        Encodes the arguments
        """
        if isinstance(args,int): args = str(args)
        if isinstance(args,str):
            for r,o in self.encoding.iteritems():
                args = args.replace(r,o)
            return args
        encoded = ''
        for k,v in args.iteritems():
            if not isinstance(v,int):
                for r,o in self.encoding.iteritems():
                    v = v.replace(r,o)
                encoded += ' '+k
                if v != '': encoded += '='+v
            else:
                encoded += ' '+k+'='+str(v)
        return encoded.strip()

    def sendCommand(self, command='', postRead=0):
        """
        Send a command to the server and receive the output
        """
        if not self.connected:
            raise Exception('Not connected to a TeamSpeak server')
        self.ioLock.acquire()
        if command != '':
            self.connection.write(command+'\n\r')
        data = self.connection.read_until('\n\r',5)
        for i in range(postRead): self.connection.read_until("\n\r", 5)
        self.ioLock.release()
        return data

    def registerEvent(self, callback, event='textchannel', cid=None, username=None, password=None):
        """
        Creates a listener that will be destroyed once the callback returns false
        Make sure that the permissions are set properly

        The username and password must be set if used becuase the listener session has to log in again if the server disconnects the client
        """
        if not self.connected: raise Exception('Not connected to a TeamSpeak server')
        self.callback = callback
        if username != None:
            data = self.decode(self.sendCommand('login '+encode(username)+' '+encode(password)))
            if data['id'] != '0':
                raise Exception('Login refused')
        command = 'servernotifyregister '+self.encode({'event':event})
        if not cid==None: command = 'servernotifyregister '+self.encode({'event':event,'id': cid})
        data = self.decode(self.sendCommand(command))
        if data['id'] != '0':
            raise Exception('listener registration refused')
        while True:
            try:
                message = self.connection.read_until('\n\r',7200)
                if callback(self, message) == False: return
            except:
                self.connect()
                if username != None:
                    data = self.decode(self.sendCommand('login '+encode(username)+' '+encode(password)))
                    if data['id'] != '0':
                        raise Exception('Login refused')
                command = 'servernotifyregister '+self.encode({'event':event})
                if not cid==None: command = 'servernotifyregister '+self.encode({'event':event,'id': cid})
                data = self.decode(self.sendCommand(command))
                if data['id'] != '0':
                    raise Exception('listener registration refused')

    def connect(self, server=1):
        """
        Create a new connection
        """
        self.connected = False
        self.virtualserver = server
        #Create new connction
        self.ioLock.acquire()
        self.connection = telnetlib.Telnet(self.host,self.port)
        data = self.connection.read_until('\n\r',5)
        self.connection.read_until("\n\r", 5)
        self.ioLock.release()
        if not 'TS3' in data:
            raise Exception('Teamspeak connection refused')
        #connect to the Virtual Server
        self.ioLock.acquire()
        self.connection.write(str(self.virtualserver)+'\n\r')
        self.decode(self.connection.read_until('\n\r',5))
        self.ioLock.release()
        if int(data['id']) != 0:
            raise Exception('Unable to select virtual server\n\r'+raw)
        self.connected= True
