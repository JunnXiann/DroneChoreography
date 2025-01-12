import pyaudio
import sys

def main():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    try:
        p = pyaudio.PyAudio()
        
        # List all audio devices
        print("\nAvailable audio input devices:")
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:  # Only show input devices
                print(f"Device {i}: {dev_info['name']}")
                
        p.terminate()
        print("\nPyAudio test successful!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
