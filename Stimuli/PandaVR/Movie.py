from direct.showbase.ShowBase import ShowBase
from direct.showbase.Loader import Loader
from panda3d.core import NodePath, CardMaker, TextureStage


class Movie(ShowBase):
    def __init__(self, base_class, movie_name):
        
        self.env = base_class
        self.sfxManagerList = self.env.sfxManagerList
        loader = Loader(self)
        # file_name = self.get_clip_info(self.curr_cond, 'file_name')
        # self.movie_path = "models/" #sad
        self.mov_texture = loader.loadTexture(self.movie_path + movie_name)
        self.mov_sound = loader.loadSfx(self.movie_path + movie_name)
        self.mov_sound.play()
        # self.mov_texture.synchronizeTo(self.mov_sound)
        cm = CardMaker("card")
        # tx_scale = self.mov_texture.getTexScale()
        cm.setFrame(-1.8, 1.8, -1, 1)
        self.movie_node = NodePath(cm.generate())
        self.movie_node.setTexture(self.mov_texture, 1)
        self.movie_node.setPos(0, 200, 30)
        self.movie_node.setTexScale(TextureStage.getDefault(), self.mov_texture.getTexScale())
        self.movie_node.setScale(30)
        self.movie_node.reparentTo(self.env.render)
        
    def play(self):
        self.mov_texture.play()