#Python TeamSpeak interface
Making the querying of TeamSpeak servers 100 times easier.

Please note that this is a heavy WIP and a lot is going to change in the next update!


##Why
The TeamSpeak query interface is an awesome tool for developers. It features pretty much everything besides voice chat. The only problem is that it's hard to work with if you don't have the proper tools for the job. This tiny library features pretty much everything that you'll need to start developing using the query interface. It contains tools for pretty much everything while maintaining the direct feel that developers like. 

##How
You can create a connection by creating a instance and then calling connect(). The reason why it doesn't connect directly is because it allows you to reconnect more easily when the server disconnects you.

    import Teamspeak

    con = Teamspeak.TeamSpeak() # Create an instance
    con.connect() # Connect to the server
    print 'Yay connected!' if con.connected() else 'Noes!'
I included an example of a basic use ( Example.py ). I've also included an example of a Teamspeak cleverbot that uses [the cleverbot library][1].


  [1]: http://code.google.com/p/pycleverbot/
