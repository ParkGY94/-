import simpy
import random
#
#  blocking probability simulation
#
channelCap = 10 # 10 channels
guardchannel = 2
arrivalRate = 2.0  # call arrival rate
callDuration = 3.0  # call duration (or service time)
calltype = 0

class Call:
	numCallArrival = 0  # count the number of call arrivals
	numCallBlocked = 0  # count the number of call blocked
	def __init__(self, env, chns):
		self.env = env
		self.chns = chns
		Call.numCallArrival += 1
		self.env.process(self.useChannel())

	def useChannel(self):
		print ("Call arrived at ", self.env.now)
		if random.random()<0.8:
			print ("This call is original call")
			calltype = 1
		else :
			print ("This call is handover call")
			calltype = 2
		print ("# of channels in use = ", self.chns.count)
		# if channel is available, get into the system. Otherwise, it is blocked.
		if self.chns.count < channelCap-guardchannel:
			print ("New call starts service at ", self.env.now)
			with self.chns.request() as req:
				yield req
				yield env.timeout(random.expovariate(1.0/callDuration))
		else:
			if calltype == 1:
				print ("New call blocked at ", self.env.now)
				Call.numCallBlocked += 1
			elif self.chns.count < channelCap :
				print ("New call sercive at ", self.env.now)
				with self.chns.request() as req:
					yield req
					yield env.timeout(random.expovariate(1.0/callDuration))
			else :
				print ("New call blocked at ", self.env.now)
				Call.numCallBlocked +=1
		print ("blocking rate = ", float(Call.numCallBlocked)/Call.numCallArrival)

def callArrival(env):
	channels = simpy.Resource(env, capacity=channelCap)
	while True:
		yield env.timeout(random.expovariate(arrivalRate))
		cl = Call(env, channels)
        
env = simpy.Environment()
env.process(callArrival(env))
env.run(until=50)
