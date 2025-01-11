from src.drone_control import DroneController
from src.music_beat_sync import BeatSynchronizer

def main():
    # Path to your music file
    music_file = "music/sample_track.mp3"

    # Initialize the BeatSynchronizer to detect beats
    beat_sync = BeatSynchronizer(music_file)
    beat_times = beat_sync.get_beats()

    # Initialize the DroneController
    drone = DroneController()
    drone.connect()

    try:
        # Start the performance
        drone.takeoff()
        print("Drone is airborne!")

        # Synchronize movements with beats
        for beat_time in beat_times:
            print(f"Performing move at beat: {beat_time:.2f} seconds")
            drone.perform_dance_move()
        
        print("Performance complete!")

    finally:
        # Land the drone safely
        drone.land()
        print("Drone landed successfully!")

if __name__ == "__main__":
    main()
