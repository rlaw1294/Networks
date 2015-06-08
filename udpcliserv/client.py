'''
udp socket client
'''

import socket #for sockets
import sys #for exit
import select

'''
select.select(rlist, wlist, xlist[, timeout])
rlist: wait until ready for reading
wlist: wait until ready for writing
xlist: wait for an "exceptional condition" (see the manual page for what your system considers such a condition)

inputs = [mySocket]
outputs = []
timeout = 10
readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
for tempSocket in readable:
   tempSocket.recvFrom(1024)
'''

#create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

host = 'localhost'
port = 8888

msg1 = "message1"
msg2 = "message2"
msg3 = "message3"

ACK = "ACK"
NACK = "NACK"


while 1:
#    msg = raw_input('Enter message to send: ')

    try:
        #Set the whole string
#        s.sendto(msg, (host, port))
        s.sendto(msg1, (host, port))
        s.sendto(msg2, (host, port))
        s.sendto(msg3, (host, port))

        #receive data from client (data, addr)
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        print 'Server reply: ' + reply

        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        print 'Server reply2: ' + reply

        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]
        
        print 'Server reply3: ' + reply
    except socket.error, msg:
        print 'Error Code: ' + str(msg[0] + 'Message ' + msg[1])
        sys.exit()
