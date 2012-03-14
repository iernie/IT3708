import json
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

	def get_activation_function(self):
		return self.activation_function

	def add_exiting_link(self, link):
		self.exiting_links.append(link)

	def get_exiting_links(self):
		return self.get_exiting_links

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

class Arc:
	def __init__(self, owner_link, pre_synaptic_node, post_synaptic_node):
		self.owner_link = owner_link
		self.pre_synaptic_node = pre_synaptic_node
		self.post_synaptic_node = post_synaptic_node
		self.current_weight = 0
		self.initial_weight = 0

	def get_pre_synaptic_node(self):
		return self.pre_synaptic_node

	def get_post_synaptic_node(self):
		return self.post_synaptic_node

	def get_weight(self):
		return self.current_weight

	def get_initial_weight(self):
		return self.initial_weight

class Node:
	def __init__(self, owner_layer):
		self.owner_layer = owner_layer
		self.membrane_potential = 0
		self.activation_level = 0
		self.previous_activation_level = 0

	def set_membrane_potential(self, membrane_potential):
		self.membrane_potential = membrane_potential

	def get_activation_level(self):
		return self.activation_level

	def add_to_membrane_potential(self, membrane_potential):
		self.membrane_potential += membrane_potential

	def get_owner(self):
		return self.owner_layer

	def run_activation_function(self):
		self.previous_activation_level = self.activation_level

		activation_function = self.owner_layer.get_activation_function()

		if activation_function == "sigmoid_logistic":
			self.activation_level = (1.0/(1.0+math.exp(-self.membrane_potential)))
		elif activation_function == "sigmoid_tahn":
			self.activation_level = (math.exp(2*self.membrane_potential)-1.0)/(math.exp(2*self.membrane_potential)+1.0)
		elif activation_function == "step":
			if self.membrane_potential >= self.owner_layer.get_threshold():
				self.activation_level = 1.0
			else:
				self.activation_level = 0.0
		elif activation_function == "linear":
			self.activation_level = self.membrane_potential
		elif activation_function == "positive_linear":
			self.activation_level = max(0,self.membrane_potential)

class ANN:
	def __init__(self, filename):
		self.layers = {}
		self.links = []

		self.execution_sequence = []

		f = open(filename)
		data = json.load(f)
		f.close()
		for layer in data["layers"]:
			l = Layer(
				layer["learning"] == 1,
				layer["settling_rounds"] > 1,
				int(layer["settling_rounds"]),
				layer["active"] == 1,
				str(layer["activation_function"]),
				float(layer["threshold"]),
				)
			for i in range(layer["size"]):
				l.add_node(Node(l))
			self.layers[str(layer["name"])] = l

		for link in data["links"]:
			pre_synaptic_layer = self.layers[str(link["pre_synaptic_layer"])]
			post_synaptic_layer = self.layers[str(link["post_synaptic_layer"])]

			l = Link(
				pre_synaptic_layer,
				post_synaptic_layer,
				str(link["connection_topology"]),
				float(link["connection_probability"]),
				float(link["min_weight"]),
				float(link["max_weight"]),
				float(link["learn_rate"]),
				str(link["learning_rule"])
				)
			

			pre_nodes = [x for x in pre_synaptic_layer.get_nodes()]
			post_nodes = [x for x in post_synaptic_layer.get_nodes()]

			connection_topology = str(link["connection_topology"])
			
			if connection_topology == "full":
				nodes = [(i, j) for i in pre_nodes for j in post_nodes]
				for i,j in nodes:
					l.add_arc(Arc(l, i, j))
			elif connection_topology == "one_to_one":
				nodes = [(i, j) for i in pre_nodes for j in post_nodes if i == j]
				for i,j in nodes:
					l.add_arc(Arc(l, i, j))
			elif connection_topology == "stochastic":
				nodes = [(i, j) for i in pre_nodes for j in post_nodes]
				for i,j in nodes:
					if random.random() <= float(link["connection_probability"]):
						l.add_arc(Arc(l, i, j))
			elif connection_topology == "triangular":
				nodes = [(i, j) for i in pre_nodes for j in post_nodes if i != j]
				for i,j in nodes:
					l.add_arc(Arc(l, i, j))

			pre_synaptic_layer.add_exiting_link(l)
			post_synaptic_layer.add_entering_link(l)

			self.links.append(l)

		self.execution_sequence = [str(x) for x in data["execution_sequence"]]

	def print_ann(self):
		print "ANN:"
		print "Number of layers: %i" % len(self.layers)
		print "Number of links: %i" % len(self.links)
		print "Number of layers in execution sequence: %i" % len(self.execution_sequence)

		for name, layer in self.layers.items():
			print "\n Layer: %s" % name
			print "Number of nodes: %i" % len(layer.get_nodes())
			print "Number of entering links: %i" % len(layer.get_entering_links())
			print "Number of exiting links: %i" % len(layer.get_exiting_links())

		for link in self.links:
			print "\n Link:"
			print "Number of arcs: %i" % len(link.get_arcs())

	def execute(self, input_values):
		for node in self.layers[self.execution_sequence[0]].get_nodes():
			for i in input_values:
				node.set_membrane_potential(i)

		for layer in [self.layers[x] for x in self.execution_sequence]:
			for settling_round in xrange(layer.get_settling_rounds()):
				if settling_round > 0:
					layer.reset_nodes_membrane_potential()
				layer.run()
		output_values = []
		for node in self.layers[self.execution_sequence[len(self.execution_sequence)-1]].get_nodes():
			output_values.append(node.get_activation_level())

		return output_values

if __name__ == '__main__':
	ann = ANN("ann.json")

	input_values = [0.2, 0.1, 0.3, 0.5]
	output_values = ann.execute(input_values)

	print "Size: %d" % len(output_values)
	print "Result:"
	for o in output_values:
		print "%d " % o
