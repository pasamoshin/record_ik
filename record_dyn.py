import soundcard as sc
import soundfile as sf
from log_entry import log_entry


class RecordDyn():
    def __init__(self, record_sec, config_speakers) -> None:
        self.record_sec = record_sec
        self.config_speakers = config_speakers


    def record_dyn(self, wave_out_path):
        if self.config_speakers['ID_DYN'] == 'default':
            self.id_dyn = str(sc.default_speaker().name)
        elif self.config_speakers['ID_DYN'] == 'Stereo Mix':
            self.id_dyn = 'Стерео микшер'
        else:
            try:
                self.id_speak = sc.get_speaker(self.config_speakers['ID_DYN'])
                self.id_dyn = self.id_speak
            except Exception as e:
                log_entry(e)
        with sc.get_microphone(id=self.id_dyn, include_loopback=True).recorder(samplerate=self.config_speakers['DYN_RATE']) as mic:
            log_entry(f'Выбран динамик {self.id_dyn}')
            # record audio with loopback from default speaker.
            log_entry('Запись динамика началась')
            data = mic.record(
                numframes=self.config_speakers['DYN_RATE']*self.record_sec)
            log_entry('Запись динамика завершилась')
            # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
            sf.write(file=wave_out_path,
                     data=data[:, 0], samplerate=self.config_speakers['DYN_RATE'])
