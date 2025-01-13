import pyaudio
import numpy as np
import time
import threading
from queue import Queue, Empty
import logging
from scipy.signal import butter, lfilter

class RealTimeBeatDetector:
    def __init__(self, device_index=None):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Audio parameters
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.device_index = device_index
        self.audio_queue = Queue(maxsize=10)
        
        # Beat detection parameters
        self.energy_threshold = 0.0003
        self.min_beat_interval = 0.3
        self.last_beat_time = 0
        self.beat_count = 0
        self.last_visualization_time = 0
        self.visualization_interval = 0.1
        
        # Frequency bands for music detection
        self.freq_bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
        }
        
        # Band energy history
        self.band_energies = {band: [] for band in self.freq_bands}
        self.history_size = 20
        self.min_active_bands = 2
        
        # Control flags
        self.is_running = False
        self.beat_callbacks = []
        
    def butter_bandpass(self, lowcut, highcut, order=4):
        """Create a butterworth bandpass filter"""
        nyq = 0.5 * self.RATE
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
        
    def bandpass_filter(self, data, lowcut, highcut, order=4):
        """Apply bandpass filter to the data"""
        b, a = self.butter_bandpass(lowcut, highcut, order=order)
        y = lfilter(b, a, data)
        return y
        
    def get_band_energy(self, data, band_name):
        """Get the energy in a specific frequency band"""
        low, high = self.freq_bands[band_name]
        filtered_data = self.bandpass_filter(data, low, high)
        return np.sqrt(np.mean(np.square(filtered_data)))
        
    def is_music_beat(self, audio_data):
        """Detect if there's a musical beat in the audio"""
        is_beat = False
        total_energy = 0
        band_info = []
        active_bands = 0
        
        # Calculate energy in each frequency band
        for band in self.freq_bands:
            energy = self.get_band_energy(audio_data, band)
            self.band_energies[band].append(energy)
            
            # Keep history size limited
            if len(self.band_energies[band]) > self.history_size:
                self.band_energies[band].pop(0)
            
            # Calculate average energy for this band
            if len(self.band_energies[band]) >= 2:
                avg_energy = np.mean(self.band_energies[band][:-1])
                current_energy = self.band_energies[band][-1]
                
                # Check if current energy is significantly higher than average
                is_band_beat = current_energy > avg_energy * 1.3
                if is_band_beat:
                    active_bands += 1
                    total_energy += current_energy
                    self.logger.info(f"Band {band} beat detected: Energy {current_energy:.6f}, Avg {avg_energy:.6f}")
                
                # Store band info for visualization
                band_info.append({
                    'name': band,
                    'energy': current_energy,
                    'avg': avg_energy,
                    'is_beat': is_band_beat
                })
        
        # Only consider it a beat if multiple bands are active
        is_beat = active_bands >= self.min_active_bands
        
        # Log overall beat detection
        if is_beat:
            self.logger.info(f"Overall beat detected with {active_bands} active bands")
        else:
            self.logger.debug(f"No beat detected. Active bands: {active_bands}")
        
        # Update visualization at fixed intervals
        current_time = time.time()
        if current_time - self.last_visualization_time >= self.visualization_interval:
            self._visualize_beat_detection(band_info, is_beat, active_bands)
            self.last_visualization_time = current_time
        
        return is_beat, total_energy
        
    def _visualize_beat_detection(self, band_info, is_beat, active_bands):
        """Create a visual representation of the beat detection"""
        # Clear previous line and move cursor up
        print('\033[F' * 8 + '\033[K', end='')
        
        # Print header with stats
        print("\n=== Beat Monitor ===")
        print(f"Total Beats: {self.beat_count} | Active Bands: {active_bands}/{len(self.freq_bands)}")
        
        # Print each frequency band
        for band in band_info:
            # Create a visual meter
            energy_ratio = min(band['energy'] / (band['avg'] * 1.3), 1.0)
            meter_length = int(energy_ratio * 20)
            meter = '█' * meter_length + '░' * (20 - meter_length)
            
            # Add beat indicator
            beat_indicator = '🔊' if band['is_beat'] else '  '
            
            # Print the band info
            print(f"{band['name']:8} {beat_indicator} [{meter}]")
        
        # Print overall beat status
        status = '🎵 BEAT!' if is_beat else '       '
        print(f"\nStatus: {status}")
        
        # Add sound alert for beat detection
        if is_beat:
            print("\a", end='')  # ASCII Bell character for sound alert
        
    def process_audio(self):
        """Process audio data from queue"""
        # Print initial empty visualization
        print("\n" * 8)
        
        while self.is_running:
            try:
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                except Empty:
                    continue
                
                # Detect musical beats
                is_beat, energy = self.is_music_beat(audio_data)
                
                # Check if this is a beat
                current_time = time.time()
                if (is_beat and energy > self.energy_threshold and 
                    current_time - self.last_beat_time > self.min_beat_interval):
                    self.last_beat_time = current_time
                    self.beat_count += 1
                    self.logger.info(f"Music beat detected! Energy: {energy:.6f}")
                    
                    # Execute callbacks
                    for callback in self.beat_callbacks:
                        try:
                            callback()
                        except Exception as e:
                            self.logger.error(f"Error in beat callback: {e}")
                
            except Exception as e:
                if not self.is_running:
                    break
                self.logger.error(f"Error processing audio: {e}")
                time.sleep(0.1)
                
    def find_input_device(self):
        """Find the best input device"""
        p = pyaudio.PyAudio()
        try:
            
            # Try to find a working input device
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        self.logger.info(f"\nSelected input device {i}: {device_info['name']}")
                        return i
                except:
                    continue
            
            # If no device found, try default
            default_device = p.get_default_input_device_info()
            self.logger.info(f"\nUsing default device: {default_device['name']}")
            return default_device['index']
            
        except Exception as e:
            self.logger.error(f"Error finding input device: {e}")
            raise
        finally:
            p.terminate()
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if self.is_running:
            try:
                audio_data = np.frombuffer(in_data, dtype=np.float32)
                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(audio_data)
            except Exception as e:
                self.logger.error(f"Error in audio callback: {e}")
        return (in_data, pyaudio.paContinue)
        
    def start(self):
        """Start beat detection"""
        if self.is_running:
            return
            
        self.logger.info("\nInitializing beat detection...")
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
            
            if not self.stream.is_active():
                raise Exception("Failed to start audio stream")
            
            self.logger.info("Beat detection running successfully!")
            print("\nBeat detection is active and listening!")
            print("1. Play music near your microphone")
            print("2. Press Ctrl+C to stop\n")
            
            # Keep the stream running
            while self.is_running:
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error in beat detection: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop beat detection"""
        self.logger.info("Stopping beat detection...")
        self.is_running = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.logger.error(f"Error stopping stream: {e}")
        
        if self.p:
            try:
                self.p.terminate()
            except Exception as e:
                self.logger.error(f"Error terminating PyAudio: {e}")
            
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
            
    def add_beat_callback(self, callback):
        """Add a function to be called when a beat is detected"""
        self.beat_callbacks.append(callback)
