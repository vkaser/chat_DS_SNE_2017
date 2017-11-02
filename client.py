#TCP Chat Client
import socket
import select
import sys
import string
import unicodedata

def prompt():
    sys.stdout.write('> ')
    sys.stdout.flush()

#main function
if __name__ == '__main__':
    if(len(sys.argv) < 3):
        print 'Usage : python client.py hostname port'
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    #Stickers
    sticker = { '@smile':'\U0001F642', '@frown':'\U00002639', \
                '@sweat':'\U0001F605', '@wink':'\U0001F609', \
                '@kiss':'\U0001F619', '@hug':'\U0001F917', \
                '@neutral':'\U0001F610', '@monkey':'\U0001F649',}

    #Create an AF_INET, STREAM socket (TCP)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2) #2 seconds to get answer from remote server
    except socket.error, msg:
        print 'Failed to create socket. Error code: {}, Mmessage: {}.'.format(str(msg[0]),msg[1])
        sys.exit()

    #Connect ot remote host
    try:
        s.connect((HOST, PORT))
    except socket.error, msg:
        print 'Unable to connect to the server {} through {} port. Error: {}'.format(host, port, msg)
        s.close()
        sys.exit()

    print '---------- InnoChat ----------'
    prompt()

    while True:
        socket_list = [sys.stdin, s]

        #Get the list sockets which are readable
        try:
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        except KeyboardInterrupt:
            s.send('quit()\n')
            sys.exit()
        for sock in read_sockets:
            #Incoming message from server
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from the server'
                    sys.exit()
                else:
                    #Print data
                    msg = data.split()
                    n = 0
                    for word in msg:
                        if word in sticker.keys():
                            msg[n] = unicode(sticker[word], 'unicode-escape')
                        n += 1
                    data = ''
                    for word in msg:
                        data += word + ' '
                    data += '\n'
                    sys.stdout.write(data)
                    prompt()
            else:
                msg = sys.stdin.readline()
                try:
                    #Set the whole string
                    s.send(msg)
                    prompt()
                except socket.error, msg:
                    print 'Send failed. Error: {}'.format(msg)
                    sys.exit()