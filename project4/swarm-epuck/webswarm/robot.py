import random

class Robot:
    def __init__(self):
        self.behaviours = self.get_behaviours()
        self.max_speed = 1.0
        self.weights = [[-1.0, -0.8],[-1.0, -0.8],[-0.4,  0.4],[ 0.0,  0.0],[ 0.0,  0.0],[ 0.4, -0.4],[-0.6, -0.8],[-0.6, -0.8]]
        self.offset = [0.5*self.max_speed, 0.5*self.max_speed]
        self.stagnation_threshold = 0.001
        self.retrieval_threshold = 0.3
        self.retrieval_light_threshold = 0.4

        self.recovering = False
        self.counter = 0
        self.last_data = None

    def get_behaviours(self):
        d = {}
        def register(fn):
            d[fn.func_name] = fn

        @register
        def search(data):
            speed = [0.0, 0.0]
            for i in range(2):
                for j in range(8):
                    speed[i] += data[0][j] * self.weights[j][i]

                speed[i] = self.offset[i] + (speed[i] * self.max_speed)
                speed[i] = self.minmax(speed[i], -self.max_speed, self.max_speed)

            return speed

        @register
        def retrieval(data):
            if (data[0][0] > self.retrieval_threshold and data[0][7] > self.retrieval_threshold):
                return [self.max_speed, self.max_speed]
            else:
                sensors_left = sum(data[0][4:])
                sensors_right = sum(data[0][:4])
                if (sensors_left - sensors_right) < 0:
                    return [self.max_speed * 0.7, self.max_speed * -0.3]
                else:
                    return [self.max_speed * -0.3, self.max_speed * 0.7]

        @register
        def stagnation(data):
            lw,rw = 0,0
            rw = -self.max_speed
            lw = -self.max_speed
            if self.counter > 50:
                lw = 0
            if self.counter > 100:
                self.counter = 0
                self.recovering = False
                    
            self.counter += 1
            return (lw,rw)

        return d


    def update(self, data):
        # search, retrieval, stagnation
        behaviour = "search"

        if self.retrieval_check(data):
            behaviour = "retrieval"
        elif self.stagnation_check(data):
            behaviour = "stagnation"

        print behaviour
        return self.behaviours[behaviour](data)

    def minmax(self, data, min_value, max_value):
        return min(max(data,min_value),max_value)

    def retrieval_check(self, data):
        for prox,light in zip(data[0],data[1]):
            print prox, light
            if (prox > self.retrieval_threshold and light > self.retrieval_light_threshold):
                return True
        return False

    def stagnation_check(self, data):
        if self.recovering: return True
        if self.last_data:
            if ( abs(self.last_data[0][0] - data[0][0]) < self.stagnation_threshold
              or abs(self.last_data[0][7] - data[0][7]) < self.stagnation_threshold
              or self.last_data == data ):
                if self.counter > 100:
                    self.counter = 0
                    self.recovering = True
                    return True
        self.last_data = data
        self.counter += 1 
        return False
