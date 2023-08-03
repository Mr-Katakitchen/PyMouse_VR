from core.Behavior import *
from Interfaces.Ball import *


# @behavior.schema
class DummyBall(Behavior, dj.Manual):
    definition = """
    # This class handles the behavior variables for RP
    ->BehCondition
    ---
    x_sz                 : float
    y_sz                 : float
    x0                   : float
    y0                   : float            
    theta0               : float
    radius               : float
    speed_thr            : float # in m/sec
    """

    class Response(dj.Part):
        definition = """
        # Lick response condition
        -> VRBall
        response_loc_y            : float            # response y location
        response_loc_x            : float            # response x location
        response_port             : tinyint          # response port id
        """

    class Reward(dj.Part):
        definition = """
        # reward port conditions
        -> VRBall
        ---
        reward_loc_x              : float
        reward_loc_y              : float
        reward_port               : tinyint          # reward port id
        reward_amount=0           : float            # reward amount
        reward_type               : varchar(16)      # reward type
        """

    cond_tables = ['VRBall', 'VRBall.Response', 'VRBall.Reward']
    required_fields = ['x0', 'y0', 'radius', 'response_loc_y', 'response_loc_x',
                       'reward_loc_x', 'reward_loc_y', 'reward_amount']
    default_key = {'reward_type': 'water', 'speed_thr': 0.025,
                   'response_port': 1, 'reward_port': 1, 'theta0': 0}

    def __init__(self):
        self.env = 0

    def setup(self, exp):
        self.previous_loc = [0, 0]
        self.curr_loc = [0, 0]
        super(DummyBall, self).setup(exp)
        #self.vr = Ball(exp)

    def prepare(self, condition):
        self.in_position_flag = False
        if condition['x0'] < 0 or condition['y0'] < 0:
            x0, y0, theta0, time = self.vr.getPosition()
            self.setPosition(condition['x_sz'], condition['y_sz'], x0, y0, theta0)
        else:
            self.setPosition(condition['x_sz'], condition['y_sz'], condition['x0'], condition['y0'],
                                condition['theta0'])
        super().prepare(condition)
        
    def setPosition(self, xmx=1, ymx=1, x0=0, y0=0, theta0=0):
        self.loc_x = x0
        self.loc_y = y0
        self.theta = theta0
        self.xmx = xmx
        self.ymx = ymx
        
    def getPosition(self):
        return self.loc_x, self.loc_y, self.theta,  self.timestamp

    def getSpeed(self):
        return self.speed

    def cleanup(self):
        try:
            self.thread_end.set()
            self.mouse1.close()
            self.mouse2.close()
        except:
            print('ball not running')

    def is_ready(self):
        x, y, theta, tmst = self.get_position()
        in_position = False
        for r_x, r_y in zip(self.curr_cond['response_loc_x'], self.curr_cond['response_loc_y']):
            in_position = in_position or np.sum((np.array([r_x, r_y]) - [x, y]) ** 2) ** .5 < self.curr_cond['radius']
        return in_position

    def is_running(self):
        return self.vr.getSpeed() > self.curr_cond['speed_thr']

    def is_in_correct_loc(self):
        x, y, theta, tmst = self.get_position()
        if self.curr_cond['reward_loc_x'] < 0 or self.curr_cond['reward_loc_y'] < 0: # cor location is any other
            resp_locs = np.array([self.curr_cond['response_loc_x'], self.curr_cond['response_loc_y']]).T
            cor_locs = resp_locs[[np.any(loc != self.previous_loc) for loc in resp_locs]]
        else:
            cor_locs = [np.array([self.curr_cond['reward_loc_x'], self.curr_cond['reward_loc_y']])]
        dist_to_loc = [np.sum((loc - np.array([x, y])) ** 2) ** .5 for loc in cor_locs]
        is_cor_loc = np.array(dist_to_loc) < self.curr_cond['radius']
        in_position = np.any(is_cor_loc)
        self.curr_loc = cor_locs[np.argmin(dist_to_loc)]
        return in_position

    def get_position(self):
        return self.vr.getPosition()

    def reward(self):
        self.interface.give_liquid(self.response.port)
        self.log_reward(self.reward_amount[self.response.port])
        self.update_history(self.response.port, self.reward_amount[self.response.port])
        self.previous_loc = self.curr_loc

    def punish(self):
        self.update_history(self.response.port, punish=True)

    def exit(self):
        super().exit()
        self.vr.cleanup()
        self.interface.cleanup()
        
        
    def key_mapping(self):
        self.keyMap = {"w" : False, 
                       "s" : False, 
                       "a" : False, 
                       "d" : False, 
                       "arrow_right" : False, 
                       "arrow_left" : False,
                       "arrow_up" : False,
                       "arrow_down" : False}

        self.env.accept("w", self.setKey, ["w", True])
        self.env.accept("s", self.setKey, ["s", True])	
        self.env.accept("a", self.setKey, ["a", True])	
        self.env.accept("d", self.setKey, ["d", True])
        self.env.accept("arrow_right", self.setKey, ["arrow_right", True])
        self.env.accept("arrow_left", self.setKey, ["arrow_left", True])
        self.env.accept("arrow_up", self.setKey, ["arrow_up", True])
        self.env.accept("arrow_down", self.setKey, ["arrow_down", True])


        self.env.accept("w-up", self.setKey, ["w", False])
        self.env.accept("s-up", self.setKey, ["s", False])
        self.env.accept("a-up", self.setKey, ["a", False])
        self.env.accept("d-up", self.setKey, ["d", False])
        self.env.accept("arrow_right-up", self.setKey, ["arrow_right", False])
        self.env.accept("arrow_left-up", self.setKey, ["arrow_left", False])
        self.env.accept("arrow_up-up", self.setKey, ["arrow_up", False])
        self.env.accept("arrow_down-up", self.setKey, ["arrow_down", False])
        
        self.env.taskMgr.add(self.camera_control, "Camera control")
        self.env.taskMgr.add(self.keep_me_grounded, "Keep z position at level")
        
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def camera_control(self, task):
        dt = globalClock.getDt()
        # if(dt > .02):
        #     return task.cont
            
        moving_speed = 15.0
         
        move_direction = Vec3(0)
        if self.keyMap["w"]:
            move_direction += Vec3(0, 1, 0)  # Move forward
        if self.keyMap["s"]:
            move_direction += Vec3(0, -1, 0)  # Move backward
        if self.keyMap["a"]:
            move_direction += Vec3(-1, 0, 0)  # Move left
        if self.keyMap["d"]:
            move_direction += Vec3(1, 0, 0)  # Move right
            
        if move_direction.length() > 0:
            move_direction.normalize()
            
        self.ypothetiko_pontiki.setPos(self.ypothetiko_pontiki, move_direction * moving_speed * dt)  
            
        if(self.keyMap["arrow_right"] == True):
            self.ypothetiko_pontiki.setH(self.ypothetiko_pontiki, -70 * dt)
        if(self.keyMap["arrow_left"] == True):
            self.ypothetiko_pontiki.setH(self.ypothetiko_pontiki, 70 * dt)
        if(self.keyMap["arrow_up"] == True):
            self.ypothetiko_pontiki.setP(self.ypothetiko_pontiki, 10 * dt)
        if(self.keyMap["arrow_down"] == True):
            self.ypothetiko_pontiki.setP(self.ypothetiko_pontiki, -10 * dt)
    
        return task.cont
    
    def keep_me_grounded(self, task):
        self.env.ypothetiko_pontiki.setR(0)
        self.env.ypothetiko_pontiki.setZ(0)
        return task.cont
        
        
    
        

    

