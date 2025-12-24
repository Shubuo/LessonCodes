#Simulation for distributed algorithms
__author__ = 'M. Tosun & C. U. Ileri'

import simpy
import random
import networkx as nx


# ============================================================================
# MsgManager
# ============================================================================
# Message manager is the communication backbone of the simulation.
# It is responsible for:
#   - keeping a global message queue indexed by future time steps,
#   - scheduling when each message will be delivered,
#   - broadcasting messages to all neighbors when receiver == 255,
#   - counting total number of messages sent in the system.
#
# Time in the environment (env.now) is discrete in this model. At each time
# step, MsgManager looks at the messages scheduled for that time and forwards
# them to the target nodes. A separate mailbox (simpy.Container) is used as a
# simple wake‑up mechanism so that nodes can react when new messages arrive.
class MsgManager(object):
	def __init__(self,env,nodes):
		self.env = env
		self.action1 = env.process(self.timeRun())
		self.action1 = env.process(self.mailboxRun())
		self.nodes = nodes
		self.messages = {}
		self.delayTime = 1
		self.mailbox = simpy.Container(env, capacity=1000, init=0)
		self.totalMessageSent = 0

	def timeRun(self):
		"""
		Main time loop of the message manager.

		At every time step:
		  1. advance simulation time by 1 unit,
		  2. check if there are messages scheduled for current time,
		  3. deliver these messages either as broadcast or unicast,
		  4. remove delivered messages from the queue.

		This function does NOT block on mailboxes of nodes, it only pushes
		messages into node.mailbox when they are ready to be processed.
		"""
		while True:
			yield self.env.timeout(1)  # Go to the next time step or wait for a message
			msgToBeSent = []

			# Find messages to be sent NOW
			if self.env.now in self.messages:
				msgToBeSent = self.messages[self.env.now]

			for msg in msgToBeSent:                
				if msg['receiver'] == 255:
					if msg['sender'] in self.nodes:
						keys = list(self.nodes[msg['sender']].neighbors.keys())
						random.shuffle(keys)
						for n in keys:
							self.forward_message(n,msg)
					# sender=-1 is from System (ROUND messages), skip broadcast
				else:
					self.forward_message(msg['receiver'],msg)

            # Delete SENT messages
			if self.env.now in self.messages:
				del(self.messages[self.env.now])
                
	
	def mailboxRun(self):
		"""
		Secondary loop that is triggered whenever a new message is added.

		This loop is similar to timeRun but it is woken up by mailbox.get(1)
		calls. The purpose is to support message delivery that is not strictly
		aligned with integer time steps, while still using the same message
		queue structure.
		"""
		while True:
			yield self.mailbox.get(1)
			msgToBeSent = []
			# Find messages to be sent NOW
			if self.env.now in self.messages:
				msgToBeSent = self.messages[self.env.now]

			for msg in msgToBeSent:                
				if msg['receiver'] == 255:
					if msg['sender'] in self.nodes:
						for n in self.nodes[msg['sender']].neighbors.keys():
							self.forward_message(n,msg)
					# sender=-1 is from System (ROUND messages), skip broadcast
				else:
					self.forward_message(msg['receiver'],msg)

            # Delete SENT messages
			if self.env.now in self.messages:
				del(self.messages[self.env.now])

	def addToMessageQueue(self,msg):
		"""
		Add a message to the global message dictionary.

		Message types:
		  - 'TIMER'  : converted into 'TIMEOUT' and scheduled in the future,
		  - 'ROUND'  : delivered immediately at current env.now,
		  - others   : delivered after fixed delayTime.

		The mailbox container is used only as a wake‑up signal for the
		mailboxRun() loop.
		"""
		if msg['type'] == 'TIMER':
			timestamp = self.env.now + msg['time']
			msg['type'] = 'TIMEOUT'
		else:
			self.totalMessageSent += 1
			if msg['type'] == 'ROUND':
				timestamp = self.env.now
			else:
				timestamp = self.env.now + self.delayTime

		if timestamp not in self.messages:
			self.messages[timestamp] = []
            
		self.messages[timestamp].append(msg)
		self.mailbox.put(1) 

	def forward_message(self, n, msg):
		"""
		Deliver a single message to node n if that node exists.

		The message is appended to the target node's local message buffer and
		its mailbox is incremented so that the node's run() coroutine wakes up.
		"""
		if n in self.nodes:  # Check if node exists
			self.nodes[n].messages.append(msg)
			self.nodes[n].mailbox.put(1)


