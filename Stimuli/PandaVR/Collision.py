from panda3d.core import CollisionSphere, CollisionNode, CollisionTube, CollisionPlane, Plane, Point3, Vec3, Vec4
from panda3d.core import LMatrix4f
from direct.showbase.ShowBase import ShowBase
from utils.helper_functions import *

class Collision(ShowBase):
    
    show = False
    
    def __init__(self, base_class, model, is_camera = False): 
        
        self.env = base_class
        self.model = model
        self.is_camera = is_camera
        if (is_camera == False):
            self.point = get_bounds(self.model)
            
    def create_collision_floor(self, z):
        planeSolid = Plane(Vec3(0, 0, 1), Point3(0, 0, z))
        planeSolid = CollisionPlane(planeSolid)
        planeNode = CollisionNode("floor")
        planeNode.addSolid(planeSolid)
        floor = self.env.render.attachNewNode(planeNode)
        if self.show: floor.show()
        
    def create_collision_walls(self, plane_boundries):
        wall_height = 3
        d = 0 #distance of the wall from the plane boundries
        self.point = plane_boundries
             
        wallSolid = CollisionTube(self.point['x0'] + d, d, 0, self.point['x1'] - d, d, 0, wall_height)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.env.render.attachNewNode(wallNode)
        wall.setY(self.point['y0'])
        if self.show: wall.show()

        wallSolid = CollisionTube(self.point['x0'] + d, -d, 0, self.point['x1'] - d, -d, 0, wall_height)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.env.render.attachNewNode(wallNode)
        wall.setY(self.point['y1'])
        if self.show: wall.show()
        
        wallSolid = CollisionTube(d, self.point['y0'] + d, 0, d, self.point['y1'] - d, 0, wall_height)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.env.render.attachNewNode(wallNode)
        wall.setX(self.point['x0'])
        if self.show: wall.show()

        wallSolid = CollisionTube(-d, self.point['y0'] + d, 0, -d, self.point['y1'] - d, 0, wall_height)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.env.render.attachNewNode(wallNode)
        wall.setX(self.point['x1'])
        if self.show: wall.show()
        
    def make_object_collidable(self):
        
        center = (0,0,0)
        if self.is_camera:
            radius = 0.2
        else:
            bounds = self.model.getChild(0).getBounds()
            center = bounds.getCenter()
            radius = bounds.getRadius() * 0.8       
          
        colliderNode = CollisionNode("collision object")
        colliderNode.addSolid(CollisionSphere(center, 2 * radius))
        collider = self.model.attachNewNode(colliderNode)
        if self.show: collider.show()
        
        if (self.is_camera):
            self.env.pusher.addCollider(collider, self.model)
            self.env.cTrav.addCollider(collider, self.env.pusher)  
            # self.accept("into-collision object", self.handle_collision)
            # self.accept("outo-collision object", self.handle_collision) 
             
    # Handler Function that could possibly replace the default Pusher handler   
    def handle_collision(self, collEntry):
        print(self.model)
        print("μπουπ")
        cur_pos = self.model.getPos()
        self.model.setPos(cur_pos) #stay in place
        