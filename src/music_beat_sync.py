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
        
        # Frequency bands for drum detection
        self.freq_bands = {
            'kick': (50, 100),      # Bass drum
            'snare': (200, 400),    # Snare drum
            'hihat': (10000, 15000),# Hi-hats
            'toms': (100, 300),     # Tom drums
        }
        
        # Band energy history
        self.band_energies = {band: [] for band in self.freq_bands}
        self.history_size = 20
        self.min_active_bands = 1  # Reduced to detect individual drum hits
        
        # Drum-specific thresholds and minimum energies
        self.drum_thresholds = {
            'kick': 0.1,    
            'snare': 0.1,   
            'hihat': 0.1,   
            'toms': 0.1    
        }
        
        # Minimum energy required to trigger movement
        self.min_trigger_energy = {
            'kick': 0.1,     
            'snare': 0.1,    
            'hihat': 0.1,    
            'toms': 0.1      
        }
        
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
        
    def detect_beats(self, audio_data):
        """Detect beats in the audio data"""
        try:
            # Apply bandpass filters and calculate energy for each band
            band_energies = {}
            active_bands = []
            significant_activity = False  # Flag for significant energy detection
            
            for band, (low, high) in self.freq_bands.items():
                filtered = self.bandpass_filter(audio_data, low, high)
                energy = np.sum(filtered * filtered) / len(filtered)
                band_energies[band] = energy
                
                # Store energy history
                self.band_energies[band].append(energy)
                if len(self.band_energies[band]) > self.history_size:
                    self.band_energies[band].pop(0)
                
                # Calculate average energy for this band
                avg_energy = np.mean(self.band_energies[band])
                
                # Check if energy is above minimum threshold for movement
                if energy > self.min_trigger_energy[band]:
                    significant_activity = True
                
                # Use drum-specific thresholds
                threshold = self.drum_thresholds[band]
                
                # Check if this band has a beat and enough energy
                if energy > avg_energy + threshold and energy > self.min_trigger_energy[band]:
                    active_bands.append(band)
                    self.logger.info(f"{band.upper()} hit detected! Energy: {energy:.6f}")
            
            # Only visualize if there's significant activity
            current_time = time.time()
            if current_time - self.last_visualization_time >= self.visualization_interval:
                if significant_activity:
                    self._visualize_drum_energies(band_energies)
                self.last_visualization_time = current_time
            
            # Trigger callback if any drum is detected with sufficient energy
            if active_bands and time.time() - self.last_beat_time >= self.min_beat_interval:
                self.last_beat_time = time.time()
                self.beat_count += 1
                
                # Call all registered callbacks with the detected drum type
                for callback in self.beat_callbacks:
                    callback(active_bands[0])  
                
        except Exception as e:
            self.logger.error(f"Error in beat detection: {e}")
            
    def _visualize_drum_energies(self, energies):
        """Visualize the energy levels of different drum components"""
        print("\n=== Drum Monitor ===")
        for band, energy in energies.items():
            if energy > self.min_trigger_energy[band] * 0.5:  # Show only if energy is significant
                bars = int(min(energy * 50000, 30))  # Scale factor adjusted for visualization
                threshold_bars = int(self.min_trigger_energy[band] * 50000)
                print(f"{band.upper():6} {'█' * bars}{' ' * (30 - bars)} | Energy: {energy:.6f}")
                print(f"       {' ' * threshold_bars}↑ Min Threshold")
        active_count = sum(1 for band, energy in energies.items() if energy > self.min_trigger_energy[band])
        print(f"Total Beats: {self.beat_count} | Active Drums: {active_count}/4")
        
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
                self.detect_beats(audio_data)
                
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
