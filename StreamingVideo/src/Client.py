from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os,time

from RtpPacket import RtpPacket
from HandleInfo import HandleInfo
CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	DESCRIBE = 4

	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.payloadLen = 0
		self.startTimePlay = 0
		self.lengtTimeRecvPkg = 0
		self.pkgRtpRecv = 0
		self.handleinfo = HandleInfo()
		self.logtime = [0]
		self.logbps = [0]
		self.logbyte = [0]
		self.totalPkgRecv = 0
		self.ratePkgLosst = 0
		self.dataratepersecond = 0
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)

		#Create Describe button
		self.describe = Button(self.master, width = 20, padx=3, pady=3)
		self.describe["text"] = "Describe"
		self.describe["command"] = self.describeMedia
		self.describe.grid(row=1, column=4, padx=2, pady=2)

		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=3, sticky=W+E+N+S, padx=5, pady=5) 

		#Create a label to display statistic
		self.ststic = Label(self.master,width=30)
		self.ststic.grid(row=0,column=3,columnspan=2,padx=5,pady=5)
	
	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)		
		self.master.destroy() # Close the gui window
		os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Set time when button is pressed
			self.startTimePlay = time.time()
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
	
	def describeMedia(self):
		if self.state != self.INIT:
			self.sendRtspRequest(self.DESCRIBE)

	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		while True:
			try:
				#Type of data is a byte object, with lenght 20480 byte

				data = self.rtpSocket.recv(20480)
				# the time period between sending and receiving package
				self.lengtTimeRecvPkg = time.time() - self.startTimePlay
				#Update startTimePlay
				self.startTimePlay = time.time()
				self.logtime.append(self.logtime[-1]+self.lengtTimeRecvPkg)
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					#Get sequence number
					currFrameNbr = rtpPacket.seqNum()				
					if currFrameNbr > self.frameNbr: # Discard the late packet
						self.frameNbr = currFrameNbr
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
						self.pkgRtpRecv += 1
					#Count number packet loss here
					#else:
					#	packageloss += 1

			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				elif self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
				else:
					# self.handleinfo.drawBytetoScnd(time=self.logtime,data=self.logbps,label='Times\nBytes to seconds')
					# self.handleinfo.drawByte(time=self.logtime,data=self.logbyte,label='Times\nBytes')
					# print('-'*60)
					# traceback.print_exc(file=sys.stdout)
					# print('-'*60)
					self.ststic["text"] = "Total Bytes Received: {} bytes\nData Rate: {:.2f} bytes/s\nPackage loss rate: {} ".format(self.payloadLen,self.dataratepersecond,self.ratePkgLosst)
					break

					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()

		#Get lenght of payload -- du lieu cua data nhan duoc thua 33 bytes so voi data gui qua rtsp
		self.payloadLen += sys.getsizeof(data) - 33
		self.logbyte.append(self.logbyte[-1]+self.payloadLen)
		# Data bytes per seconds
		self.dataratepersecond = (sys.getsizeof(data)-33)/self.lengtTimeRecvPkg
		self.logbps.append(self.dataratepersecond)
		self.ststic["text"] = "Total Bytes Received: {} bytes\nData Rate: {:.2f} bytes/s\nPackage loss rate: {}".format(self.payloadLen,self.dataratepersecond,self.ratePkgLosst)
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=288) 
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			self.rtspSeq += 1
			# Write the RTSP request to be sent.
			request = 'SETUP ' + self.fileName + ' RTSP/1.0\nCSeq ' + str(self.rtspSeq) + '\nTransport: RTP/UDP; client_port= ' + str(self.rtpPort)
			
			# Keep track of the sent request.
			self.requestSent = self.SETUP
		
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = 'PLAY ' + self.fileName + ' RTSP/1.0\nCSeq: ' +str(self.rtspSeq) + '\nSession: ' +str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.PLAY
		
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = 'PAUSE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' +str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.PAUSE
			
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = 'TEARDOWN ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' +str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN
		# Describe request
		elif requestCode == self.DESCRIBE and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq +=1

			#Write RTSP request to be sent
			request = 'DESCRIBE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' +str(self.sessionId)

			#Keep track of the sent request
			self.requestSent = self.PAUSE
		else:
			return
		
		# Send the RTSP request using rtspSocket.
		self.rtspSocket.send(request.encode("utf-8"))
		
		print('\nData sent:\n' + request)
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True:
			reply = self.rtspSocket.recv(1024)
			
			if reply: 
				self.parseRtspReply(reply.decode("utf-8"))
			
			# Close the RTSP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				self.rtspSocket.shutdown(socket.SHUT_RDWR)
				self.rtspSocket.close()
				break
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		lines = data.split('\n')
		if len(lines) == 4:
			datatemp = lines[:-1]
			self.handleinfo.writeFile(lines[-1])
			print("\nData recieve:\n")
			for dt in datatemp:
				print(dt)
			seqNum = int(lines[1].split(' ')[1])
		elif len(lines) == 3:
			print("\nData recieve:\n",data)
		elif len(lines) == 5:
			self.totalPkgRecv = int(lines[-1])
			if self.totalPkgRecv != 0:
				self.ratePkgLosst = self.pkgRtpRecv / self.totalPkgRecv
		seqNum = int(lines[1].split(' ')[1])
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
						#-------------
						# TO COMPLETE
						#-------------
						# Update RTSP state.
						self.state = self.READY
						# Open RTP port.
						self.openRtpPort()
					elif self.requestSent == self.PLAY:
						self.state = self.PLAYING
					elif self.requestSent == self.PAUSE:
						self.state = self.READY
						
						# The play thread exits. A new thread is created on resume.
						if self.state == self.PLAYING:
							self.playEvent.set()
					elif self.requestSent == self.TEARDOWN:
						self.state = self.INIT
						
						# Flag the teardownAcked to close the socket.
						self.teardownAcked = 1 
						pass
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)
		
		try:
			# Bind the socket to the address using the RTP port given by the client user
			# ...
			self.rtpSocket.bind(('',self.rtpPort))
		except:
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()
	
	def handleInfoDescribe(self,data):
		info = data.split(' ')

