import simpy
import random
import networkx as nx
from distsim import * 
import matplotlib.pyplot as plt

class FNode(Node):
	def __init__(self,*args):
		Node.__init__(self, *args)
		self.msgSent = False
		self.shouldSend = False
		self.data = None
		self.source = None


	def run(self):
		while True:
			yield self.mailbox.get(1)
			msg = self.receiveMessage()
			print('Node %d: Received %s Msg from Node %d at time %d' % (self.id,msg['type'],msg['sender'],self.env.now))
			if msg['type'] == "ROUND":
				if self.id == 0 and not self.msgSent:
					self.sendMessage({'type':'FLOOD','data':5,'source':0})
					print('Node %d: Sending FLOOD'  % self.id)
					self.msgSent = True
				else:
					if self.shouldSend and not self.msgSent:
						self.sendMessage({'type':'FLOOD','data':self.data,'source':self.source})
						print('Node %d: Sending FLOOD'  % self.id)
						self.msgSent = True

			elif msg['type'] == "FLOOD":
				self.data = msg['data']
				self.source = msg['source']
				print('Node %d: Received FLOOD from source %d' % (self.id,self.source))
				self.shouldSend = True
				self.sendMessageTo(msg['sender'],{'type':'ACK'})



# sys = System(FNode,10)
# sys.addEdge(0,1)
# sys.addEdge(1,2)
# sys.addEdge(1,3)
# sys.addEdge(3,7)
# sys.env.run(30)

#G = nx.path_graph(5)
G = nx.watts_strogatz_graph(7, 4, 0.9)
sys = System(FNode,nxGraph=G, roundInterval=3) #roundInterval=10 for rounds in 10 time
sys.env.run(50)

nx.draw_networkx(G)
plt.show()
# time=0
# while True:
# 	time +=1
# 	sys.env.run(time)


