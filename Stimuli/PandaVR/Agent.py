from direct.showbase.ShowBase import ShowBase
from Stimuli.PandaVR.Collision import Collision
from utils.Timer import *
from utils.helper_functions import *
from direct.interval.IntervalGlobal import *
from panda3d.core import Filename

class Agent(ShowBase):
    def __init__(self, base_class, cond, plane_bounds):
        self.cond = cond
        self.env = base_class
        self.point = plane_bounds
        self.timer = Timer()
        self.duration = self.cond['dur']
        # hfov = self.env.camLens.get_fov() * np.pi / 180 # half field of view in radians
        # define object time parameters
        # self.rot_fun = self.time_fun(self.cond['rot'])
        # self.tilt_fun = self.time_fun(self.cond['tilt'])
        # self.yaw_fun = self.time_fun(self.cond['yaw'])
        # z_loc = 2
        # self.x_fun = self.time_fun(self.cond['pos_x'], lambda x, t: np.arctan(x * hfov[0]) * z_loc)
        # self.y_fun = self.time_fun(self.cond['pos_y'], lambda x, t: np.arctan(x * hfov[0]) * z_loc)
        # self.scale_fun = self.time_fun(self.cond['mag'], lambda x, t: .15*x)
        # add task object
        self.name = "Obj%s-Task" % self.cond['id']

    def load(self):
        self.timer.start()
        model_path = self.env.object_files[self.cond['id']]
        model_path = Filename.fromOsSpecific(model_path).getFullpath()
        self.model = self.env.loader.loadModel(model_path)
        
        positioning = self.object_positioning()
        
        self.model.reparentTo(self.env.render)
        # self.task = self.env.taskMgr.doMethodLater(self.cond['delay']/1000, self.objTask, self.name)
 
        self.set_movement(positioning)
        
        # Create Collision Node that surrounds the object
        Collision(self.env, self.model, False).make_object_collidable()
        
    # def objTask(self, task):
    #     t = self.timer.elapsed_time()/1000
    #     print(t)
    #     if t > self.duration/1000:
    #         self.remove()
    #         return        
    #     # self.model.setHpr(self.rot_fun(t), self.tilt_fun(t), self.yaw_fun(t))
    #     # self.model.setPos(self.x_fun(t), 2, self.y_fun(t))
    #     # self.model.setScale(self.scale_fun(t))
    #     return Task.cont

    def remove(self):
        self.model.removeNode()

    # def time_fun(self, param, fun=lambda x, t: x):
    #     param = (iterable(param))
    #     idx = np.linspace(0, self.duration/1000, param.size)
    #     return lambda t: np.interp(t, idx, fun(param, t))
     
    def object_positioning(self):
        self.model.setScale(self.cond['mag'])
        self.model.setHpr(self.cond['rot'], self.cond['tilt'], self.cond['yaw'])
        grounded_z = 0 - get_bounds(self.model)['z0'] #I do that so that the objects will be right on top of the ground
        self.model.setPos(self.cond['pos_x'], self.cond['pos_y'], grounded_z)
        return self.model.getPos(), self.model.getHpr(), self.model.getScale()
            
    def set_movement(self, pos_info):
        
        start_hpr = pos_info[1]         
        hpr_interval1 = self.model.hprInterval(15, start_hpr + (360,0,0), start_hpr)
        Sequence(hpr_interval1).loop()
        

        

        

        
            
            
