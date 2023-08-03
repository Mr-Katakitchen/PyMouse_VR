from Experiments.Navigate import *
from Behaviors.DummyBall import *
from Stimuli.PandaVR.PandaVR import *


# define session parameters
session_params = {
    'trial_selection'        : 'staircase',
    'staircase_window'       : 10,
    'noresponse_intertrial'  : True,
    'max_reward'             : 2000,
    'bias_window'            : 5,
    'stair_up'               : 0.8,
    'stair_down'             : 0.5,
    'setup_conf_idx'         : 0,
}


exp = Experiment()
exp.setup(logger, DummyBall, session_params)
conditions = []

non_resp = .1
scale = 2   #has to change every time the environment size changes - depending on the space the radii change
radius = 2**.5*(scale/2) - non_resp

def_key = {
        'x_sz'                  : scale,
        'y_sz'                  : scale,
        'trial_duration'        : 60000,
        'response_loc_x'        : (0, scale, scale, 0),
        'response_loc_y'        : (0, 0, scale, scale),
        'odor_x'                : (0, scale, scale, 0),
        'odor_y'                : (0, 0, scale, scale),
        'delivery_port'         : (1, 2, 4, 3),
        'x0'                    : -1,
        'y0'                    : -1,
        'theta0'                : 0,
        'reward_loc_x'          : -1,
        'reward_loc_y'          : -1,
        'extiction_factor'      : 3,
        'radius'                : radius - 1,
        'reward_amount'         : 12,
        'odorant_id'            : (1, 2, 4, 3),
    }

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

conditions += exp.make_conditions(stim_class=Panda(), conditions={**def_key,
                              'difficulty'         : 0,
                              'trial_duration'     : 8000,
                              'x_sz'               : scale*10,
                              'y_sz'               : scale*10,
                              'reward_loc_x'       : scale/2*10,
                              'reward_loc_y'       : scale*24.85,
                              'response_loc_x'     : (scale/2*10,),
                              'response_loc_y'     : (-scale/2*29.15,),
                              'extiction_factor'   : 300,
                              'radius'             : radius*30,
                              'reward_amount'      : 10,
                              'intertrial_duration': [800, 1000, 800, 1000],
                	          'x0'                 : (scale/2)*10,
                        	  'y0'                 : (scale/2)*10+.18,
                           
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
                'plane_yaw': 0
                                })



# run experiments
exp.push_conditions(conditions)
exp.start()
