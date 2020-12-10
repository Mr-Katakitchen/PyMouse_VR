from Probe import *
from utils.Timer import *
import pygame
import numpy as np


class Behavior:
    """ This class handles the behavior variables """
    def __init__(self, logger, params):
        self.params = params
        self.resp_timer = Timer()
        self.resp_timer.start()
        self.logger = logger
        self.rew_probe = 0
        self.probes = np.array(np.empty(0))
        self.probe_history = np.array([])  # History term for bias calculation
        self.reward_history = np.array([])  # History term for performance calculation
        self.licked_probe = 0
        self.reward_amount = dict()

    def setup(self):
        pass

    def is_licking(self, since=False):
        return 0

    def is_ready(self, init_duration, since=0):
        return True, 0

    def is_hydrated(self):
        rew = np.nansum(self.reward_history)
        if self.params['max_reward']:
            return rew >= self.params['max_reward']
        else:
            return False

    def reward(self):
        self.update_history(self.licked_probe, self.reward_amount[self.licked_probe])
        self.logger.log_liquid(self.licked_probe, self.reward_amount[self.licked_probe])
        print('Giving Water at probe:%1d' % self.licked_probe)

    def punish(self):
        if self.licked_probe > 0:
            probe = self.licked_probe
        else:
            probe = np.nan
        self.update_history(probe)

    def give_odor(self, delivery_idx, odor_idx, odor_dur, odor_dutycycle):
        print('Odor %1d presentation for %d' % (odor_idx, odor_dur))

    def inactivity_time(self):  # in minutes
        return 0

    def cleanup(self):
        pass

    def get_in_position(self):
        pass

    def get_off_position(self):
        pass

    def update_history(self, probe=np.nan, reward=np.nan):
        self.probe_history = np.append(self.probe_history, probe)
        self.reward_history = np.append(self.reward_history, reward)
        self.logger.update_total_liquid(np.nansum(self.reward_history))

    def prepare(self, condition):
        pass


class RPBehavior(Behavior):
    """ This class handles the behavior variables for RP """
    def __init__(self, logger, params):
        self.probe = RPProbe(logger)
        super(RPBehavior, self).__init__(logger, params)

    def setup(self):
        self.probe.setup()

    def is_licking(self, since=0):
        licked_probe, tmst = self.probe.get_last_lick()
        if tmst >= since and licked_probe:
            self.licked_probe = licked_probe
            self.resp_timer.start()
        else:
            self.licked_probe = 0
        return self.licked_probe

    def is_ready(self, duration, since=False):
        ready, ready_time, tmst = self.probe.in_position()
        if duration == 0:
            return True
        elif not since:
            return ready and ready_time > duration # in position for specified duration
        elif tmst >= since:
            return ready_time > duration  # has been in position for specified duration since timepoint
        else:
            return (ready_time + tmst - since) > duration  # has been in position for specified duration since timepoint

    def is_correct(self, condition):
        return np.any(np.equal(self.licked_probe, condition['probe']))

    def reward(self):
        self.update_history(self.licked_probe, self.reward_amount[self.licked_probe])
        self.probe.give_liquid(self.licked_probe)
        self.logger.log_liquid(self.licked_probe, self.reward_amount[self.licked_probe])

    def give_odor(self, delivery_port, odor_id, odor_dur, odor_dutycycle):
        self.probe.give_odor(delivery_port, odor_id, odor_dur, odor_dutycycle)
        self.logger.log_stim()

    def inactivity_time(self):  # in minutes
        return np.minimum(self.probe.timer_probe1.elapsed_time(),
                          self.probe.timer_probe2.elapsed_time()) / 1000 / 60

    def cleanup(self):
        self.probe.cleanup()

    def prepare(self, condition):
        self.reward_amount = self.probe.calc_pulse_dur(condition['reward_amount'])


