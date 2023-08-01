from Experiments.Navigate import *
from Behaviors.VRBall import *
from Stimuli.PandaVR.Panda import *
from Interfaces.DummyBall import *

# define session parameters
session_params = {
    'trial_selection'        : 'random',
    'noresponse_intertrial'  : True,
    'setup_conf_idx'         : 0,
}

def setup_dummy(self, exp):
    self.previous_loc = [0, 0]
    self.curr_loc = [0, 0]
    super(VRBall, self).setup(exp)
    #self.vr = Dummy_all(exp)

VRBall.setup = setup_dummy

exp = Experiment()
exp.setup(logger, VRBall, session_params)
conditions = []

rew_locs = ([4, 4], [0, 4])
odors = ((1, 2, 3, 4), (1, 2, 4, 3))

# for idx, loc in enumerate(rew_locs):
#     conditions += exp.make_conditions(stim_class=Panda(), conditions={
#         'odorant_id'            : odors[idx],
#         'delivery_port'         : odors[idx],
#         'odor_x'                : (0, 5, 5, 0),
#         'odor_y'                : (0, 0, 5, 5),
#         'x_sz'                  : 5,
#         'y_sz'                  : 5,
#         'trial_duration'        : 300000,
#         'theta0'                : 0,
#         'x0'                    : 2.5,
#         'y0'                    : 2.5,
#         'reward_loc_x'          : loc[0],
#         'reward_loc_y'          : loc[1],
#         'response_loc_x'        : (0, 5, 5, 0),
#         'response_loc_y'        : (0, 0, 5, 5),
#         'fun'                   : 3,
#         'radius'                : 0.3,
#         'reward_amount'         : 10,
#     })

fake_conditions = {
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
                'movie_name' : "Prehistoric Park - S01E05 - The Bug House (DVD XviD MP3 PwN).avi",
                'plane_id': 0,
                'plane_pos_x': 0,
                'plane_pos_y': 0,
                'plane_pos_z': 0,
                'plane_mag': 10,
                'plane_rot': 0,
                'plane_tilt': 0,
                'plane_yaw': 0,
                }



new = Panda()

new.object_files = {
                'plane': "models/plane/plane",
                'obj0': "models/ladybug/ladybug",
                'obj1': "models/bird1/bird1"
                # 'obj0_anim': {"models/bird"}
                }

# new.init()
# new.setup()
# new.prepare(prepare_dict)
# new.start()
# new.run()

# run experiments
exp.push_conditions(fake_conditions)
exp.start()