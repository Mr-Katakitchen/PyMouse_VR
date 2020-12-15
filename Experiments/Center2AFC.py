from utils.Timer import *
from StateMachine import *
from datetime import datetime, timedelta


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
        self.logger.log_conditions(conditions, self.stim.get_cond_tables() + self.beh.get_cond_tables())

        logger.update_setup_info('start_time', session_params['start_time'])
        logger.update_setup_info('stop_time', session_params['stop_time'])

        exitState = Exit(self)
        self.StateMachine = StateMachine(Prepare(self), exitState)

        # Initialize states
        global states
        states = {
            'PreTrial'     : PreTrial(self),
            'Trial'        : Trial(self),
            'Abort'        : Abort(self),
            'InterTrial'   : InterTrial(self),
            'Reward'       : Reward(self),
            'Punish'       : Punish(self),
            'Sleep'        : Sleep(self),
            'OffTime'      : OffTime(self),
            'Exit'         : exitState}

    def entry(self):  # updates stateMachine from Database entry - override for timing critical transitions
        self.StateMachine.status = self.logger.setup_status
        self.logger.update_setup_info('state', type(self).__name__)
        self.timer.start()

    def run(self):
        self.StateMachine.run()

    def is_sleep_time(self):
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0) + self.logger.get_setup_info('start_time')
        stop = now.replace(hour=0, minute=0, second=0) + self.logger.get_setup_info('stop_time')
        if stop < start:
            stop = stop + timedelta(days=1)
        time_restriction = now < start or now > stop
        return time_restriction


class Prepare(State):
    def run(self):
        self.stim.setup()  # prepare stimulus

    def next(self):
        if self.is_sleep_time():
            return states['Sleep']
        else:
            return states['PreTrial']


class PreTrial(State):
    def entry(self):
        self.stim.prepare()
        if not self.stim.curr_cond: self.logger.update_setup_info('status', 'stop', nowait=True)
        self.beh.prepare(self.stim.curr_cond)
        super().entry()

    def run(self): pass

    def next(self):
        if self.beh.is_ready(self.stim.curr_cond['init_duration']):
            return states['Trial']
        elif self.is_sleep_time():
            return states['Sleep']
        else:
            if self.timer.elapsed_time() > 5000: # occasionally get control status
                self.timer.start()
                self.StateMachine.status = self.logger.setup_status
                self.logger.ping()
            return states['PreTrial']


class Trial(State):
    def entry(self):
        self.resp_ready = False
        super().entry()
        self.stim.init()
        self.trial_start = self.logger.init_trial(self.stim.curr_cond['cond_hash'])

    def run(self):
        self.stim.present()  # Start Stimulus
        self.response = self.beh.response(self.trial_start)
        if self.beh.is_ready(self.stim.curr_cond['delay_duration'], self.trial_start):
            self.resp_ready = True

    def next(self):
        if not self.resp_ready and self.response:                           # did not wait
            return states['Abort']
        elif self.response and not self.beh.is_correct():  # response to incorrect probe
            return states['Punish']
        elif self.response and self.beh.is_correct():  # response to correct probe
            return states['Reward']
        elif self.timer.elapsed_time() > self.stim.curr_cond['trial_duration']:      # timed out
            return states['InterTrial']
        else:
            return states['Trial']

    def exit(self):
        self.logger.log_trial()
        self.stim.stop()  # stop stimulus when timeout
        self.logger.ping()


class Abort(State):
    def run(self):
        self.beh.update_history()
        self.logger.log_abort()

    def next(self):
        return states['InterTrial']


class Reward(State):
    def run(self):
        self.stim.reward_stim()
        self.beh.reward()

    def next(self):
        return states['InterTrial']


class Punish(State):
    def entry(self):
        self.beh.punish()
        super().entry()

    def run(self):
        self.stim.punish_stim()

    def next(self):
        if self.timer.elapsed_time() >= self.stim.curr_cond['timeout_duration']:
            return states['InterTrial']
        else:
            return states['Punish']

    def exit(self):
        self.stim.unshow()


class InterTrial(State):
    def run(self):
        if self.beh.response() & self.params.get('noresponse_intertrial'):
            self.timer.start()

    def next(self):
        if self.is_sleep_time():
            return states['Sleep']
        elif self.beh.is_hydrated():
            return states['OffTime']
        elif self.timer.elapsed_time() >= self.stim.curr_cond['intertrial_duration']:
            return states['PreTrial']
        else:
            return states['InterTrial']


class Sleep(State):
    def entry(self):
        self.logger.update_setup_info('state', type(self).__name__)
        self.logger.update_setup_info('status', 'sleeping')
        self.stim.unshow([0, 0, 0])

    def run(self):
        self.logger.ping()
        time.sleep(5)

    def next(self):
        if self.logger.setup_status == 'stop':  # if wake up then update session
            return states['Exit']
        elif self.logger.setup_status == 'wakeup' and not self.is_sleep_time():
            return states['PreTrial']
        elif self.logger.setup_status == 'sleeping' and not self.is_sleep_time():  # if wake up then update session
            return states['Exit']
        else:
            return states['Sleep']

    def exit(self):
        if not self.logger.setup_status == 'stop':
            self.logger.update_setup_info('status', 'running')


class OffTime(State):
    def entry(self):
        self.logger.update_setup_info('state', type(self).__name__)
        self.logger.update_setup_info('status', 'offtime')
        self.stim.unshow([0, 0, 0])

    def run(self):
        self.logger.ping()
        time.sleep(5)

    def next(self):
        if self.logger.setup_status == 'stop':  # if wake up then update session
            return states['Exit']
        elif self.is_sleep_time():
            return states['Sleep']
        else:
            return states['OffTime']


class Exit(State):
    def run(self):
        self.beh.cleanup()
        self.stim.close()
