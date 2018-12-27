import network
import socket
import json
import machine
import utime as time
from ntptime import settime
import urandom

NETWORKS = {
    'Aperture Science': 'stillalive',
    'ASUS': 'internet',
    'Opendoor Guest': 'opendoorguest116'
}

def connect_to_wifi():
    sta_if = network.WLAN(network.STA_IF)
    print('connecting to network...')
    sta_if.active(True)
    if not sta_if.isconnected():
        networks = [str(net[0], 'utf8') for net in sta_if.scan()]
        networks = [net for net in networks if net in NETWORKS]
        if len(networks):
            net = networks[0]
            sta_if.connect(net, NETWORKS[net])
            while not sta_if.isconnected(): 
                print(".", end="")
                time.sleep_ms(100)
        print('network config:', sta_if.ifconfig())
    else:
        try:
            settime()
        except OSError as e:
            print(e)


def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    try:
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        result = ''
        while True:
            data = s.recv(100)
            if data:
                data = str(data, 'utf8')
                result += data
            else:
                break
    finally:
        s.close()
    return result

def get_bus():
    connect_to_wifi()
    default_prediction = {'prediction': [{'minutes': urandom.getrandbits(4)}]}
    result = http_get("http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=sf-muni&r=37&s=6236")
    result = json.loads(result.split('\r\n')[-2])
    print(result)
    predictions = result['predictions'].get('direction', default_prediction)['prediction']
    if type(predictions) == list:
        return int(predictions[0]['minutes'])
    return int(predictions['minutes'])

def inc(t):
    servo = machine.PWM(machine.Pin(15), freq=50)
    servo.duty(115)
    time.sleep_ms(t)
    servo.duty(0)

def main():
    current_pos = 0
    drift = 0
    while True:
        minutes = get_bus()
        minutes = min(minutes, 12)

        distance = (current_pos - minutes)
        if distance < 0:
             distance += 12
        
        inc(80 * distance)
        
        print("old current pos " + str(current_pos))
        current_pos = minutes
        if current_pos > 12:
            current_pos = current_pos % 12
        if current_pos < 0:
            current_pos += 12
        print("new data current pos, minutes and distance: " + str((current_pos, minutes, distance)))
        drift += 1
        time.sleep(10)

