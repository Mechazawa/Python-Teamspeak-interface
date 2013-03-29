#!/usr/bin/python

import telnetlib, thread
from threading import Lock

class TeamSpeak:
    def __init__(self, host='localhost', port=10011):
        self.host   = host
        self.port   = port
        self.__ioLock = Lock()
        self.listenThread = None
        self.encoding = {
            "\\":"\\\\", "/":"\\/",
            " ":"\\s", "|":"\\p",
            "\a":"\\a", "\b":"\\b",
            "\f":"\\f", "\n":"\\n",
            "\r":"\\r", "\t":"\\t",
            "\v":"\\v"
         }
    def connected(self):
        try:
            self.connection.write('\n\r')
            return True
        except:
            return False

    def decode(self, result):
        """
        Decodes the result
        """
        if '|' in result:
            decodable = result.split('|')
            decoded = []
            for d in decodable:
                decoded.append(self.__decodeSingle(d))
            return decoded
        return self.__decodeSingle(result)

    def __decodeSingle(self, result):
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

    def sendCommand(self, command, preRead=0, postRead=0):
        """
        Send a command to the server and receive the output
        """
        if not self.connected():
            raise Exception('Not connected to a TeamSpeak server')
        self.__ioLock.acquire()
        self.connection.write(command+'\n\r')
        for i in range(preRead): self.connection.read_until("\n\r", 5)
        data = self.connection.read_until('\n\r',5)
        for i in range(postRead): self.connection.read_until("\n\r", 5)
        self.__ioLock.release()
        return data

    def registerEvent(self, **args):
        """
        Creates a listener that will be destroyed once the callback returns false
        Make sure that the permissions are set properly

        The username and password must be set if used becuase the listener session has to log in again if the server disconnects the client
        """
        # Parse ALL the arguments!
        # Todo: clean this shit up
        callback = None
        event='textchannel'
        threaded=False
        cid=None
        username=None
        password=None

        if args.has_key("event") and isinstance(args['event'],str): event = args['event']
        elif args.has_key("event") and not isinstance(args['event'],str): raise Exception('Event is not a string')

        if args.has_key("callback") and hasattr(args['callback'], '__call__'): callback = args['callback']
        elif args.has_key("callback") and not hasattr(args['callback'], '__call__'): raise Exception('callback is not a function')

        # if args.has_key("threaded") and isinstance(args['threaded'],bool): threaded = args['threaded']
        # elif args.has_key("threaded") and not isinstance(args['threaded'],bool): raise Exception('threaded is not a boolean')

        if args.has_key("channel") and isinstance(args['channel'],int): cid = args['channel']
        elif args.has_key("channel") and not isinstance(args['channel'],int): raise Exception('channel is not a integer')

        if args.has_key("username") and isinstance(args['username'],str): username = args['username']
        elif args.has_key("username") and not isinstance(args['username'],str): raise Exception('username is not a string')

        if args.has_key("password") and isinstance(args['password'],str): username = args['password']
        elif args.has_key("password") and not isinstance(args['password'],str): raise Exception('password is not a string')

        if not self.connected(): raise Exception('Not connected to a TeamSpeak server')
        self.callback = callback
        if username != None and password != None:
            data = self.decode(self.sendCommand('login '+encode(username)+' '+encode(password)))
            if data['id'] != '0':
                raise Exception('Login refused')
        if not cid==None:
            whoami = self.decode(self.sendCommand('whoami',1,1))
            data = self.decode(self.sendCommand('clientmove '+self.encode({'clid':whoami['client_id'],'cid': cid})))
            if data['id'] != '0' and data['id'] != '770':
                raise Exception('Could not move client: '+data['msg'])
        command = 'servernotifyregister '+self.encode({'event':event})
        if not cid==None: command = 'servernotifyregister '+self.encode({'event':event,'id': cid})
        data = self.decode(self.sendCommand(command))
        if data['id'] != '0':
            raise Exception('listener registration refused: '+data['msg'])
        while True:
            try:
                message = self.connection.read_until('\n\r',7200)
                try: self.decode(message)['invokername']
                except: continue
                if threaded and callback != None: # Are we doing thread magic?
                    raise NotImplementedError('Can\'t thread')
                elif callback != None:
                    if callback(self, message) == False: return
                else: # Default callback
                    print self.decode(message)['invokername']+': '+self.decode(message)['msg']
            except NotImplementedError, e: raise NotImplementedError('Can\'t thread') #DDDDDDDouble exception!
            except:
                self.connect()
                if username != None:
                    data = self.decode(self.sendCommand('login '+encode(username)+' '+encode(password)))
                    if data['id'] != '0':
                        raise Exception('Login refused: '+data['msg'])
                if not cid==None:
                    whoami = self.decode(self.sendCommand('whoami'))
                    data = self.decode(self.sendCommand('clientmove '+self.encode({'clid':whoami['client_id'],'cid': cid})))
                    if data['id'] != '0' and data['id'] != '770':
                        raise Exception('Could not move client: '+data['msg'])
                command = 'servernotifyregister '+self.encode({'event':event})
                if not cid==None: command = 'servernotifyregister '+self.encode({'event':event,'id': cid})
                data = self.decode(self.sendCommand(command))
                if data['id'] != '0':
                    raise Exception('listener registration refused')

    def connect(self, server=1):
        """
        Create a new connection
        """
        self.virtualserver = server
        #Create new connection
        self.__ioLock.acquire()
        self.connection = telnetlib.Telnet(self.host,self.port)
        data = self.connection.read_until('\n\r',5)
        self.connection.read_until("\n\r", 5)
        self.__ioLock.release()
        if not 'TS3' in data:
            raise Exception('Teamspeak connection refused')
        #connect to the Virtual Server
        self.__ioLock.acquire()
        self.connection.write('use '+str(self.virtualserver)+'\n\r')
        raw = self.connection.read_until('\n\r',5)
        data = self.decode(raw)
        self.__ioLock.release()
        if int(data['id']) != 0:
            raise Exception('Unable to select virtual server\n\r'+raw)
