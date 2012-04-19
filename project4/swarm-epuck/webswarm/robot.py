STAGNATION_THRESHOLD = 5

class Robot:
	def __init__(self):
		self.behaviours = self.get_behaviours()
		self.max_speed = 1.0
		self.weights = [[-1.0, -0.8],[-1.0, -0.8],[-0.4,  0.4],[ 0.0,  0.0],[ 0.0,  0.0],[ 0.4, -0.4],[-0.6, -0.8],[-0.6, -0.8]]
		self.offset = [0.5*self.max_speed, 0.5*self.max_speed]
		self.close_threshold = 0.5
		self.stagnation_threshold = 1.0


        self.recovering = False
        self.counter = 0
        self.last_data = None

	def get_behaviours(self):
		d = {}
		def register(fn):
			d[fn.func_name] = fn

		@register
		def search(input):
			speed = [0.0, 0.0]
			for i in range(2):
				for j in range(8):
					speed[i] += input[j] * self.weights[j][i]

				speed[i] = self.offset[i] + (speed[i] * self.max_speed)
				if speed[i] > self.max_speed:
					speed[i] = self.max_speed
				elif speed[i] < -self.max_speed:
					speed[i] = -self.max_speed

			return speed

		@register
		def retrieval(input):
			if (input[0],input[7]) < (self.push_threshold, self.push_threshold):
				return [self.max_speed, self.max_speed]

		@register
		def stagnation(data):
			# TODO
            lw,rw = 0,0
            if self.recovering:
                rw = -self.max_speed
                lw = -self.max_speed
                if counter > 50:
                    lw = 0
                if counter > 100:
                    self.counter = 0
                    self.recovering = False
            else:
                ## Check for stagnation
                if self.last_input:
                    pass
            self.last_data = data
			return (lw,rw)

		return d

	def update(self, input):

		# search, retrieval, stagnation
		if self.is_close_to_object(input):
			behaviour = self.behaviours["retrieval"]
		else:
			behaviour = self.behaviours["search"]

		return behaviour(input)

	def is_close_to_object(self, input):
		for sensor in input:
			if sensor > self.close_threshold:
				return True
		return False
