class Robot:
    def __init__(self):
        self.behaviours = self.get_behaviours()
        self.max_speed = 1.0
        self.weights = [[-1.0, -0.8],[-1.0, -0.8],[-0.4,  0.4],[ 0.0,  0.0],[ 0.0,  0.0],[ 0.4, -0.4],[-0.6, -0.8],[-0.6, -0.8]]
        self.offset = [0.5*self.max_speed, 0.5*self.max_speed]
        self.close_threshold = 0.5
        self.stagnation_threshold = 1.0
        self.push_threshold = 0.1

    def get_behaviours(self):
        d = {}
        def register(fn):
            d[fn.func_name] = fn

        @register
        def search(data):
            speed = [0.0, 0.0]
            for i in range(2):
                for j in range(8):
                    speed[i] += data[j] * self.weights[j][i]

                speed[i] = self.offset[i] + (speed[i] * self.max_speed)
                if speed[i] > self.max_speed:
                    speed[i] = self.max_speed
                elif speed[i] < -self.max_speed:
                    speed[i] = -self.max_speed

            return speed

        @register
        def retrieval(data):
            if (data[1][0],data[1][7]) < (self.push_threshold, self.push_threshold):
                return [self.max_speed, self.max_speed]
            else:
                sensors_right = sum(data[1][:4])
                sensors_left = sum(data[1][4:])
                if (sensors_left - sensors_right) < 0:
                    return [self.max_speed * 0.7, self.max_speed * -0.3]
                else:
                    return [self.max_speed * -0.3, self.max_speed * 0.7]

        @register
        def stagnation(data):
            # TODO
            return [0, 0]

        return d

    def update(self, data):
        # search, retrieval, stagnation
        behaviour = "search"

        if self.is_close_to_object(data[0]):
            behaviour = "retrieval"
        elif False:
            behaviour = "stagnation"

        return self.behaviours[behaviour](data)

    def is_close_to_object(self, data):
        for sensor in data:
            if sensor > self.close_threshold:
                return True
        return False
