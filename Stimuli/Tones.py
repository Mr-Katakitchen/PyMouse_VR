from Stimuli.RPScreen import *


@stimulus.schema
class Tones(RPScreen, dj.Manual):
    definition = """
    # This class handles the presentation of Odors
    -> StimCondition
    ---
    tone_duration             : int                     # tone duration (ms)
    tone_frequency            : int                     # tone frequency (hz)
    tone_volume               : int                     # tone volume (percent)
    tone_pulse_freq           : float                   # frequency of tone pulses (hz)
    """

    cond_tables = ['Tones']
    required_fields = ['tone_duration', 'tone_frequency']
    default_key = {'tone_volume': 50, 'tone_pulse_freq': 0}
       
    def start(self):
        tone_frequency = self.curr_cond['tone_frequency']
        tone_volume = self.curr_cond['tone_volume']
        tone_pulse_freq=self.curr_cond['tone_pulse_freq']
        if 0< self.curr_cond['tone_pulse_freq']<10 :
            raise ValueError('Tone pulse frequency cannot be between zero and 10Hz (not including)')
        self.exp.interface.give_sound(tone_frequency, tone_volume, tone_pulse_freq)
        super().start()

    def present(self):
        if self.timer.elapsed_time() > self.curr_cond['tone_duration'] and self.isrunning:
            self.isrunning = False
            self.stop()

    def stop(self):
        self.log_stop()
        self.isrunning = False
        self.exp.interface.stop_sound()