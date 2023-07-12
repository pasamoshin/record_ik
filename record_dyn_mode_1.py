import pyaudio
import wave
from log_entry import log_entry



class RecordDyn_1:
    def __init__(self, record_sec, config_speak):
        self.p = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = config_speak["DYN_RATE"]
        self.CHUNK = 8000
        self.ID_MIC = int(config_speak["ID_DYN"])
        self.stream = self.p.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK,
                                    input_device_index=self.ID_MIC,
                                )


        self.record_second = record_sec

    def record_dyn(self, wave_out_path):
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        log_entry("* Запись динамика началась (мод 1)")
        for i in range(0, int(self.RATE / self.CHUNK * self.record_second)):
            data = self.stream.read(self.CHUNK, exception_on_overflow = False)
            wf.writeframes(data)
        log_entry("* Запись динамика завершилась (мод 1)")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        wf.close()
        del wf
