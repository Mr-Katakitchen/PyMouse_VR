import math
import os

import numpy as np
import panda3d.core as core
from direct.interval.IntervalGlobal import *
from direct.showbase.ShowBase import ShowBase

from core.Stimulus import *
from utils.helper_functions import *
from utils.Timer import *


@stimulus.schema
class Objects(dj.Lookup):
    
    # definition = """
    # # object information
    # obj_id               : int                          # object ID
    # ---
    # description          : varchar(256)                 # description
    # object=null          : longblob                     # 3d file
    # file_name=null       : varchar(255)   
    # """

    def store(self, obj_id, file_name, description=''):
        tuple = dict(obj_id=obj_id, description=description,
                     object=np.fromfile(file_name, dtype=np.int8), file_name=file_name)
        self.insert1(tuple, replace=True)


@stimulus.schema
class Panda(Stimulus, dj.Manual):
    # definition = """
    # # This class handles the presentation of Objects with Panda3D
    # -> StimCondition
    # """

    class Object(dj.Part):
        pass
        # definition = """
        # # object conditions
        # -> Panda
        # -> Objects
        # ---
        # obj_pos_x             : blob
        # obj_pos_y             : blob
        # obj_mag               : blob
        # obj_rot               : blob
        # obj_tilt              : blob 
        # obj_yaw               : blob
        # obj_delay             : int
        # obj_dur               : int
        # """

    class Environment(dj.Part):
        pass
        # definition = """
        # # object conditions
        # -> Panda
        # ---
        # background_color      : tinyblob
        # ambient_color         : tinyblob
        # """

    class Movie(dj.Part):
        pass
        # definition = """
        # # object conditions
        # -> Panda
        # ---
        # movie_name            : char(8)                      # short movie title
        # clip_number           : int                          # clip index
        # """

    class Light(dj.Part):
        pass
        # definition = """
        # # object conditions
        # -> Panda
        # light_idx             : tinyint
        # ---
        # light_color           : tinyblob
        # light_dir             : tinyblob
        # """

    cond_tables = ['Panda', 'Panda.Object', 'Panda.Environment', 'Panda.Light', 'Panda.Movie']
    # required_fields = ['obj_id', 'obj_dur']
    default_key = {'background_color'       : (0, 0, 0),
                   'ambient_color'          : (0.1, 0.1, 0.1, 1),
                   'light_idx'              : (1, 2),
                   'light_color'            : (np.array([0.7, 0.7, 0.7, 1]), np.array([0.2, 0.2, 0.2, 1])),
                   'light_dir'              : (np.array([0, -20, 0]), np.array([180, -20, 0])),
                    }

    object_files = dict()
    objects = dict()
    state_color = {
        'ready_color': (0, 0, 255),
        'start_color': (255, 255, 0),
        'reward_color': (0, 255, 0),
        'punish_color': (255, 0, 0)
    }
    dummy_test, ball_test = False, False # Is it a ball experiment or a dummy test on pc? 
    mouse_height = 0.05 # Z position of camera that corresponds to mouse height (about 5 cms)
    co = 15 # ball_to_panda_scale
        
    def init(self, exp):

        super().init(exp)
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__ + "ShowBase", (cls, ShowBase), {})
        if self.logger.is_pi:
            self.fStartDirect = True
            self.windowType = None
            self.Fullscreen = True
            self.path = os.path.dirname(os.path.abspath(__file__)) + '/objects/'  # default path to copy local stimuli
            self.movie_path = os.path.dirname(os.path.abspath(__file__)) + '/movies/'
            self.ball_test = True
        else:
            self.fStartDirect = False
            self.windowType = 'onscreen'
            self.Fullscreen = False
            self.path = os.path.dirname(os.path.abspath(__file__)) + '/objects/'  # default path to copy local stimuli
            self.movie_path = os.path.dirname(os.path.abspath(__file__)) + '/movies/'
            self.dummy_test = True
        ShowBase.__init__(self, fStartDirect=self.fStartDirect, windowType=self.windowType)
        
        self.accept('escape', self.close_window) # ekso sto onoma tou ihsou xristou

    def setup(self):
        self.props = core.WindowProperties()
        if self.ball_test: 
            self.props.setSize(self.pipe.getDisplayWidth(), self.pipe.getDisplayHeight())
            self.props.setFullscreen(self.Fullscreen)
            self.props.setCursorHidden(True)
            self.props.setUndecorated(True)
            self.graphicsEngine.openWindows()
            self.disableMouse()
        elif self.dummy_test: #Did this to make it easier to move the window around when testing with Dummy_Ball
            self.props.setSize(1500, 900)
        self.win.requestProperties(self.props)
        self.isrunning = False
        self.movie_exists = False

        # Set Ambient Light    
        self.ambientLight = core.AmbientLight('ambientLight')
        self.ambientLightNP = self.render.attachNewNode(self.ambientLight)
        self.render.setLight(self.ambientLightNP)

    def prepare(self, cond, stim_period=''):
                
        self.flag_no_stim = False
        if stim_period == '':
            self.curr_cond = cond
        elif stim_period not in cond:
            self.flag_no_stim = True
            return
        else: 
            self.curr_cond = cond[stim_period]
        
        self.period = stim_period

        # Set Background Color
        self.background_color = cond['background_color']
        self.set_background_color(*self.background_color)

        # Set Ambient Light
        self.ambientLight.setColor(cond['ambient_color'])

        # Set Directional Light
        self.lights = dict()  
        self.lightsNP = dict()
        for idx, light_idx in enumerate(iterable(cond['light_idx'])): 
            self.lights[idx] = core.DirectionalLight('directionalLight_%d' % idx)
            self.lightsNP[idx] = render.attachNewNode(self.lights[idx])
            render.setLight(self.lightsNP[idx])
            self.lights[idx].setColor(tuple(cond['light_color'][idx]))
            self.lightsNP[idx].setHpr(*cond['light_dir'][idx])      

        # Set Movie
        if 'movie_name' in cond:
            self.movie = True
            loader = Loader(self)
            file_name = self.get_clip_info(cond, 'file_name')
            self.mov_texture = loader.loadTexture(self.movie_path + file_name[0])
            cm = core.CardMaker("card")
            tx_scale = self.mov_texture.getTexScale()
            cm.setFrame(-1, 1, -tx_scale[1]/tx_scale[0], tx_scale[1]/tx_scale[0])
            self.movie_node = core.NodePath(cm.generate())
            self.movie_node.setTexture(self.mov_texture, 1)
            self.movie_node.setPos(0, 100, 0)
            self.movie_node.setTexScale(core.TextureStage.getDefault(), self.mov_texture.getTexScale())
            self.movie_node.setScale(48)
            self.movie_node.reparentTo(self.render)  
            
        # Set Collision Variables   
        self.cTrav = core.CollisionTraverser() # This is the variable that handles all collision methods
        self.pusher = core.CollisionHandlerPusher() #This is a collision method 
        # Makes objects bump into things and get pushed around like in the real world
        # It is to be set for every object. However, I only set it for the camera_node, because this way only the camera_node
        # get pushed around during collisions. The other objects stay still.  
        self.pusher.setHorizontal(True)      
          
        #Set Camera
        # I set an empty node to move around and I attach the main camera to it. Seemed like the most practical solution
        self.camera_node = core.NodePath("camera_node") 
        self.z0 = self.adj(self.mouse_height) # adjusted value : real value * panda_to_ball_scale
        self.camera_node.setPos(0, 0, self.z0) 
        if 'x0' in cond:
            self.camera_node.setX(self.adj(cond['x0']))
        if 'y0' in cond:
            self.camera_node.setY(self.adj(cond['y0']))
        if 'theta0' in cond:
            self.camera_node.setH(math.degrees(cond['theta0'])) # rads to degrees
        # Render is the parent node of the environemnt of the current ShowBase window. Other nodes must be attached to it
        # Then stuff like lights, models and collision objects get attached to nodes. This is useful for arranging things in the environment
        self.camera_node.reparentTo(render) 
        camera.reparentTo(self.camera_node)
        taskMgr.add(self.camera_control, "Camera control") # Camera movement
        taskMgr.add(self.keep_me_grounded, "Stay on the ground") # This is to keep the z_position of the camera stable
        taskMgr.add(self.keep_within_limits, "Keep within limits") # To prevent camera from jumping over wall
        # Further explanation of tasks at the method definition
        self.set_collision_sphere(self.camera_node, is_camera = True)     
        
        self.center_of_env = core.NodePath("0,0,0") 
        # Is used so that the collision walls of the plane will be set relative to the (0,0,0) spot
        self.set_walls() # Sets walls that correspond to the (xmx, ymx) coordinates 
        
        
                     
    def start(self):
        if self.flag_no_stim: return
        if not self.isrunning:
            self.timer.start()
            self.isrunning = True
        self.log_start()
        if self.movie_exists: self.movie.play()
        
        #Set Plane
        plane_cond = self.get_cond('plane_', self.curr_cond['plane_id']) #Made slight changes to the make_conditions method
        self.plane = self.plane_load(plane_cond) #this function returns a panda3d model        
        
        # Set Objects
        for idx, obj in enumerate(iterable(self.curr_cond['obj_id'])):
            obj_cond = self.get_cond('obj_', idx)
            self.objects[idx] = self.object_load(obj_cond) #this function returns a panda3d model          
        self.flip(2)

    def present(self):
        self.flip()
        if 'obj_dur' in self.curr_cond and self.curr_cond['obj_dur'] < self.timer.elapsed_time():
            self.isrunning = False

    def flip(self, n=1):
        for i in range(0, n):
            taskMgr.step()

    def stop(self):
        if self.flag_no_stim: return    
        if self.dummy_test:
            # This exists so that space-up (lifting of spacebar) from dummy_ball doesn't activate after trial has ended and new trial has started. 
            # Is probably unecessary if proximity isn't relevant and spacebar isn't needed
            self.exp.beh.vr.set_ready_to_false() 
        
        for idx, obj in self.objects.items():
            obj.removeNode()
        taskMgr.remove("Camera control")
        taskMgr.remove("Stay on the ground") 
        taskMgr.remove("Keep within limits")
        self.camera_node.removeNode()  
        self.plane.removeNode()  
        self.center_of_env.removeNode() # Is removed so that the collision walls attached to it are also removed
        for idx, light in self.lights.items():
            self.render.clearLight(self.lightsNP[idx])        
        if self.movie_exists:
            self.mov_texture.stop()
            self.movie_node.removeNode()
            self.movie_exists = False       
       
        self.flip(2) # clear double buffer
        self.log_stop()
        self.isrunning = False

    def punish_stim(self):
        self.unshow(self.state_color['punish_color']) #self.monitor wasn't recognized on rpi

    def reward_stim(self):
        self.unshow(self.state_color['reward_color'])
    
    def ready_stim(self):
        self.unshow(self.state_color['ready_color'])

    def start_stim(self):
        self.unshow(self.state_color['start_color'])

    def unshow(self, color=None):
        if not color: color = self.state_color['ready_color']
        self.set_background_color(*color)
        self.flip(2)

    def close(self):
        pass

    def exit(self):
        self.destroy()

    def make_conditions(self, conditions):
        conditions = super().make_conditions(conditions)
        # store local copy of files
        if not os.path.isdir(self.path):  # create path if necessary
            os.makedirs(self.path)
        for cond in conditions:
            if 'movie_name' in cond:
                file = self.exp.logger.get(schema='stimulus', table='Movie.Clip', key=cond, fields=('file_name',))
                filename = self.movie_path + file[0]
                if not os.path.isfile(filename):
                    print('Saving %s' % filename)
                    clip = self.exp.logger.get(schema='stimulus', table='Movie.Clip', key=cond, fields=('clip',))
                    clip[0].tofile(filename)
            if not 'obj_id' in cond: continue
            for obj_id in iterable(cond['obj_id']):
                object_info = (Objects() & ('obj_id=%d' % obj_id)).fetch1()
                filename = self.path + object_info['file_name']
                self.object_files[obj_id] = filename
                if not os.path.isfile(filename): 
                    print('Saving %s' % filename)
                    object_info['object'].tofile(filename)
            if 'plane_id' in cond:                                      # MY ADDITION
                obj_id = cond['plane_id']
                object_info = (Objects() & ('obj_id=%d' % obj_id)).fetch1()
                filename = self.path + object_info['file_name']
                self.object_files[obj_id] = filename
                if not os.path.isfile(filename): 
                    print('Saving %s' % filename)
                    object_info['object'].tofile(filename)
        return conditions

    def get_clip_info(self, key, *fields):
        return self.logger.get(schema='stimulus', table='Movie.Clip', key=key, fields=fields)
    
    def plane_load(self, cond):
        """_summary_
        Loads plane model to variable, sets scale and position, creates walls 

        Args:
            cond (dict): The condition dictionnary created by make_conditions, for all the keys starting with 'plane_' from curr_cond dict()

        Returns:
            panda_object: the panda_object for the plane model
        """
        model_path = self.object_files[cond['id']]
        if self.dummy_test:
            model_path = core.Filename.fromOsSpecific(model_path).getFullpath() #Windows reads file paths differently
        plane = loader.loadModel(model_path)    
          
        bounds = self.get_bounds(plane) 
        x_scale =  cond['x'] / (bounds['x1'] - bounds['x0']) # Even though x0 is always 0
        plane.setSx(self.adj(x_scale))
        y_scale =  cond['y'] / (bounds['y1'] - bounds['y0']) # Even though y0 is always 0
        plane.setSy(self.adj(y_scale)) 
        
        # Places the plane to be around the movement area (xmx, ymx) of the mouse. 
        plane.setPos(self.adj(self.curr_cond['xmx']/2), self.adj(self.curr_cond['ymx']/2), 0) 
        
        plane.reparentTo(render)  
        return plane
    
    def object_load(self, cond): 
        """Loads object, set scale and position, set movement

        Args:
            cond (dict): The condition dictionnary created by make_conditions, for each id in ['obj_id] tuple.
            Contains value for each key starting with 'obj_'

        Returns:
            panda_object: the panda_object for the object models
        """
        model_path = self.object_files[cond['id']]
        if self.dummy_test:
            model_path = core.Filename.fromOsSpecific(model_path).getFullpath() #Windows reads file paths differently
        model = loader.loadModel(model_path)  
        
        start_hpr = model.getHpr()  
        # Interval("duration_of_movement", end_position, start_position) is a single movement, can be positional or rotational 
        hpr_interval1 = model.hprInterval(self.curr_cond['rot_duration'], start_hpr + (360,0,0), start_hpr) 
        # Sequence creates a sequence of intervals. Can support complex movement. Check documentation for more (it's easy)
        Sequence(hpr_interval1).loop() 
        
        model.setScale(self.adj(cond['mag'])) # Must be set before grounded_z is defined
        # grounded_z : So that objects are always right on top of a ground, even if panda_object's z_position was initially != 0
        grounded_z = 0 - self.get_bounds(model)['z0'] 
        model.setPos(self.adj(cond['pos_x']), self.adj(cond['pos_y']), grounded_z)
        model.setHpr(cond['rot'], cond['tilt'], cond['yaw']) # Starting hpr values
        
        self.set_collision_sphere(model) # creates collision sphere that surrounds the object
        
        model.reparentTo(render)  
        return model      
        
    def camera_control(self, task):
        """Camera control
        It might be better if it changed, so thbat only the parameters get passed from the Interface and the camera_node positioning happens
        here, in Stimulus. So far, the Interface.camera_positioning method takes the whole Panda class as a parameter. 

        Args:
            task (Task): This parameter is needed for the function to act as a Panda3d Task

        Returns:
            task.cont: Withour returning task.cont, the task will only be executed once
        """        
        
        timestamp = self.timer.elapsed_time()  
        self.exp.beh.vr.camera_positioning(self.camera_node, timestamp, self.adj, self.real) # Method of Interface class of Behavior class of Experiment class of Stimuli class that's parent of current Panda class
        # print(self.camera_node.getPos())
        return task.cont
    
    def keep_me_grounded(self, task):
        """Keeps mouse z_position stable
        
        Is necessary because during collision, due to the pusher function, camera_node might also get pushed up or down
        """
        self.camera_node.setZ(self.z0)
        return task.cont   
    
    def keep_within_limits(self, task): 
        """Doesn't let the mouse get out of (0,xmx), (0,ymx)
        
        Might not be needed. Is used to solve the problem of mouse jumping over collision wall
        it happens if the dx from the ball is bigger than the ball width, for example after some very fast movesment
        """
        x, y = self.adj(self.curr_cond['xmx']), self.adj(self.curr_cond['ymx'])
        if self.camera_node.getX() > x:
            self.camera_node.setX(x)
        if self.camera_node.getX() < 0:
            self.camera_node.setX(0)
        if self.camera_node.getY() > y:
            self.camera_node.setY(y)
        if self.camera_node.getY() < 0:
            self.camera_node.setY(0)
        return task.cont 
    
    def set_collision_sphere(self, model, is_camera = False):
        """Creates collision sphere that surrounds the object

        Args:
            model (panda_object): panda_object for model
            is_camera (bool, optional): If model is the camera_node, is set to True. Defaults to False.
        """
        if is_camera:
            radius = self.z0 # default mouse height
        else:
            # These functions throw an error if called on camera_node, because it's an empty_node and has no dimensions
            bounds = model.getChild(0).getBounds()
            radius = bounds.getRadius() 
                     
        sphere = core.CollisionNode("collision node to contain the sphere") # Special type of node that can contain collision objects
        sphere.addSolid(core.CollisionSphere((0,0,0), radius)) # Adds a collision object in the shape of a sphere to the above node
        sphere_node = model.attachNewNode(sphere) # I'm not sure exactly what type of node is this. It's needed to add the collision node to the environment
        if self.dummy_test: sphere_node.show() 
        
        if is_camera:
            self.pusher.addCollider(sphere_node, self.camera_node) # Pusher method is only set for the camera_node
            self.cTrav.addCollider(sphere_node, self.pusher) # Collision method of camera_node is added to collision handler function
        
    def set_walls(self):
        """Sets walls
        """
        box = core.CollisionNode("collision node to contain the walls") 
        x = self.adj(self.curr_cond['xmx'])
        y = self.adj(self.curr_cond['ymx'])
        d = self.z0 
        # d is used to slightly move the walls, because by default they will be centered to the defined positions and will 
        # occupy some space inside the predefined (0,xmx), (0,ymx) area, due to their width
        width, height = d, d # they're set relative to the mouse size (d = self.z0 = mouse_height)
        box.addSolid(core.CollisionBox((-2*d, y/2, 0), width, y/2 + d, height))
        box.addSolid(core.CollisionBox((x + 2*d, y/2, 0), width, y/2 + d, height))
        box.addSolid(core.CollisionBox((x/2, -2*d, 0), x/2 + d, width, height))
        box.addSolid(core.CollisionBox((x/2, y + 2*d, 0), x/2 + d, width, height))
        self.center_of_env.setPos(0, 0, 0)
        self.center_of_env.reparentTo(render) 
        box_node = self.center_of_env.attachNewNode(box) # Walls are attached to an empty_node placed at the center of the env (0,0,0)
        if self.dummy_test: box_node.show()
        
    def adj(self, value): #adjusted
        """Multiplies values by a ball_to_panda_scale_coefficient so that they're closer to panda3d's default values. 
        Is useful for developping

        Args:
            value (int): Can be position or scale. Is in meters 
        """
        return value  * self.co
    
    def real(self, value): #real
        """Divides by the ball_to_panda_scale_coefficient to convert values back to meters (ball scale). Inverted adj

        Args:
            value (int): Position or scale
        """
        return value / self.co
    
    def get_bounds(self, model):  
        """Returns the physical bounds of the objects in space

        Args:
            model (plane_object): the object

        Returns:
            dict: x0 is where the object begins in the x axis, x1 where it ends. Same for y, z
        """
        bound_coordinates = dict()
        bound_coordinates['x0'] = model.getTightBounds()[0][0]
        bound_coordinates['y0'] = model.getTightBounds()[0][1]
        bound_coordinates['z0'] = model.getTightBounds()[0][2]
        bound_coordinates['x1'] = model.getTightBounds()[1][0]
        bound_coordinates['y1'] = model.getTightBounds()[1][1]
        bound_coordinates['z1'] = model.getTightBounds()[1][2]
        return bound_coordinates
    
    def get_cond(self, cond_name, idx=0): 
        """ Splits a dictionnary in multiple smaller dictionnaries
        
        This takes the self.curr_cond() dictionnary and finds all the keys whose name begines with "cond_name". 
        Then, it returns a new dictionnary that, for each key, only contains a single entry that corresponds to the 
        given idx.
        Idx comes from enumerating the number of elements in the curr_cond['cond_name_id'] tuple
        
        For example, the dictionnary [obj_id: (1,4,5), obj_pos: (0.5, 0.7, 1.2), obj_name: ("panda", "koala", "fortounis")]
        returns [obj_id: 1, obj_pos: 0.5, obj_name: "panda"] for idx = 1,
        [obj_id: 4, obj_pos: 0.7, obj_name: "koala"] for idx = 2, 
        [obj_id: 5, obj_pos: 1.2, obj_name: "fortounis"] for idx = 3

        Throws an error if not all the tuples of the "cond_name" keys have the same number of elements, 
        except for keys containing one element (e.g. obj_pos: 2) or a single element tuple (e.g. obj_pos: (2))

        Args:
            cond_name (string): The threshold for the key names. For example: obj_
            idx (int, optional): An element of the self.curr_cond['obj_id'] tuple. Defaults to 0.

        Returns:
            dict: A dictionnary for each of the values in the cond['obj_id'] tuple
        """
        return {k.split(cond_name, 1)[1]: v if type(v) is int or type(v) is float or type(v) is str else v[idx] #added string parameter
        for k, v in self.curr_cond.items() if k.startswith(cond_name)}
        
        
        
        
        

     





        

        

    

        

            
