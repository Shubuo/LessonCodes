import simpy
import random
import networkx as nx
from distsim import * 
import matplotlib.pyplot as plt

class FNode(Node):
	def __init__(self,*args):
		Node.__init__(self, *args)
		self.msgSent = False

	def run(self):
		if self.id == 0:
			self.setTimer('timer1',2)

		while True:
			yield self.mailbox.get(1)
			msg = self.receiveMessage()
			print('Node %d: Received %s Msg from Node %d at time %d' % (self.id,msg['type'],msg['sender'],self.env.now))
			if msg['type'] == "FLOOD":
				data = msg['data']
				if not self.msgSent:
					self.sendMessage({'type':'FLOOD','data':data})
					self.msgSent = True

			elif msg['type'] == "TIMEOUT":
				if msg['name'] == 'timer1':
					if self.id == 0: 
						self.sendMessage({'type':'FLOOD','data':5}) 
						self.msgSent = True




# sys = System(FNode,10)
# sys.addEdge(0,1)
# sys.addEdge(1,2)
# sys.addEdge(1,3)
# sys.addEdge(3,7)
# sys.env.run(30)

#G = nx.path_graph(5)
G = nx.watts_strogatz_graph(7, 4, 0.9)
sys = System(FNode,nxGraph=G) #roundInterval=10 for rounds in 10 time
sys.env.run(30)

nx.draw_networkx(G)
plt.show()
# time=0
# while True:
# 	time +=1
# 	sys.env.run(time)


