import random

class Robot:
    def __init__(self):
        self.behaviours = self.get_behaviours()
        self.max_speed = 1.0
        self.weights = [[-1.0, -0.8],[-1.0, -0.8],[-0.4,  0.4],[ 0.0,  0.0],[ 0.0,  0.0],[ 0.4, -0.4],[-0.6, -0.8],[-0.6, -0.8]]
        self.offset = [0.5*self.max_speed, 0.5*self.max_speed]
        self.stagnation_threshold = 1.0
        self.push_threshold = 0.1

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
            sensors_left = sum(data[0][4:])
            sensors_right = sum(data[0][:4])
            left_speed = self.minmax(sensors_left + (sensors_right - sensors_left) * random.Random())
            right_speed = self.minmax(sensors_right + (sensors_left - sensors_right) * random.Random())

            if left_speed == right_speed && left_speed >= self.distance_threshold:
                right_speed = self.max_speed

            return [left_speed, right_speed]

        @register
        def retrieval(data):
            if (data[1][0],data[1][7]) < (self.push_threshold, self.push_threshold):
                return [self.max_speed, self.max_speed]
            else:
                # light sensors
                sensors_left = sum(data[1][4:])
                sensors_right = sum(data[1][:4])
                if (sensors_left - sensors_right) < 0:
                    return [self.max_speed * 0.7, self.max_speed * -0.3]
                else:
                    return [self.max_speed * -0.3, self.max_speed * 0.7]

        @register
        def stagnation(data):
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
                if self.last_data:
                    if ( abs(self.last_data[0][0] - self.data[0][0]) < self.stagnation_threshold
                      or abs(self.last_data[1][0] - self.data[1][0]) < self.stagnation_threshold
                      or self.last_data == self.data ):
                        if counter > 100:
                            counter = 0
                            self.recovering = True
                    else:
                        counter = 0
                    
            self.counter += 1
            self.last_data = data
            return (lw,rw)

        return d

    def update(self, data):
        # search, retrieval, stagnation
        behaviour = "search"

        if self.is_close_to_object(data[1]):
            behaviour = "retrieval"
        elif False:
            behaviour = "stagnation"

        return self.behaviours[behaviour](data)

    def minmax(data, min_value, max_value):
        return min(max(data,min_value),max_value)

    def is_close_to_object(self, data):
        for sensor in data:
            if sensor > self.push_threshold:
                return True
        return False
