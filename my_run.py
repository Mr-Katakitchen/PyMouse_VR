from PandaVR.Panda import *

prepare_dict = {
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



new = Panda()

new.object_files = {
                'plane': "models/plane/plane",
                'obj0': "models/ladybug/ladybug",
                'obj1': "models/bird1/bird1"
                # 'obj0_anim': {"models/bird"}
                }

new.init()
new.setup()
new.prepare(prepare_dict)
new.start()
new.run()