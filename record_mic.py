import pyaudio
import wave
from log_entry import log_entry



class RecordMic:
    def __init__(self, record_sec, config_mic):
        self.p = pyaudio.PyAudio()
        self.FORMAT = config_mic['FORMAT']
        self.CHANNELS = config_mic['MIC_CHANNELS']
        self.RATE = config_mic['MIC_RATE']
        self.CHUNK = config_mic['MIC_CHUNK']
        self.ID_MIC = config_mic['ID_MIC']
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=8000,
                                  input=True,
                                  frames_per_buffer=self.CHUNK,
                                  input_device_index=self.ID_MIC,
                                  )
        self.record_second = record_sec

    def record_mic(self, wave_out_path):
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        log_entry("* Запись микрофона началась")
        for i in range(0, int(self.RATE / self.CHUNK * self.record_second)):
            data = self.stream.read(self.CHUNK, exception_on_overflow = False)
            wf.writeframes(data)
        log_entry("* Запись микрофона завершилась")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        wf.close()
        del wf
