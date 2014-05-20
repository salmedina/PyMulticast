#!/usr/bin/python
import socket
import time
import struct
import sys
import os.path
import yaml

#GLOBAL DEFAULTS
CONFIG_FILE = "config.yaml"
ANY_ADDR = '0.0.0.0'
MCAST_ADDR = '224.0.1.60'
SENDER_PORT = 1501
MCAST_PORT = 10000

def LoadConfigFile():
	global MCAST_ADDR
	global SENDER_PORT
	global MCAST_PORT
	if os.path.isfile(CONFIG_FILE):
		try:
			configFile = open(CONFIG_FILE, 'r')
			config = yaml.load(configFile)
			MCAST_ADDR = config["mcastIP"]
			SENDER_PORT = config["senderPort"]
			MCAST_PORT =  config["mcastPort"]
			print("Config file loaded")
		except e:
			print("No %s file found. Loading default values."%CONFIG_FILE)
	else:
		print("No config.yaml file found. Loading default values.")

	return

def PrintConfig():
	print("Sender Port: 		%d"%SENDER_PORT)
	print("Multicast Address:	%s"%MCAST_ADDR)
	print("Multicast Port:		%d"%MCAST_PORT)

def Sender():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(0.2)
	ttl = struct.pack('b', 1)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		time.sleep(1)
		print("Message sent")
		sock.sendto(str(time.time()), (MCAST_ADDR, MCAST_PORT) );

	sock.close()
	return

def Receiver():
	# Create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# Bind to the server address
	sock.bind(('', MCAST_PORT))
	# Tell the operating system to add the socket to the multicast group
	group = socket.inet_aton(MCAST_ADDR)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	status = sock.setsockopt(socket.IPPROTO_IP, 
							socket.IP_ADD_MEMBERSHIP, 
							mreq)

	# Receive/respond loop
	while True:
		try:
			data, addr = sock.recvfrom(1024)
			ts = time.time()
			print "Message received [%s:%d]: %s"%(addr[0], addr[1], data)
			print "Clock difference: %.3f [s]"%(ts-float(data))
		except socket.error, e:
			print(e)
			time.sleep(1)
			pass

	sock.close()
	return

## MAIN PROGRAM
if __name__ == '__main__':
	print("***   Multicasting   ***")
	LoadConfigFile()
	PrintConfig()

	args = sys.argv
	if len(args)<2 or args == "-s":
		Sender()
	else:
		Receiver()