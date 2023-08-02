from Experiments.Navigate import *
from Stimuli.Grating import *
from Behaviors.DummyBall import *
from Stimuli.PandaVR.Panda import *

# define session parameters
session_params = {
    'trial_selection'    : 'staircase',
    'max_reward'         : 3000,
    'bias_window'        : 5,
    'staircase_window'   : 10,
    'stair_up'           : 0.7,
    'stair_down'         : 0.6,
    'setup_conf_idx'     : 0,
}

default_key = {'background_color': (0, 0, 0),
                'ambient_color': (0.1, 0.1, 0.1, 1),
                'light_idx': (1, 2),
                'light_color': (np.array([0.7, 0.7, 0.7, 1]), np.array([0.2, 0.2, 0.2, 1])),
                'light_dir': (np.array([0, -20, 0]), np.array([180, -20, 0])),
                'pos_x': 0,
                'pos_y': 0,
                'mag': .5,
                'rot': 0,
                'tilt': 0,
                'yaw': 0,
                'dur': 5,
                'id' : 0}

exp = Experiment()
exp.setup(logger, DummyBall, session_params)

# define stimulus conditions
key = {
    'contrast'           : 100,
    'spatial_freq'       : .05,   # cycles/deg
    'square'             : 0,     # squarewave or Guassian
    'temporal_freq'      : 1,     # cycles/sec
    'flatness_correction': 1,     # adjustment of spatiotemporal frequencies based on animal distance
    'duration'           : 5000,
    'difficulty'         : 1,
    'timeout_duration'   : 4000,
    'trial_duration'     : 5000,
    'intertrial_duration': 1000,
    'init_duration'      : 100,
    'delay_duration'     : 2000,
    'reward_amount'      : 8
}

repeat_n = 1
conditions = []

ports = {1: 0,
         2: 90}

Grating_Stimuli = Grating() if session_params['setup_conf_idx'] ==0 else GratingRP()
for port in ports:
    conditions += exp.make_conditions(stim_class=Grating_Stimuli, conditions={**key,
                                                                              'theta'        : ports[port],
                                                                              'reward_port'  : port,
                                                                              'response_port': port})
panda_conditions = {
                'background_color': (0/255, 0/255, 0/255),
                'ambient_color': (0.1, 0.1, 0.1, 1),
                'light_idx': (1, 2, 3),
                'light_color': (np.array([0.8, 0.8, 0.8, 1]), np.array([0.8, 0.8, 0.8, 1]), np.array([1, 1, 1, 1])),
                'light_dir': (np.array([0, -20, 0]), np.array([180, -20, 0]), np.array([0, -90, 0])),
                'obj_id': [0, 1],
                'obj_pos_x': [-15, 15],
                'obj_pos_y': [15, -15],
                'obj_pos_z': [0, 0],
                'obj_mag': [2.5, 7],
                'obj_rot': [45, 45],
                'obj_tilt': [0, 0],
                'obj_yaw': [0, 0],
                'obj_dur': [10000, 10000],
                'obj_delay': [0, 1],
                'movie_id' : 0,
                'movie_name' : "Never on Sunday (1960) SDTV GreekDiamond XviD MP3.AVI",
                'plane_id': 0,
                'plane_pos_x': 0,
                'plane_pos_y': 0,
                'plane_pos_z': 0,
                'plane_mag': 4,
                'plane_rot': 0,
                'plane_tilt': 0,
                'plane_yaw': 0,
                }

conditions[0].update(panda_conditions)

# run experiments
exp.push_conditions(conditions)
print("\n ta xwnw \n")
exp.start()

