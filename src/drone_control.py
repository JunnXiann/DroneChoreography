from djitellopy import Tello

class DroneController:
    def __init__(self):
        self.tello = Tello()

    def connect(self):
        """
        Connects to the drone and prints the battery level.
        """
        print("Connecting to drone...")
        self.tello.connect()
        print(f"Battery level: {self.tello.get_battery()}%")

    def takeoff(self):
        """
        Commands the drone to take off.
        """
        self.tello.takeoff()

    def land(self):
        """
        Commands the drone to land safely.
        """
        self.tello.land()

    def perform_dance_move(self):
        """
        Executes a simple dance move. Customize this for complex choreography.
        """
        self.tello.rotate_clockwise(30)  # Rotate 30 degrees
