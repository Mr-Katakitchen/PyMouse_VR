from direct.showbase.ShowBase import ShowBase
# from Stimuli.PandaVR.pandaVR_helper_functions import *
from utils.helper_functions import *
from Stimuli.PandaVR.Collision import Collision


class Plane(ShowBase):
    def __init__(self, base_class, cond):
        self.cond = cond
        self.env = base_class
        # add task object
        # self.name = "Obj%s-Task" % self.cond['id']
        self.load()

    def load(self):
        model_path = self.env.object_files['plane']
        self.model = self.env.loader.loadModel(model_path)
        
        self.plane_positioning()
        
        Collision(self.env, self.model, False).create_collision_walls(self.get_plane_bounds())
        # Collision(self.env, self.model, False, True).create_collision_floor(1)
        # Collision(self.env, self.model, False, True).create_collision_floor(0)
        self.model.reparentTo(self.env.render)
        
    def plane_positioning(self):
        self.model.setHpr(self.cond['rot'], self.cond['tilt'], self.cond['yaw'])
        self.model.setPos(self.cond['pos_x'], self.cond['pos_y'], self.cond['pos_z'])
        self.model.setScale(self.cond['mag'])   
        
    def get_plane_bounds(self):      
        plane_bound_coordinates = get_bounds(self.model)
        return plane_bound_coordinates

        
        
            
            
