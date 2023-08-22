from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3
from Stimuli.PandaVR.Collision import Collision
import numpy as np

class Camera(ShowBase):
    
    interface = None
    fixed_z = 0.8
    fixed_R = 0
    
    def __init__(self, base_class):
        
        self.env = base_class
        self.alithino_pontiki = NodePath("camera_node") #self.env.loader.loadModel("models/Mouse/Mouse")
        self.alithino_pontiki.reparentTo(self.env.render)
        self.alithino_pontiki.setPos(self.env.curr_cond['x0'], self.env.curr_cond['y0'], 0)
        # self.alithino_pontiki.getChild(0).setScale(1)
        # self.alithino_pontiki.getChild(0).setP(20)
                                              
        Collision(self.env, self.alithino_pontiki, True).make_object_collidable()     
        
        self.env.taskMgr.add(self.camera_control, "Camera control")
        self.env.taskMgr.add(self.keep_me_grounded, "Stay on the ground")
    
    def camera_control(self, task):
        dt = globalClock.getDt()
        ball_pos = (self.env.exp.beh.get_position()[0] * 100, self.env.exp.beh.get_position()[1] * 100, 0)
        ball_theta = self.env.exp.beh.get_position()[2] * 360 / np.pi 
        self.alithino_pontiki.setPos(ball_pos) #self.env.exp.beh.vr.camera_positioning(self.alithino_pontiki, dt)
        self.alithino_pontiki.setH(ball_theta)
        print("position:  ",self.alithino_pontiki.getPos(), "   rotation:       ", self.alithino_pontiki.getHpr())
        self.env.camera.setPos(self.alithino_pontiki, 0, 0, 0.5)
        self.env.camera.setHpr(self.alithino_pontiki, 0, 0, 0)
        return task.cont
    
    def keep_me_grounded(self, task):
        self.alithino_pontiki.setR(self.fixed_R)
        self.alithino_pontiki.setZ(self.fixed_z)
        return task.cont
               
    def remove(self):
        self.env.taskMgr.remove("Camera control")        
        self.env.taskMgr.remove("Stay on the ground")        
        self.alithino_pontiki.removeNode()
        
    
    
