from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3
from Stimuli.PandaVR.Collision import Collision
from Behaviors.DummyBall import DummyBall

class Camera(ShowBase):
    def __init__(self, base_class):
        
        self.env = base_class
        self.fixed_z = 0.5
        
        self.ypothetiko_pontiki = NodePath("ypothetiko pontiki node") 
        self.ypothetiko_pontiki.setZ(self.fixed_z)
        self.ypothetiko_pontiki.reparentTo(self.env.render)
        self.env.camera.reparentTo(self.ypothetiko_pontiki)
        
        Collision(self.env, self.ypothetiko_pontiki, True).make_object_collidable()     
        
        self.env.taskMgr.add(self.camera_control, "Camera control")
        self.env.taskMgr.add(self.keep_me_grounded, "Camera control")
    
    def camera_control(self, task):
        dt = globalClock.getDt()
        DummyBall().camera_positioning(self.ypothetiko_pontiki, dt)
        return task.cont
    
    def keep_me_grounded(self, task):
        self.ypothetiko_pontiki.setR(0)
        self.ypothetiko_pontiki.setZ(self.fixed_z)
        return task.cont
    
