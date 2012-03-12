import json

class Layer:
	def __init__(self, learning, quicent, settling_rounds, 
		is_active, activation_function, threshold):

		self.learning = learning
		self.quicent = quicent
		self.settling_rounds = settling_rounds
		self.is_active = is_active
		self.activation_function = activation_function
		self.threshold = threshold

	def add_node(self, node):
		pass

class Node:
	def __init__(self, layer_name):
		self.layer_name = layer_name

class ANN:
	def __init__(self, filename):
		self.layers = []
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
				l.add_node(Node(str(layer["name"])))
			self.layers.append(l)

		#TODO Links

		self.execution_sequence = [str(x) for x in data["execution_sequence"]]
		print self.execution_sequence



if __name__ == '__main__':
	ann = ANN("ann.json")