"""
RFID Simulator: 
 1. ISO 18000-6 Type B (binary tree)
 2. one reader and multiple tags 
"""

import simpy
import random

"""
  class slotSignal: generate slot signal to Reader and tags
"""
class slotSignal:
	slotEvt = 0  # slot event 
	def __init__(self, Tslot):
		self.env = env
		self.Tslot = Tslot
		slotSignal.slotEvt = env.event()  # slot event initialization 
		
		# schedule process
		env.process(self.run())

	def run(self):
		while True:
			# periodic slot generation 
			yield self.env.timeout(self.Tslot)
			print "slot begins at t = %4.1f" %(self.env.now)
			slotSignal.slotEvt.succeed()   # trigger event, send slot signal 
			slotSignal.slotEvt = env.event() # slot event initialization 
"""
   RFID tag class
"""
class Tag:
	tagID = 0
	def __init__(self, env):
		# set mobile ID
		self.tagID = Tag.tagID
		Tag.tagID += 1
		self.env = env
		# schedule process
		env.process(self.run())
	
	def run(self):
		while True:
			# one slot passed
			yield slotSignal.slotEvt
			#print "Tag %d: slot begins" %(self.tagID)
			
			# start contention (or transmission)
			Reader.colCount += 1
			
			# wait for the feedback from the reader 
			ret = yield (Reader.idleMsgEvt | Reader.succeedMsgEvt | Reader.failMsgEvt)
			if ret.values()[0] == 'idle':
				print "idle"
				pass
			elif ret.values()[0]  == 'succeed':
				print "succeed"
				pass
			elif ret.values()[0] == 'fail':
				print "collision"
				pass
			 
			
"""
   RFID reader class
"""
class Reader:
	# define message events
	succeedMsgEvt = 0
	failMsgEvt = 0
	idleMsgEvt = 0
	
	# collision count
	colCount = 0 
	
	# successful read count
	readCount = 0
	def __init__(self, env, tSlot):
		# initialize message event
		Reader.succeedMsgEvt = env.event()
		Reader.failMsgEvt = env.event()
		Reader.idleMsgEvt = env.event()
		
		# initialize collistion count
		Reader.colCount = 0
		
		self.env = env
		self.tSlot = tSlot # slot time
		
		# schedule process
		env.process(self.run())
	
	def run(self):
		while True:
			# one slot passed
			yield slotSignal.slotEvt
			print "Reader: slot begins "
			
			# receiving the packets
			
			# check the collision
			tEpsilon = 0.1
			yield self.env.timeout(self.tSlot - tEpsilon)
			
			# send the feedback 0.1 time unit before the next slot
			if Reader.colCount == 0: 
				# send IDLE message
				print "Feedback: slot idle"
				Reader.idleMsgEvt.succeed(value='idle')
				Reader.idleMsgEvt = env.event()

			elif Reader.colCount == 1:
				# send SUCCEED message
				print "Feedback: ID read succeed"
				Reader.succeesMsgEvt.succeed(value='succeed')
				Reader.succeedMsgEvt = env.event()				

			elif Reader.colCount > 1:
				# send FAIL message (collision)
				print "Feedback: slot collision"
				Reader.failMsgEvt.succeed(value='fail')
				Reader.failMsgEvt = env.event()
			
			# reset collision count
			Reader.colCount = 0
			
simTime = 200		
env = simpy.Environment()
slotSig = slotSignal(1.0)
numTags = 100
tagSet = [Tag(env) for i in range(numTags)]
reader = Reader(env, 1.0)
env.run(until=simTime)

print "Throughput = %f" %(Reader.readCount/float(simTime))
           
