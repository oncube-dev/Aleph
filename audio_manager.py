import pyaudio
import socket
import threading
import time
import wave
import numpy as np
from typing import Optional, Callable
try:
    import client_config as config
except ImportError:
    try:
        import server_config as config
    except ImportError:
        import config

class AudioManager:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        self.recording_thread = None
        self.playing_thread = None
        self.udp_socket = None
        self.callback_function = None
        
        # Аудио параметры
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        self.channels = config.AUDIO_CHANNELS
        self.format = pyaudio.paInt16
        
        # Потоки для записи и воспроизведения
        self.input_stream = None
        self.output_stream = None
        
        # Буферы для аудио
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
    
    def start_audio_call(self, remote_host: str, remote_port: int, is_caller: bool = True):
        """Начало голосового звонка"""
        try:
            # Создание UDP сокета для аудио
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            if is_caller:
                # Звонящий отправляет аудио на указанный адрес
                self.remote_address = (remote_host, remote_port)
            else:
                # Получающий привязывает сокет к локальному порту
                self.udp_socket.bind(('', remote_port))
                self.remote_address = None
            
            # Запуск записи и воспроизведения
            self.start_recording()
            self.start_playing()
            
            print(f"Голосовой звонок {'начат' if is_caller else 'принят'}")
            return True
            
        except Exception as e:
            print(f"Ошибка начала звонка: {e}")
            return False
    
    def start_recording(self):
        """Запуск записи аудио"""
        if self.is_recording:
            return
        
        try:
            self.input_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            print("Запись аудио запущена")
            
        except Exception as e:
            print(f"Ошибка запуска записи: {e}")
    
    def _recording_loop(self):
        """Цикл записи аудио"""
        while self.is_recording:
            try:
                # Чтение аудио данных
                audio_data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Отправка аудио данных через UDP
                if self.udp_socket and self.remote_address:
                    self.udp_socket.sendto(audio_data, self.remote_address)
                
                # Сохранение в буфер для локального воспроизведения (эхо)
                with self.buffer_lock:
                    self.audio_buffer.append(audio_data)
                    # Ограничение размера буфера
                    if len(self.audio_buffer) > 10:
                        self.audio_buffer.pop(0)
                
            except Exception as e:
                print(f"Ошибка записи аудио: {e}")
                break
        
        # Очистка
        if self.input_stream:
            self.input_stream.close()
            self.input_stream = None
    
    def start_playing(self):
        """Запуск воспроизведения аудио"""
        if self.is_playing:
            return
        
        try:
            self.output_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_playing = True
            self.playing_thread = threading.Thread(target=self._playing_loop)
            self.playing_thread.daemon = True
            self.playing_thread.start()
            
            print("Воспроизведение аудио запущено")
            
        except Exception as e:
            print(f"Ошибка запуска воспроизведения: {e}")
    
    def _playing_loop(self):
        """Цикл воспроизведения аудио"""
        while self.is_playing:
            try:
                # Получение аудио данных из буфера
                audio_data = None
                with self.buffer_lock:
                    if self.audio_buffer:
                        audio_data = self.audio_buffer.pop(0)
                
                if audio_data:
                    # Воспроизведение аудио
                    self.output_stream.write(audio_data)
                else:
                    # Небольшая задержка если нет данных
                    time.sleep(0.01)
                
            except Exception as e:
                print(f"Ошибка воспроизведения аудио: {e}")
                break
        
        # Очистка
        if self.output_stream:
            self.output_stream.close()
            self.output_stream = None
    
    def receive_audio_data(self, audio_data: bytes):
        """Получение аудио данных от удаленного пользователя"""
        try:
            # Добавление в буфер для воспроизведения
            with self.buffer_lock:
                self.audio_buffer.append(audio_data)
                # Ограничение размера буфера
                if len(self.audio_buffer) > 10:
                    self.audio_buffer.pop(0)
        except Exception as e:
            print(f"Ошибка получения аудио данных: {e}")
    
    def start_audio_receiver(self, local_port: int):
        """Запуск приемника аудио данных"""
        try:
            # Создание UDP сокета для приема аудио
            self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiver_socket.bind(('', local_port))
            
            # Запуск потока для приема аудио
            self.receiver_thread = threading.Thread(target=self._receiver_loop)
            self.receiver_thread.daemon = True
            self.receiver_thread.start()
            
            print(f"Приемник аудио запущен на порту {local_port}")
            return True
            
        except Exception as e:
            print(f"Ошибка запуска приемника аудио: {e}")
            return False
    
    def _receiver_loop(self):
        """Цикл приема аудио данных"""
        while hasattr(self, 'receiver_socket') and self.receiver_socket:
            try:
                # Получение аудио данных
                audio_data, address = self.receiver_socket.recvfrom(self.chunk_size * 2)
                
                # Обработка полученных данных
                self.receive_audio_data(audio_data)
                
            except Exception as e:
                print(f"Ошибка приема аудио: {e}")
                break
    
    def stop_audio_call(self):
        """Остановка голосового звонка"""
        try:
            self.is_recording = False
            self.is_playing = False
            
            # Остановка потоков
            if self.recording_thread:
                self.recording_thread.join(timeout=1)
            if self.playing_thread:
                self.playing_thread.join(timeout=1)
            
            # Закрытие потоков аудио
            if self.input_stream:
                self.input_stream.close()
                self.input_stream = None
            
            if self.output_stream:
                self.output_stream.close()
                self.output_stream = None
            
            # Закрытие UDP сокета
            if self.udp_socket:
                self.udp_socket.close()
                self.udp_socket = None
            
            # Очистка буфера
            with self.buffer_lock:
                self.audio_buffer.clear()
            
            print("Голосовой звонок остановлен")
            
        except Exception as e:
            print(f"Ошибка остановки звонка: {e}")
    
    def play_notification_sound(self):
        """Воспроизведение звука уведомления о новых сообщениях"""
        try:
            # Создание простого звукового сигнала (бип)
            sample_rate = 44100
            duration = 0.1  # 100ms
            frequency = 800  # 800 Hz
            
            # Генерация синусоидального сигнала
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Преобразование в 16-битный формат
            audio_data = (tone * 32767).astype(np.int16)
            
            # Создание временного потока воспроизведения
            temp_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            
            # Воспроизведение звука
            temp_stream.write(audio_data.tobytes())
            
            # Закрытие временного потока
            temp_stream.close()
            
            print("Звук уведомления воспроизведен")
            
        except Exception as e:
            print(f"Ошибка воспроизведения звука уведомления: {e}")
    
    def play_sound(self, sound_file: str):
        """Воспроизведение звукового файла"""
        try:
            with wave.open(sound_file, 'rb') as wf:
                # Открытие потока для воспроизведения
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # Чтение и воспроизведение данных
                data = wf.readframes(self.chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                # Очистка
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def record_audio_file(self, filename: str, duration: float = 5.0):
        """Запись аудио в файл"""
        try:
            # Открытие потока для записи
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            num_frames = int(self.sample_rate / self.chunk_size * duration)
            
            print(f"Запись аудио в файл {filename}...")
            
            for i in range(num_frames):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            # Очистка
            stream.stop_stream()
            stream.close()
            
            # Сохранение в WAV файл
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"Аудио записано в файл {filename}")
            
        except Exception as e:
            print(f"Ошибка записи аудио в файл: {e}")
    
    def get_audio_devices(self):
        """Получение списка доступных аудио устройств"""
        devices = []
        
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'max_input_channels': device_info['maxInputChannels'],
                    'max_output_channels': device_info['maxOutputChannels'],
                    'default_sample_rate': device_info['defaultSampleRate']
                })
        except Exception as e:
            print(f"Ошибка получения списка устройств: {e}")
        
        return devices
    
    def set_audio_device(self, device_index: int, is_input: bool = True):
        """Установка аудио устройства"""
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            
            if is_input and device_info['maxInputChannels'] > 0:
                # Устройство ввода
                if self.input_stream:
                    self.input_stream.close()
                
                self.input_stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.chunk_size
                )
                print(f"Устройство ввода установлено: {device_info['name']}")
                
            elif not is_input and device_info['maxOutputChannels'] > 0:
                # Устройство вывода
                if self.output_stream:
                    self.output_stream.close()
                
                self.output_stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True,
                    output_device_index=device_index,
                    frames_per_buffer=self.chunk_size
                )
                print(f"Устройство вывода установлено: {device_info['name']}")
                
        except Exception as e:
            print(f"Ошибка установки аудио устройства: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop_audio_call()
        
        if hasattr(self, 'receiver_socket') and self.receiver_socket:
            self.receiver_socket.close()
        
        if hasattr(self, 'receiver_thread') and self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=1)
        
        self.audio.terminate()
        print("Аудио менеджер очищен")
