import random
import arc as Arc

class Link:
	def __init__(self, pre_synaptic_layer, post_synaptic_layer, connection_topology,
			connection_probability, min_weight, max_weight,learn_rate,
			learning_rule):
		self.arcs = []
		self.pre_synaptic_layer = pre_synaptic_layer
		self.post_synaptic_layer = post_synaptic_layer
		self.connection_topology = connection_topology
		self.connection_probability = connection_probability
		self.learn_rate = learn_rate
		self.learning_rule = learning_rule
		self.min_weight = min_weight
		self.max_weight = max_weight

	def add_arc(self, arc):
		self.arcs.append(arc)

	def get_range(self):
		return (self.min_weight,self.max_weight)

	def get_arcs(self):
		return self.arcs

	def get_pre_synaptic_layer(self):
		return self.pre_synaptic_layer

	def get_post_synaptic_layer(self):
		return self.post_synaptic_layer

	def get_connection_topology_function(self):
		d = {}
		def register(fn):
			d[fn.func_name] = fn

		@register
		def full(link, pre_nodes, post_nodes):
			nodes = [(i, j) for i in pre_nodes for j in post_nodes]
			for i,j in nodes:
				link.add_arc(Arc.Arc(link, i, j))

		@register
		def one_to_one(link, pre_nodes, post_nodes):
			nodes = [(i, j) for i in pre_nodes for j in post_nodes if i == j]
			for i,j in nodes:
				link.add_arc(Arc.Arc(link, i, j))

		@register
		def stochastic(link, pre_nodes, post_nodes):
			nodes = [(i, j) for i in pre_nodes for j in post_nodes]
			for i,j in nodes:
				if random.random() <= link.get_connection_probability():
					link.add_arc(Arc.Arc(link, i, j))

		@register
		def triangular(link, pre_nodes, post_nodes):
			nodes = [(i, j) for i in pre_nodes for j in post_nodes if i != j]
			for i,j in nodes:
				link.add_arc(Arc.Arc(link, i, j))

		@register
		def optimal(link, pre_nodes, post_nodes):
			for i in xrange(len(pre_nodes)):
				for j in xrange(len(post_nodes)):
					pre_node = pre_nodes[i]
					post_node = post_nodes[j]
					weight = 0.0
					if (i,j) == (0,1) or (i,j) == (1,0): weight = 1.0
					link.add_arc(Arc.Arc(link, pre_node, post_node, weight))

		return d[self.connection_topology]

	def get_connection_probability(self):
		return self.connection_probability

	def propagate_deltas(self):
		for arc in self.arcs:
			pre_synapic_node = arc.get_pre_synaptic_node()
			post_synaptic_node = arc.get_post_synaptic_node()
			pre_synapic_node.add_to_delta_value(
				post_synaptic_node.get_delta_value()*
				arc.get_weight())

	def modify_weights(self):
		for arc in self.arcs:
			pre_synapic_node = arc.get_pre_synaptic_node()
			post_synaptic_node = arc.get_post_synaptic_node()
			arc.add_to_weight(self.learn_rate*
				pre_synapic_node.get_activation_level()*
				post_synaptic_node.get_delta_value())
