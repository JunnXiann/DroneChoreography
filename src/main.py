from drone_control import DroneController
from music_beat_sync import RealTimeBeatDetector
import time

def main():
    # Initialize components
    print("\n=== Drone Choreography System ===\n")
    
    # Create drone controller in simulation mode
    drone = DroneController(simulation_mode=False)
    
    # Create beat detector
    detector = RealTimeBeatDetector()
    
    try:
        # Connect to drone
        drone.connect()
        
        # Set up beat callback
        detector.add_beat_callback(drone.perform_dance_move)
        
        # Take off
        drone.takeoff()
        time.sleep(1)  # Wait for stable flight
        
        print("\nSystem ready!")
        print("1. Play music near your microphone")
        print("2. Press Ctrl+C to stop")
        print("\nStarting beat detection...")
        
        # Start beat detection
        detector.start()
        
    except KeyboardInterrupt:
        print("\n\nStopping performance...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # Clean shutdown
        detector.stop()
        drone.land()
        print("\nPerformance ended!")

if __name__ == "__main__":
    main()
