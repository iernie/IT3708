import json


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

	def add_exiting_link(self, link):
		self.exiting_links.append(link)

	def add_entering_link(self, link):
		self.entering_links.append(link)


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

class Arc:
	def __init__(self, owner_link, pre_synaptic_node, post_synaptic_node):
		self.owner_link = owner_link
		self.pre_synaptic_node = pre_synaptic_node
		self.post_synaptic_node = post_synaptic_node
		self.current_weight = 0
		self.initial_weight = 0

class Node:
	def __init__(self, owner_layer):
		self.owner_layer = owner_layer
		self.membrane_potentional = 0
		self.activation_level = 0
		self.previous_activation_level = 0

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
				int(layer["threshold"]),
				)
			for i in range(layer["size"]):
				l.add_node(Node(l))
			self.layers[str(layer["name"])] = l

		for link in data["links"]:
			l = Link(
				str(link["pre_synaptic_layer"]),
				str(link["post_synaptic_layer"]),
				str(link["connection_topology"]),
				int(link["connection_probability"]),
				int(link["min_weight"]),
				int(link["max_weight"]),
				int(link["learn_rate"]),
				str(link["learning_rule"])
				)
			pre_synaptic_layer = str(link["pre_synaptic_layer"])
			post_synaptic_layer = str(link["post_synaptic_layer"])

			pre_nodes = [x for x in self.layers[pre_synaptic_layer].get_nodes()]
			post_nodes = [x for x in self.layers[post_synaptic_layer].get_nodes()]

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

			self.layers[pre_synaptic_layer].add_exiting_link(l)
			self.layers[post_synaptic_layer].add_entering_link(l)

			self.links.append(l)

		self.execution_sequence = [str(x) for x in data["execution_sequence"]]

if __name__ == '__main__':
	ann = ANN("ann.json")
