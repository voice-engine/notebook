"""
A example to show delay&sum beamforming, Noise Suppression (NS) and Keyword Spotting (KWS)

The keyword is "computer".

Requirements:
    snowboy - https://github.com/Kitt-AI/snowboy
    python-webrtc-audio-processing - `pip3 install webrtc-audio-processing`
"""


import time
import numpy as np

from voice_engine.element import Element
from voice_engine.source import Source
from voice_engine.kws import KWS
from voice_engine.ns import NS


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


def main():
    src = Source(rate=16000, channels=4, device_name="default")
    ds = DelaySum(channels=src.channels)
    ns = NS(rate=16000, channels=1)
    kws = KWS(model='computer', sensitivity=0.6, verbose=True)

    src.pipeline(ds, ns, kws)

    def on_detected(keyword):
        print('\ndetected {}'.format(keyword))

    kws.set_callback(on_detected)

    src.pipeline_start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()


if __name__ == '__main__':
    main()