class TouchBehavior(Behavior):
    def __init__(self, logger, params):
        from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE
        super(TouchBehavior, self).__init__(logger, params)
        self.screen_sz = np.array([800, 480])
        self.touch_area = 50  # +/- area in pixels that a touch can occur
        self.buttons = dict()
        self.buttons['any_loc'] = self.Button(self.screen_sz/2, 800)
        self.loc2px = lambda x: self.screen_sz/2 + x*self.screen_sz[0]
        self.px2loc = lambda x: x/self.screen_sz[0] - self.screen_sz/2
        self.probe = RPProbe(logger)
        self.ts = Touchscreen()
        for touch in self.ts.touches:
            touch.on_press = self._touch_handler
            touch.on_release = self._touch_handler

    def setup(self):
        self.ts.run()
        self.probe.setup()

    def is_licking(self, since=0):
        licked_probe, tmst = self.probe.get_last_lick()
        if tmst >= since and licked_probe:
            self.licked_probe = licked_probe
            self.resp_timer.start()
        else:
            self.licked_probe = 0
        return self.licked_probe

    def is_ready(self, duration, since=0):
        if duration == 0:
            return True
        else:
            return self.buttons['ready_loc'].tmst >= since

    def is_correct(self, condition):
        return np.any(np.equal(self.licked_probe, condition['probe']))

    def reward(self):
        self.update_history(self.licked_probe, self.reward_amount[self.licked_probe])
        self.probe.give_liquid(self.licked_probe)
        self.logger.log_liquid(self.licked_probe, self.reward_amount[self.licked_probe])

    def give_odor(self, delivery_port, odor_id, odor_dur, odor_dutycycle):
        self.probe.give_odor(delivery_port, odor_id, odor_dur, odor_dutycycle)
        self.logger.log_stim()

    def cleanup(self):
        self.probe.cleanup()
        self.ts.stop()

    def prepare(self, condition):
        self.reward_amount = self.probe.calc_pulse_dur(condition['reward_amount'])
        self.buttons['ready_loc'] = self.Button(self.loc2px(condition['ready_loc']))
        self.buttons['correct_loc'] = self.Button(self.loc2px(condition['correct_loc']))

    def _touch_handler(self, event, touch):
        if event == TS_PRESS:
            tmst = self.logger.log_touch(self.px2loc(touch))
            for button in self.buttons.keys():
                if self.buttons[button].is_pressed(touch):
                    self.buttons[button].tmst = tmst

    class Button:
        def __init__(self, loc=[0, 0], touch_area=50):
            self.loc = loc
            self.tmst = None
            self.touch_area = touch_area

        def is_pressed(self, touch):
            touch_x = self.loc[0] + self.touch_area > touch.x > self.loc[0] - self.touch_area
            touch_y = self.loc[1] + self.touch_area > touch.y > self.loc[1] - self.touch_area
            return touch_x and touch_y


class DummyProbe(Behavior):
    def __init__(self, logger, params):
        self.lick_timer = Timer()
        self.lick_timer.start()
        self.ready_timer = Timer()
        self.ready_timer.start()
        self.ready = False
        self.probe = 0
        pygame.init()
        super(DummyProbe, self).__init__(logger, params)

    def is_ready(self, init_duration, since=0):
        self.__get_events()
        elapsed_time = self.ready_timer.elapsed_time()
        return self.ready and elapsed_time > init_duration

    def inactivity_time(self):  # in minutes
        return self.lick_timer.elapsed_time() / 1000 / 60

    def is_licking(self, since=0):
        probe = self.__get_events()
        # reset lick timer if licking is detected &
        if probe > 0:
            self.resp_timer.start()
        self.licked_probe = probe
        return probe

    def __get_events(self):
        probe = 0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick(1)
                    print('Probe 1 activated!')
                    probe = 1
                    self.lick_timer.start()
                elif event.key == pygame.K_RIGHT:
                    self.logger.log_lick(2)
                    print('Probe 2 activated!')
                    probe = 2
                elif event.key == pygame.K_SPACE and self.ready:
                    self.ready = False
                    print('off position')
                elif event.key == pygame.K_SPACE and not self.ready:
                    self.lick_timer.start()
                    self.ready = True
                    print('in position')
        return probe