# ============================================================================
# Node
# ============================================================================
# Base node model used by higher‑level distributed algorithms.
#
# A Node instance maintains:
#   - a reference to the global SimPy environment,
#   - its unique identifier (id),
#   - a reference to MsgManager for sending messages,
#   - a local mailbox (simpy.Container) used as wake‑up signal,
#   - a FIFO list of incoming messages,
#   - a neighbors dictionary that can store per‑neighbor metadata.
#
# The default run() method is intentionally minimal; concrete algorithms
# (such as MDSNode in algorithms.py) subclass Node and override run()
# to implement protocol‑specific behaviour.
class Node(object):
	def __init__(self,id,env,msgManager):
		self.env = env
		self.id = id
		self.msgManager = msgManager
		self.mailbox = simpy.Container(env, capacity=1000, init=0)
		self.messages = []
		self.neighbors = {}
		self.action = env.process(self.run())

	def run(self):
		"""
		Default behaviour of a node.

		This method is expected to be overridden by subclasses. In the base
		implementation it only prints 'running' once and then terminates,
		which is useful as a sanity check but not for real protocols.

		Algorithm‑specific node classes (for example MDSNode) implement
		their own run() method that usually:
		  - waits on mailbox.get(1),
		  - reads messages using receiveMessage(),
		  - updates local state and sends new messages.
		"""
		print('running')



	def sendMessageTo(self,to,msgdict):
		msgdict['sender'] = self.id
		msgdict['receiver'] = to
		self.msgManager.addToMessageQueue(msgdict)

	def sendMessage(self,msgdict):
		self.sendMessageTo(255,msgdict)

	def receiveMessage(self):
		return self.messages.pop(0)

	def addNeighbor(self,id,neighborDict):
		self.neighbors[id] = neighborDict

	def setTimer(self,name,time):
		self.sendMessageTo(self.id,{'type':'TIMER','name':name,'time':time})




# ============================================================================
# System
# ============================================================================
# System ties everything together:
#   - it owns the global SimPy environment,
#   - creates all Node objects (or subclasses of Node),
#   - constructs the neighbor relation either from:
#       * an explicit nodeCount (synthetic topology), or
#       * a NetworkX graph (nxGraph),
#   - creates a single MsgManager instance shared by all nodes,
#   - optionally runs syncRound() to generate global ROUND messages
#     with a given roundInterval.
#
# Higher‑level algorithms (such as Span MDS) usually interact only with
# System and a custom Node subclass; they do not need to manage SimPy
# details or low‑level message passing directly.
class System(object):
	def __init__(self,NodeObject=Node,nodeCount=None,nxGraph=None,roundInterval=None):
		self.env = simpy.Environment()
		self.nodes = {}
		self.NodeObject = NodeObject
		self.msgManager = MsgManager(self.env,self.nodes)

		if roundInterval != None:
			self.roundInterval = roundInterval
			self.round = 0
			self.action = self.env.process(self.syncRound())

		if nxGraph == None:
			self.nodeCount = nodeCount
			for i in range(nodeCount):
				self.addNode(i)
		else:
			self.nxGraph = nxGraph
			for i in self.nxGraph.nodes():
				self.addNode(i)
			for (id1,id2) in self.nxGraph.edges():
				self.addEdge(id1,id2)
				self.addEdge(id2,id1)

		self.msgManager.nodes = self.nodes

	def addNode(self,id):
		n = self.NodeObject(id,self.env,self.msgManager)
		self.nodes[id]=n
		
	def addEdge(self,id1,id2):
		self.nodes[id1].addNeighbor(id2,{})

	def syncRound(self):
		while True:
			self.round += 1
			keys = list(self.nodes.keys())
			random.shuffle(keys)
			for i in keys:
				self.msgManager.addToMessageQueue({'type': 'ROUND', 'round': self.round,'receiver': i,'sender':-1})
			yield self.env.timeout(self.roundInterval) 
	


