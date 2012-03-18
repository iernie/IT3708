from __future__ import division
import math

class Layer:
	def __init__(self, learning, quicent, settling_rounds, 
			is_active, activation_function, threshold):
		self.nodes = []
		self.entering_links = []
		self.exiting_links = []
		self.learning = learning
		self.quicent = quicent
		self.settling_rounds = settling_rounds
		self.is_active = is_active
		self.activation_function = activation_function
		self.threshold = threshold

	def add_node(self, node):
		self.nodes.append(node)

	def get_nodes(self):
		return self.nodes

	def get_activation_function_name(self):
		return self.activation_function

	def get_activation_function(self):
		d = {}
		def register(f):
			d[f.func_name] = f
			return f

		@register
		def sigmoid_logistic(n, a=None):
			return (1.0/(1.0+math.exp(-n)))

		@register
		def sigmoid_tanh(n, a=None):
			return (math.exp(2*n)-1.0)/(math.exp(2*n)+1.0)

		@register
		def step(n, a=None):
			if n >= a.owner_layer.get_threshold():
				print "hi",n
				return 1.0
			else:
				print "hn",n
				return 0.0

		@register
		def linear(n, a=None):
			return n

		@register
		def positive_linear(n, a=None):
			return max(0.0, n)

		return d[self.activation_function]

	def add_exiting_link(self, link):
		self.exiting_links.append(link)

	def get_exiting_links(self):
		return self.exiting_links

	def add_entering_link(self, link):
		self.entering_links.append(link)

	def get_entering_links(self):
		return self.entering_links

	def is_activated(self):
		return self.is_active

	def get_settling_rounds(self):
		return self.settling_rounds

	def reset_nodes_membrane_potential(self):
		for node in self.nodes:
			node.set_membrane_potential(0.0)

	def reset_activation_level(self):
		for node in self.nodes:
			node.reset_activation_level()

	def reset_delta_values(self):
		for node in self.nodes:
			node.set_delta_value(0.0)

	def get_threshold(self):
		return self.threshold

	def run(self):
		links = [x for x in self.entering_links if x.get_pre_synaptic_layer().is_activated()] 
		for link in links:
			for arc in link.get_arcs():
				post_node = arc.get_post_synaptic_node()
				pre_node = arc.get_pre_synaptic_node()
				post_node.add_to_membrane_potential(pre_node.get_activation_level()*arc.get_weight())

		for node in self.nodes:
			node.run_activation_function()

	def update_delta_values(self):
		for node in self.nodes:
			node.update_delta_value()
