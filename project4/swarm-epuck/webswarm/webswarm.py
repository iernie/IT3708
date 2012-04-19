# This uses the EpuckBasic code as the interface to webots, and the epuck2 code to connect an ANN
# to webots.
from __future__ import division
#import epuck2
import epuck_basic as epb
#import graph
import prims1
import imagepro
import robot


# The webann is a descendent of the webot "controller" class, and it has the ANN as an attribute.

class WebSwarm(epb.EpuckBasic):

    def __init__(self,
            tempo = 1.0,
            e_thresh = 125,
            nvect = True,
            cvect = True,
            svect = True,
            band = 'bw',
            concol = 1.0,
            snapshow = True,
            ann_cycles = 1,
            agent_cycles = 5,
            act_noise = 0.1,
            tfile = "redman4"):
        epb.EpuckBasic.__init__(self)
        self.basic_setup() # defined for EpuckBasic 
        self.robot = robot.Robot()
    
    def long_run(self,steps = 500):
        while True:
            #image = self.snapshot()

            proximities = [(x/4096) for x in self.get_proximities()]
            #print proximities

            lights = self.get_lights()
            data = (proximities,lights)
            #print lights

            speed = self.robot.update(data)

            self.set_wheel_speeds(speed[0], speed[1])
            self.run_timestep()

    

#*** MAIN ***
# Webots expects a controller to be created and activated at the bottom of the controller file.

controller = WebSwarm(tempo = 1.0, band = 'gray')
controller.long_run(40)
