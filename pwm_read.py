import machine
import time


class Servo:
    def __init__(self, pin_in, pin_out):
        self.maxlen = 10

        self.t_high = None
        self.t_low = None

        self.pin = machine.Pin(pin_in, machine.Pin.IN, machine.Pin.PULL_UP)
        self.out = machine.Pin(pin_out, machine.Pin.OUT)
        self.servo = machine.PWM(self.out, freq=50)

    def get_angle(self):
        self.t_highs = []
        self.t_lows = []

        self.t_highs.append(machine.time_pulse_us(self.pin, 1, 1100))
        self.t_highs.append(machine.time_pulse_us(self.pin, 1, 1100))

        self.t_lows.append(machine.time_pulse_us(self.pin, 0, 1100))
        self.t_lows.append(machine.time_pulse_us(self.pin, 0, 1100))

        self.t_high = max(self.t_highs)
        self.t_low = max(self.t_lows)

        tCycle = self.t_high + self.t_low
        theta = 0
        dc = 0
        unitsFC = 360
        dcMin = 0.029
        dcMax = 0.971
        dutyScale = 1
        if(tCycle == 0):
            return 0
        dc = (dutyScale * self.t_high) / tCycle
        theta = ((dc - dcMin) * unitsFC) / (dcMax - dcMin)
        return theta

    def get_error(self, target):
        current_angle = self.get_angle()
        error = target - current_angle
        return error

    def clockwise(self):
        self.servo.duty(80)

    def counterclockwise(self):
        self.servo.duty(72)

    def stop(self):
        self.servo.duty(0)

    def set_angle(self, target):
        # lots of difficulties reading zero with PWM
        if (target == 0):
            target = 360

        SLEEP_US = 1000
        while(abs(self.get_error(target)) > 1):
            error_perc = self.get_error(target) / 360
            if (error_perc > 0):
                self.counterclockwise()
                time.sleep_us(int(SLEEP_US * abs(error_perc)))
            else:
                self.clockwise()
                time.sleep_us(int(SLEEP_US * abs(error_perc)))
        self.stop()

