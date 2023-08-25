import math
from core.Interface import *
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *

class DummyBall(Interface, ShowBase):
    speed, update_location, prev_loc_x, prev_loc_y, loc_x, loc_y, theta, xmx, ymx = 0, True, 0, 0, 0, 0, 0, 1, 1
    # keyMap is a dictionnary that changes dynamically after key presses, to update the status of each key (pressed or not). 
    # The camera_positioning method looks here to move mouse according to key presses
    keyMap = {
                "a" : False, 
                "d" : False, 
                "arrow_right" : False, 
                "arrow_left" : False,
                "arrow_up" : False,
                "arrow_down" : False,
                "space" : False
                }
    mouse_is_moving = False 
    mouse_moving_speed = 1
    
    current_position = [] # x, y, theta 
    timestamp = 0
    movement_log = []
    time_log = []
     
    def __init__(self, **kwargs):
        Interface.__init__(self, **kwargs)
        self.setPosition()
      
        # ShowBase.accept(key action, method that gets called, parameters passed to the method (in a list))      
        self.accept("arrow_right", self.setKey, ["arrow_right", True]) 
        self.accept("arrow_left", self.setKey, ["arrow_left", True])
        self.accept("arrow_up", self.setKey, ["arrow_up", True])
        self.accept("arrow_down", self.setKey, ["arrow_down", True])

        self.accept("arrow_right-up", self.setKey, ["arrow_right", False])
        self.accept("arrow_left-up", self.setKey, ["arrow_left", False])
        self.accept("arrow_up-up", self.setKey, ["arrow_up", False])
        self.accept("arrow_down-up", self.setKey, ["arrow_down", False])
        
        self.accept("space", self.in_position, ["proximity_true"])
        self.accept("space-up", self.in_position, ["proximity_false"])
        self.accept("d", self.in_position, ["right_port"])
        self.accept("a", self.in_position, ["left_port"])  
    
    def setPosition(self, x0=0, y0=0, theta0=0):
        self.current_position = [x0, y0, theta0]
        
    def getPosition(self):
        return *self.current_position, self.timestamp

    def getSpeed(self):
        if self.mouse_is_moving: 
            speed = self.mouse_moving_speed 
        else:
            speed = 0
        return speed

    def cleanup(self):
        try:
            self.thread_end.set()
            self.mouse1.close()
            self.mouse2.close()
        except:
            print('ball not running')
            
    def setKey(self, key, value):
        self.keyMap[key] = value # keyMap dictionnary gets updated after each key action (pressing or lifting)
        if key == "arrow_up" or key == "arrow_down":
            if value == True:
                self.mouse_is_moving = True # Up or Down button has just been pressed, mouse is moving
            else:
                self.mouse_is_moving = False # Up or Down button has just been lifted, mouse is not moving
        
    def camera_positioning(self, camera_node, timestamp, adj, real):
        """Positions the camera and updates the current_position variable, that Behavior gets from Interface

        Args:
            camera_node (panda_object): the empty node that has the main camera attached to it
            timestamp (int?): what gets returned from timer.elapsed_time()
            adj (method): method that multiplies value by ball_to_panda_scale
            real (method): inverted adj
        """
        virtual_speed = adj(self.mouse_moving_speed) # Speed adjusted to ball_to_panda_scale
        turning_speed = 110.0 # Speed with wich the mouse rotates. Isn't relevant to scale
        turning_co = 0.5 if self.mouse_is_moving else 1 # So that movement is more natural.
        
        # Checks key status (pressed or not pressed) from keyMap dictionnary
        dt = globalClock.getDt() # Time since the last frame was drawn in the active ShowBase window 
        if self.keyMap["arrow_up"]:
            camera_node.setY(camera_node, 1 * virtual_speed * dt) # node.setY(node, dy) : newY = oldY + dy
        if self.keyMap["arrow_down"]:
            camera_node.setY(camera_node, -1 * virtual_speed * dt) 
        if self.keyMap["arrow_left"]:
            camera_node.setH(camera_node, turning_co * turning_speed * dt) 
        if self.keyMap["arrow_right"]:
            camera_node.setH(camera_node, -1 * turning_co * turning_speed * dt) 
        
        # After that, the positions get rescaled to the ball scaling to get passed to Behavior and to the database
        real_x = real(camera_node.getX()) 
        real_y = real(camera_node.getY())                                 
        self.current_position = [real_x, real_y, math.radians(camera_node.getH())]  
        self.timestamp = timestamp   
         
    def load_calibration(self):
        pass

    def calc_pulse_dur(self, reward_amount):
        actual_rew = dict()
        for port in self.rew_ports:
            actual_rew[port] = reward_amount
        return actual_rew

    def cleanup(self):
        self.set_running_state(False)
    
    def off_proximity(self):
        return self.position.type != 'Proximity'
        
    def set_ready_to_false(self):
        self.ready = False  #gets called when new trial starts, so that spacebar-activation resets
        
    def _proximity_change(self, event, port):
        if event == 'proximity_true' and not self.ready and not self.mouse_is_moving:
            self.timer_ready.start() 
            self.ready = True
            port =3  
            self.position = self.ports[Port(type='Proximity', port=port) == self.ports][0]
            self.position_tmst = self.beh.log_activity({**self.position.__dict__, 'in_position': self.ready})
            print('in position')
        elif event == 'proximity_false' and self.ready:
            self.ready = False
            port = 0
            tmst = self.beh.log_activity({**self.position.__dict__, 'in_position': self.ready})
            self.position_dur = tmst - self.position_tmst
            self.position = Port()
            print('off position')
            # print(pygame.mouse.get_pos())
            
    def in_position(self, event):
        self.__get_events(event)
        position_dur = self.timer_ready.elapsed_time() if self.ready else self.position_dur
        return self.position, position_dur, self.position_tmst
    
    def __get_events(self, event):
        port = 0
        # events = pygame.event.get() if pygame.get_init() else []

        # Check if any port is licked
        port = self._port_activated(event, port)
        # Check position
        port = self._proximity_change(event,port)

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     print(pygame.mouse.get_pos())
        # elif event.type == pygame.QUIT:
        #     self.logger.update_setup_info({'status': 'stop'})
        
    def _port_activated(self, event, port):
        if event == 'left_port' and not self.mouse_is_moving:
            print('Probe 1 activated!')
            port = 1
        if event == 'right_port' and not self.mouse_is_moving:
            print('Probe 2 activated!')
            port = 2
        if port:
            self.position=self.ports[Port(type='Lick', port=port) == self.ports][0]
            self.resp_tmst = self.logger.logger_timer.elapsed_time()
            self.beh.log_activity(self.position.__dict__)
        return port
    

