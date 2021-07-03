from core.Experiment import *
import os


@stimulus.schema
class StimCondition(dj.Manual):
    definition = """
    # This class handles the stimulus presentation use function overrides for each stimulus class
    stim_hash            : char(24)                     # unique stimulus condition hash  
    """

    class Trial(dj.Part):
        definition = """
        # Stimulus onset timestamps
        -> experiment.Trial
        time                 : int                          # start time from session start (ms)
        ---
        -> StimCondition
        period=NULL          : varchar(64)
        end_time=NULL        : int                          # end time from session start (ms)
        """


class Stimulus:
    """ This class handles the stimulus presentation use function overrides for each stimulus class """

    cond_tables, required_fields, default_key = [], [], dict()

    def init(self, exp):
        """store parent objects """
        self.logger = exp.logger
        self.exp = exp

    def setup(self):
        """setup stimulation for presentation before experiment starts"""
        pass

    def prepare(self, condition=False, stim_periods=''):
        """prepares stuff for presentation before trial starts"""
        pass

    def ready_stim(self):
        """Stim Cue for ready"""
        pass

    def reward_stim(self):
        """Stim Cue for reward"""
        pass

    def punish_stim(self):
        """Stim Cue for punishment"""
        pass

    def present(self):
        """trial presentation method"""
        pass

    def stop(self):
        """stop trial"""
        pass

    def exit(self):
        """exit stimulus stuff"""
        pass

    def set_intensity(self):
        intensity = self.logger.get(schema='experiment', table='SetupConfiguration.Screen')
        if self.logger.is_pi:
            cmd = 'echo %d > /sys/class/backlight/rpi_backlight/brightness' % intensity
            os.system(cmd)

    def make_conditions(self, conditions=[]):
        """generate and store stimulus condition hashes"""
        for cond in conditions:
            assert np.all([field in cond for field in self.required_fields])
            cond.update({**self.default_key, **cond})
        return self.exp.log_conditions(conditions, schema='stimulus', hsh='stim_hash',
                                       condition_tables=['StimCondition'] + self.cond_tables)

