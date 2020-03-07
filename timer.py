#!/usr/bin/env python

import time

CLOCK = {}
RUNNING_TIMERS = {}


def time_function(fun):
    def time_helper(*args, **kwargs):
        t0 = time.time()
        ret_value = fun(*args, **kwargs)
        t1 = time.time()
        increase_clock(fun.__name__, t1 - t0)
        return ret_value

    return time_helper


def increase_clock(name, duration, total=True):
    timer = CLOCK.setdefault(name, [0, 0])
    timer[0] += 1
    timer[1] += duration
    if total:
        timer = CLOCK.setdefault("total", [0, 0])
        timer[0] += 1
        timer[1] += duration


def get_clock():
    return CLOCK


def start_named_timer(name):
    RUNNING_TIMERS[name] = time.time()


def stop_named_timer(name, total=True):
    t0 = RUNNING_TIMERS.get(name, 0)
    increase_clock(name, time.time() - t0, total)


def reset_clock():
    CLOCK = {}
