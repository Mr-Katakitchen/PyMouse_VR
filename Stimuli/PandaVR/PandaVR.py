from core.Stimulus import *
import os
import time
import numpy as np
from direct.showbase.ShowBase import ShowBase
from direct.task import Task #it's being used
import panda3d.core as core
from utils.Timer import *
from utils.helper_functions import *
from Stimuli.PandaVR.Agent import Agent
from Stimuli.PandaVR.Camera import Camera
from Stimuli.PandaVR.Movie import Movie
from Stimuli.PandaVR.Collision import Collision
from Stimuli.PandaVR.Plane import Plane
# from PandaVR.pandaVR_helper_functions import *

   
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
    required_fields = ['obj_id', 'obj_dur']
    default_key = {'background_color': (0, 0, 0),
                   'ambient_color': (0.1, 0.1, 0.1, 1),
                   'light_idx': (1, 2),
                   'light_color': (np.array([0.7, 0.7, 0.7, 1]), np.array([0.2, 0.2, 0.2, 1])),
                   'light_dir': (np.array([0, -20, 0]), np.array([180, -20, 0])),
                   'obj_pos_x': 0,
                   'obj_pos_y': 0,
                   'obj_mag': .5,
                   'obj_rot': 0,
                   'obj_tilt': 0,
                   'obj_yaw': 0,
                   'obj_delay': 0}

    object_files = dict()
    objects = dict()
        
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
        else:
            self.fStartDirect = False
            self.windowType = 'onscreen'
            self.Fullscreen = False
            self.path = '\\Stimuli\\objects\\'  # default path to copy local stimuli
            self.movie_path = os.path.dirname(os.path.abspath(__file__)) + '/movies/'
        ShowBase.__init__(self, fStartDirect=self.fStartDirect, windowType=self.windowType)

    def setup(self):
        self.props = core.WindowProperties()
        # self.props.setSize(self.pipe.getDisplayWidth(), self.pipe.getDisplayHeight())
        # self.props.setFullscreen(self.Fullscreen)
        # self.props.setCursorHidden(True)
        # self.props.setUndecorated(True)
        self.win.requestProperties(self.props)
        self.graphicsEngine.openWindows()
        self.set_background_color(0, 0, 0)
        # self.disableMouse()
        self.isrunning = False
        self.movie_exists = False

        #info = self.pipe.getDisplayInformation()
        #print(info.getTotalDisplayModes())
        #print(info.getDisplayModeWidth(0), info.getDisplayModeHeight(0))
        #print(self.pipe.getDisplayWidth(), self.pipe.getDisplayHeight())

        # Create Ambient Light
        # self.ambientLight = core.AmbientLight('ambientLight')
        # self.ambientLightNP = self.render.attachNewNode(self.ambientLight)
        # self.render.setLight(self.ambientLightNP)
        # self.set_taskMgr()

    def prepare(self, curr_cond, stim_period=''):
        
        self.flag_no_stim = False
        if stim_period == '':
            self.curr_cond = curr_cond
        elif stim_period not in curr_cond:
            self.flag_no_stim = True
            return
        else: 
            self.curr_cond = curr_cond[stim_period]
        
        self.period = stim_period

        # Set Background Color
        self.background_color = self.curr_cond['background_color']
        self.set_background_color(*self.background_color)

        # Set Ambient Light
        self.ambientLight = core.AmbientLight('ambientLight')
        self.ambientLightNP = self.render.attachNewNode(self.ambientLight)
        self.render.setLight(self.ambientLightNP)
        self.ambientLight.setColor(self.curr_cond['ambient_color'])

        # Set Directional Light
        self.lights = dict()  
        self.lightsNP = dict()
        for idx, light_idx in enumerate(iterable(self.curr_cond['light_idx'])): #used to be enumerate(iterable())
            self.lights[idx] = core.DirectionalLight('directionalLight_%d' % idx)
            self.lightsNP[idx] = render.attachNewNode(self.lights[idx])
            render.setLight(self.lightsNP[idx])
            self.lights[idx].setColor(tuple(self.curr_cond['light_color'][idx]))
            self.lightsNP[idx].setHpr(*self.curr_cond['light_dir'][idx])
    
        #Load Environment Plane
        self.plane = Plane(self, get_cond(self.curr_cond, 'plane_'))
        self.plane_bound_coor = self.plane.get_plane_bounds()
    
        # Set Object tasks
        self.plane_has_been_set = False #So that objects will be placed after the environment plane has been set
        for idx, obj in enumerate(iterable(self.curr_cond['obj_id'])):
            self.objects[idx] = Agent(self, get_cond(self.curr_cond, 'obj_', idx), self.plane_bound_coor)

        # Set Movie
        if 'movie_name' in self.curr_cond:
            file_name = get_cond(self.curr_cond, 'movie_')['name']
            self.movie = Movie(self, file_name)
            self.movie_exists = True            
          
        # Set Collision Variables  
        self.cTrav = core.CollisionTraverser()
        self.pusher = core.CollisionHandlerPusher()
        self.pusher.setHorizontal(True)
        # self.cHandler = CollisionHandlerEvent()
        # self.cHandler.addInPattern('into-%in')
        # self.cHandler.addOutPattern('outof-%in')
        
        # Set Main Camera  
        Camera(self)
        
    def start(self):
        if self.flag_no_stim: return

        if not self.isrunning:
            self.timer.start()
            self.isrunning = True
    
        self.log_start()
        if self.movie_exists: self.movie.play()
        for idx, obj in enumerate(iterable(self.curr_cond['obj_id'])):
            self.objects[idx].load() #loads the models with the Agent class
        self.flip(2)

    def present(self):
        self.flip()
        if 'obj_dur' in self.curr_cond and self.curr_cond['obj_dur'] < self.timer.elapsed_time():
            self.isrunning = False

    def flip(self, n=1):
        for i in range(0, n):
            self.taskMgr.step()

    def stop(self):
        if self.flag_no_stim: return
        for idx, obj in self.objects.items():
            obj.remove(obj.task)
        for idx, light in self.lights.items():
            self.render.clearLight(self.lightsNP[idx])
        if self.movie_exists:
            self.mov_texture.stop()
            self.movie_node.removeNode()
            self.movie_exists = False
        self.render.clearLight

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
        self.unshow(self.monitor["start_color"])

    def unshow(self, color=None):
        if not color: color = self.monitor['background_color']
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
                print(obj_id)
                object_info = (Objects() & ('obj_id=%d' % obj_id)).fetch1()
                filename = self.path + object_info['file_name']
                self.object_files[obj_id] = filename
                if not os.path.isfile(filename): print('Saving %s' % filename); object_info['object'].tofile(filename)
        return conditions

    def get_clip_info(self, key, *fields):
        return self.logger.get(schema='stimulus', table='Movie.Clip', key=key, fields=fields)

    def set_taskMgr(self):
        """
        Use this at the setup of pandas because for some reason the taskMgr the first time it 
        doesn't work properly. It needs time sleep between steps or to run many steps
        """
        self.set_background_color((0,0,0))
        for i in range(0, 2):
            time.sleep(0.1)
            self.taskMgr.step()



        

        

    

        

            
