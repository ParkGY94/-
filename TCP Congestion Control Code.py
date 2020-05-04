import simpy
import random
RTT = 1
class Network:
    ConWin =1
    ConWin = int(ConWin)
    threshold = 1
    Congestion =0
    #Timeout, 3Duplicate ACK
    delay = 0
    loss = 0
    def __init__(self, env):
        Network.ConWin=1
        Network.ConWin = int(Network.ConWin)
        Network.threshold =1
        Network.Congestion = 0
        Network.delay = 0
        Network.loss = 0
        self.env = env
        env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(RTT)
            if random.random() < 0.1:
                Network.delay = 1
                Network.loss = 0
            elif random.random() > 0.9:
                Network.loss = 1
                Network.delay = 0
            else:
                Network.delay =0
                Network.loss=0

class TCPSender:
    PacketNum =1
    sendEvt = 0
    def __init__(self,env):
        TCPSender.PacketNum = 1
        self.env = env
        TCPSender.sendEvt = env.event()
        env.process(self.run())

    def run(self):
        while True:
            print("ConWin = ", Network.ConWin)
            yield self.env.timeout(RTT)
            for i in range (Network.ConWin):
                TCPSender.sendEvt.succeed()
                TCPSender.sendEvt = env.event()
                print(TCPSender.PacketNum, "th Packet start sending at t = %4.1f" % (self.env.now))
                if Network.delay == 0 & Network.loss == 0:
                    TCPSender.PacketNum +=1/Network.ConWin
                elif Network.loss == 1:
                    TCPSender.PacketNum += 1/Network.ConWin
                elif Network.delay == 1:
                    TCPSender.PacketNum += 1/Network.ConWin


class TCPReceiver:
    fail = 0
    PacketNum = 1
    def __init__(self, env):
        TCPReceiver.fail=0
        TCPReceiver.PacketNum=1
        self.env = env
        env.process(self.run())

    def run(self):
        while True:
            yield TCPSender.sendEvt
            if Network.Congestion ==0:
                if Network.loss == 1:
                    print("sending was failed")
                    TCPReceiver.fail+=1
                elif Network.delay == 1:
                    print ("Timeout was happend")
                    yield self.env.timeout(RTT/2)
                    Network.threshold = Network.ConWin / 2
                    Network.ConWin = 1
                    Network.Congestion +=1
                    TCPSender.PacketNum = TCPReceiver.PacketNum
                else:
                    print((TCPSender.PacketNum-1), "th Packet sending was successful")
                    Network.ConWin *=2
                    if TCPSender.PacketNum == TCPReceiver.PacketNum+1:
                        print(TCPReceiver.PacketNum, "th Packtet ACK start sending")
                        TCPReceiver.PacketNum+=1
                    else:
                        TCPReceiver.fail +=1
                        print(TCPReceiver.PacketNum, "th Packtet ACK start sending")

            else:
                if Network.loss == 1:
                    print("sending was failed")
                    TCPReceiver.fail+=1
                    Network.loss =0
                elif Network.delay == 1:
                    yield self.env.timeout((random.random()/2)+(RTT/2))
                    print ("Timeout was happend Delayed ACK arrived")
                    Network.threshold = Network.ConWin / 2
                    Network.ConWin = 1
                    Network.Congestion +=1
                    Network.delay =0
                    TCPSender.PacketNum = TCPReceiver.PacketNum
                else:
                    print((TCPSender.PacketNum - 1), "th Packet sending was successful")
                    if Network.ConWin <= Network.threshold/2:
                        Network.ConWin *=2
                    else:
                        Network.ConWin += 1
                    if TCPSender.PacketNum == TCPReceiver.PacketNum + 1:
                        TCPReceiver.PacketNum += 1
                    else:
                        TCPReceiver.fail += 1
                    print(TCPReceiver.PacketNum, "th Packtet ACK start sending")

            if TCPReceiver.fail ==3:
                print ("3Duplicated ACK was happend")
                Network.threshold = Network.ConWin /2
                Network.threshold = int(Network.threshold)
                Network.ConWin = Network.threshold
                TCPReceiver.fail = 0
                Network.Congestion += 1
                TCPSender.PacketNum=TCPReceiver.PacketNum

simTime = 30
env = simpy.Environment()
Network = Network(env)
Sender = TCPSender(env)
Receiver = TCPReceiver(env)

env.run(until=simTime)
