import Teamspeak
import sys

# Create a new instance that will connect to localhost
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

# Define the callback
def callback(message, ts3):
    print message['invokername']+': '+message['msg']
    # If a client says 'go away' then we'l stop the listener

# Register the listener
ts3.registerEvent(callableack, event='textchannel', cid=1)

# Exit the program
print 'I\'m all done now'


