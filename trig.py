from machine import Pin
from collections.deque import deque
import time


class TRIG:
    def __init__(self, pin):
        self.times = deque()
        self.maxlen = 10

        self.result_falling = None
        self.start_falling = 0
        self.result_rising = None
        self.start_rising = 0

        self.pin = Pin(pin, Pin.IN, pull=Pin.PULL_UP)
        self.pin.irq(trigger=(Pin.IRQ_FALLING | Pin.IRQ_RISING), handler=self.trig_falling_or_rising)

    def trig_falling_or_rising(self, pin):
        if(len(self.times) > self.maxlen):
            self.times.popleft()
        self.times.append((self.pin.value(), time.ticks_cpu()))

        if self.pin.value() == 1:
            self.start_falling = time.ticks_cpu()
        elif self.start_falling is not 0:
            self.result_falling = time.ticks_diff(self.start_falling, time.ticks_cpu())
            # print("falling time: " + str(self.result_falling))
            self.start_falling = 0

        if self.pin.value() == 0:
            self.start_rising = time.ticks_cpu()
        elif self.start_rising is not 0:
            self.result_rising = time.ticks_diff(self.start_rising, time.ticks_cpu())
            #   print("rising time: " + str(self.result_rising))
            self.start_rising = 0

    def get_rate(self, callback_fn):
        self.result_falling = None
        self.start_falling = 0
        self.result_rising = None
        self.start_rising = 0
        while (self.result_rising is None) or (self.result_falling is None):
            print("rising times")
            print(str(self.times))
            print("waiting...")

        tHigh = self.result_rising
        tLow = self.result_falling
        tCycle = tHigh + tLow

        theta = 0
        dc = 0
        unitsFC = 360
        dcMin = 0.029
        dcMax = 0.971
        dutyScale = 1
        dc = (dutyScale * tHigh) / tCycle
        theta = ((dc - dcMin) * unitsFC) / (dcMax - dcMin)
        callback_fn(theta)
