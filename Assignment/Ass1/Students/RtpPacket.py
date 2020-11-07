import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	
	def __init__(self):
		self.header = bytearray(HEADER_SIZE)
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		self.header = bytearray(HEADER_SIZE)
		#--------------
		# TO COMPLETE
		#--------------
		# Fill the header bytearray with RTP header fields
		
		# header[0] = ...
		# ...

		# Version + P(padding) + X(extension) + CC	
		self.header[0] = version << 6
		self.header[0] = self.header[0] | padding << 5
		self.header[0] = self.header[0] | extension << 4
		self.header[0] = self.header[0] | cc

		# M(Marker) +PT(Payload type)
		self.header[1] = marker << 7
		self.header[1] = self.header[1] | pt

		# Sequence number
		self.header[2] = (seqnum & 0xFF00) >> 8
		self.header[3] = (seqnum & 0xFF)
		#Timestamp
		self.header[4] = (timestamp >> 24) & 0xFF
		self.header[5] = (timestamp >> 16) & 0xFF
		self.header[6] = (timestamp >> 8) & 0xFF
		self.header[7] = timestamp & 0xFF

		# ssrc(SSRC identifier)
		self.header[8] = (ssrc >> 24) & 0xFF
		self.header[9] = (ssrc >> 16) & 0xFF
		self.header[10] = (ssrc >> 8) & 0xFF
		self.header[11] = ssrc & 0xFF

		print(self.header)
		# Get the payload from the argument
		# self.payload = ...
		self.payload = payload

	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload
