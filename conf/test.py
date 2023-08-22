# print("this one")
from Experiments.Navigate import *
from Behaviors.VRBall import *
from Stimuli.PandaVR import *


# define session parameters
session_params = {
    'trial_selection'        : 'staircase',
    'staircase_window'       : 10,
    'noresponse_intertrial'  : True,
    'max_reward'             : 2000,
    'bias_window'            : 5,
    'stair_up'               : 0.8,
    'stair_down'             : 0.5,
    'setup_conf_idx'         : 3,
}


exp = Experiment()
exp.setup(logger, VRBall, session_params)
conditions = []

non_resp = .1
scale = 2   #has to change every time the environment size changes - depending on the space the radii change
radius = 2**.5*(scale/2) - non_resp #peripou riza 2

def_key = {
        'x_sz'                  : 18.8,
        'y_sz'                  : 18.8,
        'trial_duration'        : 6000000,
        'response_loc_x'        : (-15, 15),
        'response_loc_y'        : (-15, 15),
        'x0'                    : 0,
        'y0'                    : 0,
        'theta0'                : 90,
        'reward_loc_x'          : -1,
        'reward_loc_y'          : -1,
        'extiction_factor'      : 3,
        'radius'                : 20,
        'reward_amount'         : 12,
    }

conditions += exp.make_conditions(stim_class=Panda(), conditions={**def_key,

                'background_color': (0/255, 0/255, 0/255),
                'ambient_color': (0.1, 0.1, 0.1, 1),
                # 'light_idx': (1, 2, 3),
                'light_color': (np.array([0.8, 0.8, 0.8, 1]), np.array([0.2, 0.2, 0.2, 1]), np.array([1, 1, 1, 1])),
                'light_dir': (np.array([0, -20, 0]), np.array([180, -20, 0]), np.array([0, -90, 0])),
                 'obj_id': (5, 6, 9),
                'obj_pos_x': (-15, 15, 0), 'obj_pos_y': (-15, 15, 0), 'obj_pos_z': 0,
                'obj_mag': (0.2, 0.2, 1), 
                'obj_rot': 0, 'obj_tilt': 0, 'obj_yaw': 0,
                'obj_dur': 1,
                'obj_delay': 0,
                'obj_is_plane' : (False, False, True),
                'movie_id' : 0,
                'plane_id': 0,
                'plane_pos_x': 0,
                'plane_pos_y': 0,
                'plane_pos_z': 0,
                'plane_mag': 1,
                'plane_rot': 0,
                'plane_tilt': 0,
                'plane_yaw': 0,
                'fr_movie_name' : 'MadMax'
                                })

Panda.object_files['plane'] = "models/plane/plane"
# run experiments
exp.push_conditions(conditions)
exp.start()
