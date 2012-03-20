class Node:
	def __init__(self, owner_layer):
		self.owner_layer = owner_layer
		self.membrane_potential = 0.0
		self.activation_level = 0.0
		self.previous_activation_level = 0.0
		self.delta_value = 0.0
		self.target_value = 0.0

	def set_membrane_potential(self, membrane_potential):
		self.membrane_potential = membrane_potential

	def get_activation_level(self):
		return self.activation_level

	def reset_activation_level(self):
		self.activation_level = 0.0

	def add_to_membrane_potential(self, membrane_potential):
		self.membrane_potential += membrane_potential

	def get_owner(self):
		return self.owner_layer

	def run_activation_function(self):
		self.previous_activation_level = self.activation_level

		activation_function = self.owner_layer.get_activation_function()
		self.activation_level = activation_function(self.membrane_potential, self)

	def get_delta_value(self):
		return self. delta_value

	def set_delta_value(self, value):
		self.delta_value = value

	def add_to_delta_value(self, value):
		self.delta_value += value

	def set_target_value(self, value):
		self.target_value = value

	def get_target_value(self):
		return self.target_value

	def update_delta_value(self):
		activation_function = self.get_activation_function(
			self.owner_layer.get_activation_function_name())
		self.delta_value = activation_function(self.activation_level)*get_difference()

	def get_activation_function(self, name):
		d = {}
		def register(fn):
			d[fn.func_name] = fn
			return fn

		@register
		def sigmoid_logistic(activation_level):
			return activation_level*(1.0 - activation_level)
			

		@register
		def sigmoid_tanh(activation_level):
			return 1.0 - activation_level**2

		@register
		def step(activation_level):
			return 1.0

		@register
		def linear(activation_level):
			return 1.0

		@register
		def positive_linear(activation_level):
			return 1.0

		return d[name]

	def get_difference(self):
		if len(self.owner_layer.get_exiting_links()) == 0:
			return self.target_value - self.activation_level
		else:
			return self.delta_value
