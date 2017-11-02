#TCP Chat Server
import socket
import select
import sys

#Function to broadcast chat messages to all connected clients
def broadcast_data(sock, message):
	#Do not send the message to master socket and the client who has send message
	for socket in CONNECTION_LIST:
		if socket != server_socket and socket != sock and socket != input_server:
			try:
				socket.send(message)
			except:
				#Broken socket connection may be, chat client pressed ctrl+c to exit
				socket.close()
				CONNECTION_LIST.remove(socket)

#Starting program
if __name__ == '__main__':
	#List to keep track of socket descriptors
	CONNECTION_LIST = []
	RECV_BUFFER = 4096
	PORT = 5555
	quit = 'quit()\n'

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(('0.0.0.0', PORT))
	server_socket.listen(10)

	#Add server socket and standard input object to the list of readable connections
	input_server = sys.stdin
	CONNECTION_LIST.append(input_server)
	CONNECTION_LIST.append(server_socket)

#	print CONNECTION_LIST
	print "Chat Server started on port: " + str(PORT)

	while True:
		#Get the list sockets which are ready to be read through select
		read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
		for sock in read_sockets:
			#New connection
			if sock == server_socket:
				#Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print 'Client [{}, {}] connected'.format(addr[0], addr[1])
				broadcast_data(sockfd, '\b\b*** [{}:{}] joined the chat ***\n'.format(addr[0],addr[1]))
			#Standard input in the Server
			elif sock == input_server:
				server_msg = sys.stdin.readline()

				#Close Server connection
				if server_msg == quit:
					for kick in CONNECTION_LIST[2:]:
						kick.close()
						CONNECTION_LIST.remove(kick)
					CONNECTION_LIST[1].close()
					sys.exit()

				#Kill client using 'kill' command and port number
				kill = server_msg.split()
				if len(kill) == 2 and kill[0] == 'kill':
					try:
						port_kill = int(kill[1])
					except:
						sys.stdout.write('Usage: kill port_client\n')
						sys.stdout.flush()
						continue
					ff = True
					for kick in CONNECTION_LIST[2:]:
						peername = kick.getpeername()
						if port_kill == peername[1]:
							ff = False
							broadcast_data(kick, 'Client [{}:{}] is offline\n'.format(peername[0], peername[1]))
							print 'Client [{}:{}] kicked'.format(peername[0], peername[1])
							kick.close()
							CONNECTION_LIST.remove(kick)
							break
					if ff:
						sys.stdout.write('Unknown port number\n')
				elif kill and kill[0] == 'kill':
					sys.stdout.write('Usage: kill port_client\n')
					sys.stdout.flush()
					continue

			#Some incoming message from a client
			else:
				peername = sock.getpeername()
				#Data recieved from client, process it
				try:
					data = sock.recv(RECV_BUFFER)
					if data == quit:
						broadcast_data(sock, 'Client [{}:{}] is offline\n'.format(peername[0], peername[1]))
						print 'Client [{}:{}] disconnected'.format(peername[0], peername[1])
						sock.close()
						CONNECTION_LIST.remove(sock)
						continue
					if data:
#						print '[{}]: {}'.format(str(sock.getpeername()), data)
						broadcast_data(sock, '\b\b[{}:{}]> {}'.format(peername[0], peername[1], data))
				except:
					broadcast_data(sock, '\b\bClient [{}:{}] is offline\n'.format(addr[0], addr[1]))
					print 'Client [{}:{}] disconnected'.format(peername[0], peername[1])
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue

	server_socket.close()