import simpy
import random
import networkx as nx
from distsim import * 
import matplotlib.pyplot as plt

class FNode(Node):
	def __init__(self,*args):
		Node.__init__(self, *args)

	def run(self):
		while True:
			yield self.mailbox.get(1)
			msg = self.receiveMessage()
			print('Node %d: Received %s Msg from Node %d at time %d' % (self.id,msg['type'],msg['sender'],self.env.now))
			if msg['type'] == "ROUND":
				print('Node %d: neighbours' %self.id + str(list(self.neighbors.keys())))
				for i in self.neighbors.keys():
					self.sendMessageTo(i,{'type':'SAMPLE'})




# sys = System(FNode,10)
# sys.addEdge(0,1)
# sys.addEdge(1,2)
# sys.addEdge(1,3)
# sys.addEdge(3,7)
# sys.env.run(30)

G = nx.path_graph(5)
sys = System(FNode,nxGraph=G,roundInterval=3) #roundInterval=10 for rounds in 10 time
sys.env.run(50)

nx.draw_networkx(G)
plt.show()
# time=0
# while True:
# 	time +=1
# 	sys.env.run(time)


