import socket
import sys
import select

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port wherever the server is listening
server_address = ('10.0.0.4', 10000)
print >> sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
sys.stdout.flush()

try:
    while True:
        socket_list = [sys.stdin, sock]

        # Get the list sockets which are readable
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
        
        for s in ready_to_read:
                if s==sock:
                        # incoming message from remote server, sock
                        data = sock.recv(4096)
                        if not data:
                                print '\nDisconnected from chat server'
                                sys.exit()
                        else:
                                #print data
                                sys.stdout.write(data)
                                sys.stdout.flush()
                                if data.strip("\r\n")=="LOGOUT":
                                    sys.stdout.write("\n")
                                    sys.exit()
                else: 
                        # user entered a message
                        msg = sys.stdin.readline()
                        sock.sendto(msg, server_address)
        
finally:
    #print >> sys.stderr, 'closing socket'
    sock.close()
