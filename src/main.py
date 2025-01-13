from drone_control import DroneController
from music_beat_sync import RealTimeBeatDetector
import time
import logging

def main(simulation_mode=True):
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize components
    # Determine mode
    mode = "SIMULATION MODE" if simulation_mode else "REAL DRONE MODE"
    print(f"\n=== Drone Choreography System ({mode}) ===\n")
    
    detector = None
    drone = None
    
    try:
        # Create drone controller
        logger.info(f"Initializing drone controller in {mode.lower()}...")
        drone = DroneController(simulation_mode=simulation_mode)  
        
        # Create beat detector with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Initializing beat detector (attempt {attempt + 1}/{max_retries})...")
                detector = RealTimeBeatDetector()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.error(f"Failed to initialize beat detector: {e}")
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    raise
        
        # Connect to drone
        logger.info("Connecting to drone...")
        drone.connect()
        
        # Set up beat callback
        detector.add_beat_callback(drone.perform_dance_move)
        
        # Take off
        logger.info("Taking off...")
        drone.takeoff()
        logger.info("Waiting for stable flight...")
        time.sleep(2)
        
        print("\nSystem ready!")
        print("1. Play music near your microphone")
        print("2. Press Ctrl+C to stop\n")
        
        # Start beat detection
        detector.start()
        
    except KeyboardInterrupt:
        logger.info("\nStopping performance gracefully...")
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    finally:
        # Clean shutdown
        try:
            if detector:
                detector.stop()
            if drone:
                if drone.is_flying:
                    logger.info("Landing drone...")
                    drone.land()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("Performance ended!")

if __name__ == "__main__":
    main()
