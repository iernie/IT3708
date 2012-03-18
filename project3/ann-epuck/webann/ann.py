import json
import layer as Layer
import link as Link
import node as Node

class ANN:
	def __init__(self, filename):
		self.layers = {}
		self.links = {}

		self.execution_sequence = []
		self.learning_order = []

		f = open(filename)
		data = json.load(f)
		f.close()
		for layer in data["layers"]:
			l = Layer.Layer(
					layer["learning"] == 1,
					layer["settling_rounds"] > 1,
					int(layer["settling_rounds"]),
					layer["active"] == 1,
					str(layer["activation_function"]),
					float(layer["threshold"]),
					)
			for i in range(layer["size"]):
				l.add_node(Node.Node(l))
			self.layers[str(layer["name"])] = l

		for link in data["links"]:
			pre_synaptic_layer = self.layers[str(link["pre_synaptic_layer"])]
			post_synaptic_layer = self.layers[str(link["post_synaptic_layer"])]

			l = Link.Link(
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

			connection_topology_function = l.get_connection_topology_function()
			connection_topology_function(l, pre_nodes, post_nodes)

			pre_synaptic_layer.add_exiting_link(l)
			post_synaptic_layer.add_entering_link(l)

			self.links[str(link["name"])] = l

		self.execution_sequence = [str(x) for x in data["execution_sequence"]]
		self.learning_order = [str(x) for x in data["learning_order"]]

	def print_ann(self):
		print "ANN:"
		print "Number of layers: %i" % len(self.layers)
		print "Number of links: %i" % len(self.links)
		print "Number of layers in execution sequence: %i" % len(self.execution_sequence)

		for name, layer in self.layers.items():
			print "\nLayer: %s" % name
			print "Number of nodes: %i" % len(layer.get_nodes())
			print "Number of entering links: %i" % len(layer.get_entering_links())
			print "Number of exiting links: %i" % len(layer.get_exiting_links())

		for name, link in self.links.items():
			print "\nLink: %s" % name
			print "Number of arcs: %i" % len(link.get_arcs())

	def execute(self, input_values):
		for node, i in zip(self.layers[self.execution_sequence[0]].get_nodes(),
				input_values):
			node.set_membrane_potential(i)

		count = 0
		execution_sequence = [self.layers[x] for x in self.execution_sequence]

		for layer in execution_sequence:
			layer.reset_delta_values()
			for settling_round in xrange(layer.get_settling_rounds()):
				if count > 0:
					layer.reset_nodes_membrane_potential()
				layer.run()
			count += 1
		output_values = []
		for node in execution_sequence[-1].get_nodes():
			output_values.append(node.get_activation_level())

		return output_values

	def execute_learning(self, input_values, target_values):
		output_values = self.execute(input_values)

		post_synaptic_layer = self.links[self.learning_order[0]].get_post_synaptic_layer()

		for node, i in zip(post_synaptic_layer.get_nodes(),
			target_values):
			node.set_target_value(i)

		learning_order = [self.links[x] for x in self.learning_order]

		for link in learning_order:
			print "Updating delta values..."
			link.get_post_synaptic_layer().update_delta_values()
			link.propagate_deltas()
			link.modify_weights()
			print "Done!"


	def reset(self):
		for layer in self.layers:
			layer.reset_nodes_membrane_potential()
			layer.reset_activation_level



if __name__ == '__main__':
	ann = ANN("ann.json")

	ann.print_ann()

	input_values = [0 for i in range(52)]
	output_values = ann.execute(input_values)

	print "\nSize: %d" % len(output_values)
	print "Result:"
	for o in output_values:
		print "%f " % o
