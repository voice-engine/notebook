"""
A example to show Noise Suppression (NS) and Keyword Spotting (KWS)

The keyword is "computer".

Requirements:
    snowboy - https://github.com/Kitt-AI/snowboy
"""


import time
from voice_engine.source import Source
from voice_engine.kws import KWS


def main():
    src = Source(rate=16000, channels=1, device_name="default")
    kws = KWS(model='computer', sensitivity=0.6, verbose=True)

    src.pipeline(kws)

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