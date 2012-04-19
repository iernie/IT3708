import random

class Robot:
    def __init__(self):
        self.behaviours = self.get_behaviours()
        self.max_speed = 1.0
        self.weights = [[-1.0, -0.8],[-1.0, -0.8],[-0.4,  0.4],[ 0.0,  0.0],[ 0.0,  0.0],[ 0.4, -0.4],[-0.6, -0.8],[-0.6, -0.8]]
        self.offset = [0.5*self.max_speed, 0.5*self.max_speed]
        self.stagnation_threshold = 0.002
        self.retrieval_threshold = 0.3
        self.retrieval_light_threshold = 0.1

        self.recovering = False
        self.counter = 0
        self.last_data = None

    def get_behaviours(self):
        d = {}
        def register(fn):
            d[fn.func_name] = fn

        @register
        def search(data):
            # proximity sensors
            sensors_left = sum(data[1][:4])
            sensors_right = sum(data[1][4:])

            sensors_back = data[1][0] + data[1][7]

            diff = sensors_right - sensors_left
            #left_speed = self.minmax((sensors_left + (sensors_right - sensors_left) * random.random()), -self.max_speed, self.max_speed)
            #right_speed = self.minmax((sensors_right + (sensors_left - sensors_right) * random.random()), -self.max_speed, self.max_speed)
            if diff < 0:
                left_speed = self.max_speed
                right_speed = self.max_speed * (1 + diff*2)
            else:
                left_speed = self.max_speed * (1 - diff*2)
                right_speed = self.max_speed
            if sensors_back < data[1][3] + data[1][4]:
                left_speed = self.max_speed
                right_speed = -self.max_speed

            return [left_speed, right_speed]

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
        if self.stagnation_check(data):
            behaviour = "stagnation"

        print behaviour
        return self.behaviours[behaviour](data)

    def minmax(self, data, min_value, max_value):
        return min(max(data,min_value),max_value)

    def retrieval_check(self, data):
        for prox in data[0]:
            light_is_near = False
            for light in data[1]:
                if light > self.retrieval_light_threshold:
                    light_is_near = True
            if prox > self.retrieval_threshold and light_is_near:
                return True
        return False

    def stagnation_check(self, data):
        if self.recovering: return True
        if self.last_data:
            print abs(self.last_data[0][0] - data[0][0])
            print abs(self.last_data[1][0] - data[1][0])
            print self.last_data == data
            if ( abs(self.last_data[0][0] - data[0][0]) < self.stagnation_threshold
              or abs(self.last_data[1][0] - data[1][0]) < self.stagnation_threshold
              or self.last_data == data ):
                self.counter += 1
                if self.counter > 100:
                    self.counter = 0
                    self.recovering = True
                    return True
        self.last_data = data
        return False
