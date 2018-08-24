'''
pr0ntools
Benchmarking utility
Copyright 2010 John McMaster
'''

import time

def time_str(delta):
    fraction = delta % 1
    delta -= fraction
    delta = int(delta)
    seconds = delta % 60
    delta /= 60
    minutes = delta % 60
    delta /= 60
    hours = delta
    return '%02d:%02d:%02d.%04d' % (hours, minutes, seconds, fraction * 10000)

class Benchmark:
    start_time = None
    end_time = None
    
    def __init__(self, max_items = None):
        # For the lazy
        self.start_time = time.time()
        self.end_time = None
        self.max_items = max_items
        self.cur_items = 0

    def start(self):
        self.start_time = time.time()
        self.end_time = None
        self.cur_items = 0

    def stop(self):
        self.end_time = time.time()
    
    def advance(self, n = 1):
        self.cur_items += n

    def set_cur_items(self, n):
        self.cur_items = n
		
    def delta_s(self):    
        if self.end_time:
            return self.end_time - self.start_time
        else:
            return time.time() - self.start_time
    
    def __str__(self):
        if self.end_time:
            return time_str(self.end_time - self.start_time)
        elif self.max_items:
            cur_time = time.time()
            delta_t = cur_time - self.start_time
            rate_s = 'N/A'
            if delta_t > 0.000001:
                rate = self.cur_items / (delta_t)
                rate_s = '%f items / sec' % rate
                if rate == 0:
                    eta_str = 'inf'
                else:
                    remaining = (self.max_items - self.cur_items) / rate
                    eta_str = time_str(remaining)
            else:
                eta_str = "indeterminate"
            return '%d / %d, ETA: %s @ %s' % (self.cur_items, self.max_items, eta_str, rate_s)
        else:
            return time_str(time.time() - self.start_time)

