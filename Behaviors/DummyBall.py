from core.Behavior import *
from Interfaces.Ball import *
from panda3d.core import Vec3
from direct.showbase.ShowBase import ShowBase

# @behavior.schema
class DummyBall(Behavior, ShowBase, dj.Manual):
    update_location = True
    current_position = []
    keyMap = {"w" : False, 
                "s" : False, 
                "a" : False, 
                "d" : False, 
                "arrow_right" : False, 
                "arrow_left" : False,
                "arrow_up" : False,
                "arrow_down" : False}

    
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
        self.accept("w", self.setKey, ["w", True])
        self.accept("s", self.setKey, ["s", True])	
        self.accept("a", self.setKey, ["a", True])	
        self.accept("d", self.setKey, ["d", True])
        self.accept("arrow_right", self.setKey, ["arrow_right", True])
        self.accept("arrow_left", self.setKey, ["arrow_left", True])
        self.accept("arrow_up", self.setKey, ["arrow_up", True])
        self.accept("arrow_down", self.setKey, ["arrow_down", True])

        self.accept("w-up", self.setKey, ["w", False])
        self.accept("s-up", self.setKey, ["s", False])
        self.accept("a-up", self.setKey, ["a", False])
        self.accept("d-up", self.setKey, ["d", False])
        self.accept("arrow_right-up", self.setKey, ["arrow_right", False])
        self.accept("arrow_left-up", self.setKey, ["arrow_left", False])
        self.accept("arrow_up-up", self.setKey, ["arrow_up", False])
        self.accept("arrow_down-up", self.setKey, ["arrow_down", False])
    
    def setup(self, exp):
        self.previous_loc = [0, 0]
        self.curr_loc = [0, 0]
        super(DummyBall, self).setup(exp)
        #self.vr = Ball(exp)

    def prepare(self, condition):
        self.in_position_flag = False
        if condition['x0'] < 0 or condition['y0'] < 0:
            x0, y0  = self.getPosition()
            self.setPosition(x0, y0)
        else:
            self.setPosition(condition['x0'], condition['y0'])
        self.current_position = [condition['x0'], condition['y0']]
        super().prepare(condition)
        
    def setPosition(self, x0=0, y0=0):
        self.current_position = [x0, y0]
        
    def getPosition(self):
        return self.current_position[0], self.current_position[1]

    def getSpeed(self):
        return 0

    def is_ready(self):
        x, y = self.getPosition()
        in_position = False
        for r_x, r_y in zip(self.curr_cond['response_loc_x'], self.curr_cond['response_loc_y']):
            in_position = in_position or np.sum((np.array([r_x, r_y]) - [x, y]) ** 2) ** .5 < self.curr_cond['radius']
        return in_position

    def is_running(self):
        return self.getSpeed() > self.curr_cond['speed_thr']

    def is_in_correct_loc(self):
        x, y = self.getPosition()
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


    def reward(self):
        self.interface.give_liquid(self.response.port)
        self.log_reward(self.reward_amount[self.response.port])
        self.update_history(self.response.port, self.reward_amount[self.response.port])
        self.previous_loc = self.curr_loc

    def punish(self):
        self.update_history(self.response.port, punish=True)

    def exit(self):
        super().exit()   
        return self.current_position[0], self.current_position[1]
        
    

        
        
    
        

    

