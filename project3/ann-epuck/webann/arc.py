import random

class Arc:
	def __init__(self, owner_link, pre_synaptic_node, post_synaptic_node, weight=None):
		self.owner_link = owner_link
		self.pre_synaptic_node = pre_synaptic_node
		self.post_synaptic_node = post_synaptic_node
		self.current_weight = self.initial_weight = self.set_initial_weight(weight)


	def get_pre_synaptic_node(self):
		return self.pre_synaptic_node

	def get_post_synaptic_node(self):
		return self.post_synaptic_node

	def get_weight(self):
		return self.current_weight

	def get_initial_weight(self):
		return self.initial_weight

	def set_initial_weight(self, weight):
		if weight == None:
			return random.uniform(*self.owner_link.get_range())
		else:
			return weight

	def add_to_weight(self, weight):
		self.current_weight += weight
