from core.Stimulus import *
import os
import math
import numpy as np
from direct.showbase.ShowBase import ShowBase
import panda3d.core as core
from utils.Timer import *
from utils.helper_functions import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
   
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
    # default_key = {'background_color': (0, 0, 0),
    #                'ambient_color': (0.1, 0.1, 0.1, 1),
    #                'light_idx': (1, 2),
    #                'light_color': (np.array([0.7, 0.7, 0.7, 1]), np.array([0.2, 0.2, 0.2, 1])),
    #                'light_dir': (np.array([0, -20, 0]), np.array([180, -20, 0])),
    #                'obj_pos_x': 0,
    #                'obj_pos_y': 0,
    #                'obj_mag': .5,
    #                'obj_rot': 0,
    #                'obj_tilt': 0,
    #                'obj_yaw': 0,
    #                'obj_delay': 0}

    object_files = dict()
    objects = dict()
    dummy_test, ball_test = False, False # Is it a ball experiment or a dummy test on pc? 
    z0 = 0.5 # This the camera z position, so that the mouse will be at eye-level with the other objects 
        
    def init(self, exp):
        super().init(exp)
        self.exp = exp
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
        elif self.dummy_test:
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
        self.cTrav = core.CollisionTraverser()
        self.pusher = core.CollisionHandlerPusher()
        self.pusher.setHorizontal(True)
        
        #Set Camera
        self.camera_node = core.NodePath("camera_node")
        self.camera_node.setPos(0,0,self.z0)
        if 'x0' in cond:
            self.camera_node.setX(cond['x0'])
        if 'y0' in cond:
            self.camera_node.setY(cond['y0'])
        if 'theta0' in cond:
            self.camera_node.setH(math.degrees(cond['theta0'])) # rads to degrees
        self.camera_node.reparentTo(render)
        camera.reparentTo(self.camera_node)
        taskMgr.add(self.camera_control, "Camera control")
        taskMgr.add(self.keep_me_grounded, "Stay on the ground")
        self.set_collision_sphere(self.camera_node, is_camera = True)
                     
    def start(self):
        if self.flag_no_stim: return
        if not self.isrunning:
            self.timer.start()
            self.isrunning = True
        self.log_start()
        if self.movie_exists: self.movie.play()
        
        # Set Objects
        for idx, obj in enumerate(iterable(self.curr_cond['obj_id'])):
            obj_cond = get_cond(self.curr_cond, 'obj_', idx)
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
        self.exp.beh.vr.set_ready_to_false() # This exists so that space-up doesn't activate after trial has ended. Is probably unecessary
        
        for idx, obj in self.objects.items():
            obj.removeNode()
        taskMgr.remove("Camera control")
        taskMgr.remove("Stay on the ground")
        self.camera_node.removeNode()     
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
        self.unshow(self.monitor['punish_color'])

    def reward_stim(self):
        self.unshow(self.monitor['reward_color'])
    
    def ready_stim(self):
        self.unshow(self.monitor['ready_color'])

    def start_stim(self):
        self.unshow(self.monitor['start_color'])

    def unshow(self, color=None):
        if not color: color = self.monitor['background_color']
        if self.dummy_test:
            self.monitor['ready_color'] = (0, 0, 255)
            self.monitor['start_color'] = (255, 255, 0)
            self.monitor['reward_color'] = (0, 255, 0)
            self.monitor['punish_color'] = (255, 0, 0)
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
        return conditions

    def get_clip_info(self, key, *fields):
        return self.logger.get(schema='stimulus', table='Movie.Clip', key=key, fields=fields)
    
    def object_load(self, cond): # cond = condition for current object id
        model_path = self.object_files[cond['id']]
        if self.dummy_test:
            model_path = core.Filename.fromOsSpecific(model_path).getFullpath() #Windows reads file paths differently
        model = loader.loadModel(model_path)
        if not cond['is_plane']:
            model.setScale(cond['mag'])
        else:
            self.set_plane_scale(model)
        model.setHpr(cond['rot'], cond['tilt'], cond['yaw'])
        grounded_z = 0 - get_bounds(model)['z0'] #I do that so that the objects will always be right on top of the ground
        model.setPos(cond['pos_x'], cond['pos_y'], grounded_z)
        model.reparentTo(render)     
        if not cond['is_plane']:
            start_hpr = model.getHpr()        
            hpr_interval1 = model.hprInterval(cond['rot_dur'], start_hpr + (360,0,0), start_hpr) #Set Interval for 360 rotation
            Sequence(hpr_interval1).loop()
            self.set_collision_sphere(model)        #Create Collision Node that surrounds the object
        # print("object id = ", cond['id'], "   ,", model.getScale().x, "    ,", model.getScale().y, "\n  bounds:   ", get_bounds(model))
        return model
        
    def camera_control(self, task):
        dt = globalClock.getDt()
        if self.ball_test:
            self.ball_to_panda_scale = self.curr_cond['ball_to_panda_speed_co']
            ball_pos = (self.exp.beh.get_position()[0] * self.ball_to_panda_scale, self.exp.beh.get_position()[1] * self.ball_to_panda_scale, self.z0) 
            ball_theta = math.degrees(self.exp.beh.get_position()[2]) # rads to degrees
            self.camera_node.setPos(ball_pos) 
            self.camera_node.setH(ball_theta)
        elif self.dummy_test:
            self.exp.beh.vr.camera_positioning(self.camera_node, dt)
        return task.cont
    
    def keep_me_grounded(self, task):
        self.camera_node.setR(0)
        self.camera_node.setZ(self.z0)
        return task.cont
    
    def keep_within_limits(self, task):
        pass
    
    def set_collision_sphere(self, model, is_camera = False):
        if is_camera:
            radius = 1
        else:
            bounds = model.getChild(0).getBounds()
            radius = bounds.getRadius() 
                     
        collision_object = core.CollisionNode("collision object")
        collision_object.addSolid(core.CollisionSphere((0,0,0), radius))
        collision_sphere = model.attachNewNode(collision_object)
        if self.dummy_test: collision_sphere.show()
        
        if is_camera:
            self.pusher.addCollider(collision_sphere, self.camera_node)
            self.cTrav.addCollider(collision_sphere, self.pusher) 
            
            
    def set_plane_scale(self, plane):
        # cond['mag'] (object size scale) is overwritten for the plane
        bounds = get_bounds(plane)
        x_scale =  2 * self.curr_cond['plane_x'] / (bounds['x1'] - bounds['x0']) 
        plane.setSx(x_scale)
        y_scale =  2 * self.curr_cond['plane_y'] / (bounds['x1'] - bounds['x0'])
        plane.setSy(y_scale)
        
        
        

     





        

        

    

        

            
