from utils.Timer import *
from StateMachine import *


class State(StateClass):
    def __init__(self, parent=None):
        self.timer = Timer()
        if parent:
            self.__dict__.update(parent.__dict__)

    def setup(self, logger, BehaviorClass, StimulusClass, session_params, conditions):
        self.logger = logger
        self.logger.log_session(session_params, '2AFC')
        # Initialize params & Behavior/Stimulus objects
        self.beh = BehaviorClass(self.logger, session_params)
        self.stim = StimulusClass(self.logger, session_params, conditions, self.beh)
        self.params = session_params
        self.logger.log_conditions(conditions, self.stim.get_condition_tables())
        exitState = Exit(self)
        self.StateMachine = StateMachine(Prepare(self), exitState)

        # Initialize states
        global states
        states = {
            'PreTrial'     : PreTrial(self),
            'Trial'        : Trial(self),
            'InterTrial'   : InterTrial(self),
            'Exit'         : exitState}

    def entry(self):  # updates stateMachine from Database entry - override for timing critical transitions
        self.StateMachine.status = self.logger.get_setup_info('status')
        self.logger.update_state(self.__class__.__name__)

    def run(self):
        self.StateMachine.run()


class Prepare(State):
    def run(self):
        self.stim.setup() # prepare stimulus

    def next(self):
        return states['PreTrial']


class PreTrial(State):
    def entry(self):
        self.stim.prepare()
        self.logger.update_state(self.__class__.__name__)

    def run(self): pass

    def next(self):
        if self.stim.curr_cond: # if run out of conditions exit
            return states['Trial']
        else:
            return states['Exit']


class Trial(State):
    def entry(self):
        self.logger.update_state(self.__class__.__name__)
        self.stim.init()
        self.timer.start()  # trial start counter
        self.logger.init_trial(self.stim.curr_cond['cond_hash'])

    def run(self):
        self.stim.present()  # Start Stimulus

    def next(self):
        if not self.stim.isrunning:     # timed out
            return states['InterTrial']
        else:
            return states['Trial']

    def exit(self):
        self.logger.log_trial()
        self.logger.ping()


class InterTrial(State):
    def entry(self):
        self.timer.start()

    def run(self):
        pass

    def next(self):
        if self.logger.get_setup_info('status') == 'stop':
            return states['Exit']
        elif self.timer.elapsed_time() >= self.stim.curr_cond['intertrial_duration']:
            return states['PreTrial']
        else:
            return states['InterTrial']

class Exit(State):
    def run(self):
        self.logger.update_setup_status('stop')
        self.beh.cleanup()
        self.stim.close()
