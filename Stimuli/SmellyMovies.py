from Stimuli.Movies import *


class SmellyMovies(RPMovies):
    """ This class handles the presentation of Visual (movies) and Olfactory (odors) stimuli"""

    def get_cond_tables(self):
        return super().get_cond_tables()+['Olfactory', 'Olfactory.Channel']

    def start(self):
        delivery_port = self.curr_cond['delivery_port']
        odor_id = self.curr_cond['odor_id']
        odor_dur = self.curr_cond['odor_duration']
        odor_dutycycle = self.curr_cond['dutycycle']
        super().start()
        self.interface.give_odor(delivery_port, odor_id, odor_dur, odor_dutycycle)
        self.logger.log('StimOnset')
        self.timer.start()
