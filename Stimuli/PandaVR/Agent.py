from direct.showbase.ShowBase import ShowBase
from Stimuli.PandaVR.Collision import Collision
from utils.Timer import *
from utils.helper_functions import *
from direct.interval.IntervalGlobal import *
from panda3d.core import Filename

class Agent(ShowBase):
    def __init__(self, base_class, cond):
        self.cond = cond
        self.env = base_class
        self.duration = self.cond['dur']
        self.name = "Obj%s-Task" % self.cond['id']

    def load(self, id):
        id = self.cond['id']
        self.timer.start()
        model_path = self.env.object_files[self.cond['id']]
        self.model = self.env.loader.loadModel(model_path)
        positioning = self.object_positioning()  
        self.model.reparentTo(self.env.render)
     
        # Create Collision Node that surrounds the object and set the object movement (360 rotation)
        if not self.cond['is_plane']:
            self.set_movement(positioning)
            Collision(self.env, self.model, False).make_object_collidable()

    def remove(self):
        self.model.removeNode()
     
    def object_positioning(self):
        self.model.setScale(self.cond['mag'])
        self.model.setHpr(self.cond['rot'], self.cond['tilt'], self.cond['yaw'])
        grounded_z = 0 - get_bounds(self.model)['z0'] #I do that so that the objects will always be right on top of the ground
        self.model.setPos(self.cond['pos_x'], self.cond['pos_y'], grounded_z)
        return self.model.getPos(), self.model.getHpr(), self.model.getScale()
            
    def set_movement(self, pos_info):
        start_hpr = pos_info[1]         
        hpr_interval1 = self.model.hprInterval(15, start_hpr + (360,0,0), start_hpr)
        Sequence(hpr_interval1).loop()
        

        

        

        
            
            
