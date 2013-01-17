#!/usr/bin/python
import Teamspeak
import time
import urllib2
import hashlib
import re

class ServerFullError(Exception):
        pass

ReplyFlagsRE = re.compile('<INPUT NAME=(.+?) TYPE=(.+?) VALUE="(.*?)">', re.IGNORECASE | re.MULTILINE)

class Session(object):
        keylist=['stimulus','start','sessionid','vText8','vText7','vText6','vText5','vText4','vText3','vText2','icognoid','icognocheck','prevref','emotionaloutput','emotionalhistory','asbotname','ttsvoice','typing','lineref','fno','sub','islearning','cleanslate']
        headers={}
        headers['User-Agent']='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0'
        headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        headers['Accept-Language']='en-us;q=0.8,en;q=0.5'
        headers['X-Moz']='prefetch'
        headers['Accept-Charset']='ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        headers['Referer']='http://www.cleverbot.com'
        headers['Cache-Control']='no-cache, no-cache'
        headers['Pragma']='no-cache'

        def __init__(self):
                self.arglist=['','y','','','','','','','','','wsf','','','','','','','','','0','Say','1','false']
                self.MsgList=[]

        def Send(self):
                data=encode(self.keylist,self.arglist)
                digest_txt=data[9:29]
                hash=hashlib.md5(digest_txt).hexdigest()
                self.arglist[self.keylist.index('icognocheck')]=hash
                data=encode(self.keylist,self.arglist)
                req=urllib2.Request("http://www.cleverbot.com/webservicemin",data,self.headers)
                f=urllib2.urlopen(req)
                reply=f.read()
                return reply

        def Ask(self,q):
                self.arglist[self.keylist.index('stimulus')]=q
                if self.MsgList: self.arglist[self.keylist.index('lineref')]='!0'+str(len(self.MsgList)/2)
                asw=self.Send()
                self.MsgList.append(q)
                answer = parseAnswers(asw)
                for k,v in answer.iteritems():
                        try:
                                self.arglist[self.keylist.index(k)] = v
                        except ValueError:
                                pass
                self.arglist[self.keylist.index('emotionaloutput')]=''
                text = answer['ttsText']
                self.MsgList.append(text)
                return text

def parseAnswers(text):
        d = {}
        keys = ["text", "sessionid", "logurl", "vText8", "vText7", "vText6", "vText5", "vText4", "vText3",
                        "vText2", "prevref", "foo", "emotionalhistory", "ttsLocMP3", "ttsLocTXT",
                        "ttsLocTXT3", "ttsText", "lineRef", "lineURL", "linePOST", "lineChoices",
                        "lineChoicesAbbrev", "typingData", "divert"]
        values = text.split("\r")
        i = 0
        for key in keys:
                d[key] = values[i]
                i += 1
        return d

def encode(keylist,arglist):
        text=''
        for i in range(len(keylist)):
                k=keylist[i]; v=quote(arglist[i])
                text+='&'+k+'='+v
        text=text[1:]
        return text

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
def quote(s, safe = '/'):   #quote('abc def') -> 'abc%20def'
        safe += always_safe
        safe_map = {}
        for i in range(256):
                c = chr(i)
                safe_map[c] = (c in safe) and c or  ('%%%02X' % i)
        res = map(safe_map.__getitem__, s)
        return ''.join(res)


def main():
        import sys
        cb = Session()

        q = ''
        while q != 'bye':
                try:
                        q = raw_input("> ")
                except KeyboardInterrupt:
                        print
                        sys.exit()
                print cb.Ask(q)


def chatCallback(ts, raw):
    message = ts.decode(raw)
    print message['invokername']+': '+message['msg']
    if message['invokername'] == nick: return None
    if message['msg'] == 'go away bot':
        command = 'sendtextmessage '+ts.encode({
                    'targetmode':2,
                    'msg': 'Mkay '+message['invokername']+'. I\'ll be back in 5 minutes.'
                })
        ts.sendCommand(command)
        time.sleep(60*5)
        command = 'sendtextmessage '+ts.encode({
                    'targetmode':2,
                    'msg': 'I\'m back bitchez!'
                })
        ts.sendCommand(command)
        return None
    ts.sendCommand('clientupdate '+ts.encode({'client_nickname':nick}))
    dumb = cb.Ask(message['msg'])
    print nick+': '+dumb
    command = 'sendtextmessage '+ts.encode({
                    'targetmode':2,
                    'msg': dumb
                })
    ts.sendCommand(command)

if __name__ == "__main__":
    host = raw_input('host: ')
    port = raw_input('port: ')
    nick = raw_input('nickname: ')

    print 'connecting...'
    ts3 = Teamspeak.TeamSpeak(host,port)
    ts3.connect()
    print ts3.connected()
    #print ts3.sendCommand('login megabot ATQnuvxX')
    print 'getting channels'
    channels = ts3.decode(ts3.sendCommand('channellist'))
    for channel in channels:
        print '['+channel['cid']+']\t'+channel['channel_name']

    cid = raw_input('channel id: ')
    print 'starting session'
    cb = Session()
    ts3.registerEvent(callback=chatCallback, channel=int(cid))
	
