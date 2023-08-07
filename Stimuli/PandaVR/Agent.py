from direct.showbase.ShowBase import ShowBase
from Stimuli.PandaVR.Collision import Collision
from utils.Timer import *
from utils.helper_functions import *
import numpy as np
from direct.task import Task
from direct.interval.IntervalGlobal import *

class Agent(ShowBase):
    def __init__(self, base_class, cond, plane_bounds):
        self.cond = cond
        self.env = base_class
        self.point = plane_bounds
        self.timer = Timer()
        self.d = 10 #distance of objects from plane boundries
        self.duration = self.cond['dur']
        hfov = self.env.camLens.get_fov() * np.pi / 180 # half field of view in radians
        # define object time parameters
        self.rot_fun = self.time_fun(self.cond['rot'])
        self.tilt_fun = self.time_fun(self.cond['tilt'])
        self.yaw_fun = self.time_fun(self.cond['yaw'])
        z_loc = 2
        self.x_fun = self.time_fun(self.cond['pos_x'], lambda x, t: np.arctan(x * hfov[0]) * z_loc)
        self.y_fun = self.time_fun(self.cond['pos_y'], lambda x, t: np.arctan(x * hfov[0]) * z_loc)
        self.scale_fun = self.time_fun(self.cond['mag'], lambda x, t: .15*x)
        # add task object
        self.name = "Obj%s-Task" % self.cond['id']

    def load(self):
        self.timer.start()
        # model_path = self.env.object_files['obj' + str(self.cond['id'])]
        # self.model = self.env.loader.loadModel(model_path)
        self.model = self.env.loader.loadModel(self.env.object_files[self.cond['id']])
        
        positioning = self.object_positioning()
        
        self.model.reparentTo(self.env.render)
        self.task = self.env.taskMgr.doMethodLater(self.cond['delay']/1000, self.objTask, self.name)
        
        self.set_movement(positioning)
        
        # Create Collision Node that surrounds the object
        Collision(self.env, self.model, False).make_object_collidable()
        
        

    def objTask(self, task):
        t = self.timer.elapsed_time()/1000
        if t > self.duration/1000:
            self.remove(task)
            return
        
        # d = 10 #distance of objects from plane boundries
        # adjusted_z = self.cond['pos_z'] #Some models are a little higher or lower apo kataskeyis tous
        # if self.cond['id'] == 0:
        #     start_pos = (self.point['x0'] + d, self.point['y1'] - d, adjusted_z) #First object goes to the top left corner
        # elif self.cond['id'] == 1:
        #     start_pos = (self.point['x1'] - d, self.point['y0'] + d, adjusted_z) #Second goes to the bottom right
        
        self.model.setHpr(self.rot_fun(t), self.tilt_fun(t), self.yaw_fun(t))
        self.model.setPos(self.x_fun(t), 2, self.y_fun(t))
        self.model.setScale(self.scale_fun(t))

        return Task.cont

    def remove(self, task):
        task.remove()
        self.model.removeNode()

    def time_fun(self, param, fun=lambda x, t: x):
        param = (iterable(param))
        idx = np.linspace(0, self.duration/1000, param.size)
        return lambda t: np.interp(t, idx, fun(param, t))
     
        
    def object_positioning(self):
        
        self.model.setScale(self.cond['mag'] + 3)
        self.model.setHpr(self.cond['rot'], self.cond['tilt'], self.cond['yaw'])
        self.model.setPos(self.cond['pos_x'], self.cond['pos_y'], self.cond['pos_z'])
        d = self.d #distance of objects from plane boundries
        adjusted_z = self.cond['pos_z'] #Some models are a little higher or lower apo kataskeyis tous     
        grounded_z = 0 - get_bounds(self.model)['z0'] 
        print(grounded_z)
        if self.cond['id'] == 0:
            self.model.setPos(self.point['x0'] + d, self.point['y1'] - d, grounded_z) #First object goes to the top left corner
        elif self.cond['id'] == 1:
            self.model.setPos(self.point['x1'] - d, self.point['y0'] + d, grounded_z) #Second goes to the bottom right
        
        
        return self.model.getPos(), self.model.getHpr(), self.model.getScale()
            
    def set_movement(self, pos_info):
        
        start_pos = pos_info[0]
        start_hpr = pos_info[1]
        op = -1 if self.cond['id'] == 0 else 1
        dy = op * (self.point['y1'] - self.point['y0'] - 2 * self.d)
        dp = 360
         
        pos_interval1 = self.model.posInterval(15, start_pos + (0,dy,0), start_pos)
        hpr_interval1 = self.model.hprInterval(8, start_hpr + (dp,0,0), start_hpr)
        pos_interval2 = self.model.posInterval(10, start_pos, start_pos + (0,dy,0))
        hpr_interval2 = self.model.hprInterval(10, start_hpr, start_hpr + (dp,0,0))
        parallel1 = Parallel(pos_interval1, hpr_interval1, name="go")
        parallel2 = Parallel(pos_interval2, hpr_interval2, name="return")
        
        Sequence(
            # Wait(2.0),
            # parallel1,
            # Wait(2.0),
            # parallel2
            hpr_interval1
        ).loop()
        

        

        

        
            
            
