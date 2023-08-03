from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3
from Stimuli.PandaVR.Collision import Collision

class Camera(ShowBase):
    def __init__(self, base_class):
        
        self.env = base_class
        self.fixed_z = 0.5
        
        self.ypothetiko_pontiki = NodePath("ypothetiko pontiki node") 
        self.ypothetiko_pontiki.setZ(self.fixed_z)
        self.ypothetiko_pontiki.reparentTo(self.env.render)
        self.env.camera.reparentTo(self.ypothetiko_pontiki)
        
        Collision(self.env, self.ypothetiko_pontiki, True, True).make_object_collidable()
        
        
        self.keyMap = {"w" : False, 
                       "s" : False, 
                       "a" : False, 
                       "d" : False, 
                       "arrow_right" : False, 
                       "arrow_left" : False,
                       "arrow_up" : False,
                       "arrow_down" : False}

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
        self.ypothetiko_pontiki.setR(0)
        self.ypothetiko_pontiki.setZ(self.fixed_z)
        return task.cont
    
