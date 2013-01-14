import Teamspeak
import sys

# Create a new instance that will connect to localhost
print 'Connecting...'
ts3 = Teamspeak.TeamSpeak()

# Connect to the server
try:
    ts3.connect()
except Exception, e: # An exception is thrown if something goes wrong
    print e

# Check if we're connected
if not ts3.connected:
    print "Oops something went wrong."
    sys.exit(1)

print 'Sending a message'
# Let's encode the arguments
args = ts3.encode({
                    'targetmode':2,
                    'target':1,
                    'msg': 'Hello world'
                })
# Now we're going to send a message and then print out
#   what the server returns
print ts3.decode(ts3.sendCommand('sendtextmessage '+args))

# That was fun now let's listen into a conversation

print 'Stalking'
# Define the callback
def eventcallback(ts3, raw):
    message = ts3.decode(raw)
    print message['invokername']+': '+message['msg']
    # If a client says 'go away' then we'l stop the listener
    if message['msg'] == 'go away bot':
        return False
# Register the listener
ts3.registerEvent(eventcallback, event='textchannel', cid=1)

# Exit the program
print 'I\'m all done now'


