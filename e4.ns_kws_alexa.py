"""
Hands-free Voice Assistant with Snowboy and Alexa Voice Service. The wake word is "alexa"

Requirements:
    snowboy - https://github.com/Kitt-AI/snowboy
    python-webrtc-audio-processing - `pip3 install webrtc-audio-processing`
    avs - `pip3 install avs`
"""

import os
import signal
import time
import logging
import numpy as np

from voice_engine.element import Element
from voice_engine.source import Source
from voice_engine.kws import KWS
from voice_engine.ns import NS
from avs.alexa import Alexa


class DelaySum(Element):
    '''a simplest delay&sum beamforming with zero delay'''
    
    def __init__(self, channels=4):
        super(DelaySum, self).__init__()
        self.channels = channels

    def put(self, data):
        data = np.fromstring(data, dtype='int16')
        bf = data[0::self.channels] / self.channels
        for ch in range(1, self.channels):
            bf += data[ch::self.channels] / self.channels
        super(DelaySum, self).put(bf.astype('int16').tostring())


def leds_on():
    os.system("mosquitto_pub -t '/voicen/leds/value' -m '0xf'")

def leds_off():
    os.system("mosquitto_pub -t '/voicen/leds/value' -m '0x0'")

def main():
    logging.basicConfig(level=logging.DEBUG)

    src = Source(rate=16000, channels=4, device_name='default')
    ds = DelaySum(channels=src.channels)
    ns = NS(rate=16000, channels=1)
    kws = KWS(model='alexa')
    alexa = Alexa()

    alexa.state_listener.on_listening = leds_on
#     alexa.state_listener.on_thinking = pixel_ring.think
#     alexa.state_listener.on_speaking = pixel_ring.speak
    alexa.state_listener.on_finished = leds_off

    src.link(ds)
    ds.link(ns)
    ns.link(kws)
    kws.link(alexa)

    def on_detected(keyword):
        logging.info('\ndetected {}'.format(keyword))
        alexa.listen()

    kws.set_callback(on_detected)

    is_quit = []
    def signal_handler(sig, frame):
        is_quit.append(True)
        print('quit')
    signal.signal(signal.SIGINT, signal_handler)

    src.pipeline_start()
    while not is_quit:
        time.sleep(1)

    src.pipeline_stop()


if __name__ == '__main__':
    main()
