import pyaudio
import numpy as np
import time
import threading
from queue import Queue

class RealTimeBeatDetector:
    def __init__(self, device_index=None):
        # Audio parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.device_index = device_index
        self.audio_queue = Queue(maxsize=10)
        
        # Beat detection parameters
        self.energy_threshold = 0.01
        self.min_beat_interval = 0.2  # minimum time between beats (seconds)
        self.last_beat_time = 0
        
        # Control flags
        self.is_running = False
        self.beat_callbacks = []
        
        # Initialize PyAudio
        self.p = None
        self.stream = None
        
    def find_input_device(self):
        """Find the best input device"""
        p = pyaudio.PyAudio()
        default_device = p.get_default_input_device_info()
        print(f"Default input device: {default_device['name']}")
        return default_device['index']
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_running:
            try:
                audio_data = np.frombuffer(in_data, dtype=np.float32)
                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(audio_data)
            except Exception as e:
                print(f"Error in callback: {e}")
        return (in_data, pyaudio.paContinue)
        
    def process_audio(self):
        """Process audio data from queue"""
        while self.is_running:
            try:
                # Get audio data from queue
                audio_data = self.audio_queue.get(timeout=1.0)
                
                # Calculate energy
                energy = np.mean(np.abs(audio_data))
                
                # Check if this is a beat
                current_time = time.time()
                if (energy > self.energy_threshold and 
                    current_time - self.last_beat_time > self.min_beat_interval):
                    self.last_beat_time = current_time
                    # Notify all callbacks
                    for callback in self.beat_callbacks:
                        callback()
                        
            except Exception as e:
                if self.is_running:  # Only print if we're still supposed to be running
                    print(f"Error processing audio: {e}")
                    
    def start(self):
        """Start beat detection"""
        if self.is_running:
            return
            
        print("Starting beat detection...")
        self.is_running = True
        
        try:
            # Initialize PyAudio
            self.p = pyaudio.PyAudio()
            
            # Find input device if not specified
            if self.device_index is None:
                self.device_index = self.find_input_device()
                
            # Start processing thread
            self.process_thread = threading.Thread(target=self.process_audio)
            self.process_thread.daemon = True
            self.process_thread.start()
            
            # Open stream
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.CHUNK,
                stream_callback=self.audio_callback
            )
            
            print("Beat detection running. Play music now!")
            print("Press Ctrl+C to stop")
            
            # Keep the stream running
            while self.is_running:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error starting audio: {e}")
            self.stop()
            
    def stop(self):
        """Stop beat detection"""
        print("Stopping beat detection...")
        self.is_running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
            
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
            
    def add_beat_callback(self, callback):
        """Add a function to be called when a beat is detected"""
        self.beat_callbacks.append(callback)
