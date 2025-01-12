from djitellopy import Tello
import time
from queue import Queue
import threading
import random

class DroneController:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.is_connected = False
        self.is_flying = False
        self.command_queue = Queue()
        self.current_height = 0
        self.last_command_time = 0
        self.min_command_interval = 0.1  # seconds between commands
        
        # Initialize Tello drone if not in simulation mode
        if not simulation_mode:
            self.drone = Tello()
        
    def connect(self):
        """Connect to the drone"""
        print("Connecting to drone...")
        if self.simulation_mode:
            self.is_connected = True
            print("Drone connected (SIMULATION MODE)")
        else:
            try:
                self.drone.connect()
                self.is_connected = True
                battery = self.drone.get_battery()
                print(f"Drone connected! Battery: {battery}%")
            except Exception as e:
                print(f"Failed to connect to drone: {e}")
                raise
        
    def takeoff(self):
        """Take off"""
        if not self.is_connected:
            print("Error: Drone not connected!")
            return
            
        print("Taking off...")
        if self.simulation_mode:
            self.is_flying = True
            self.current_height = 100
            print("Drone is airborne! (SIMULATION MODE)")
        else:
            try:
                self.drone.takeoff()
                self.is_flying = True
                print("Drone is airborne!")
            except Exception as e:
                print(f"Takeoff failed: {e}")
        
    def land(self):
        """Land the drone"""
        if not self.is_flying:
            return
            
        print("Landing...")
        if self.simulation_mode:
            self.is_flying = False
            self.current_height = 0
            print("Drone has landed! (SIMULATION MODE)")
        else:
            try:
                self.drone.land()
                self.is_flying = False
                print("Drone has landed!")
            except Exception as e:
                print(f"Landing failed: {e}")
        
    def perform_dance_move(self):
        """Perform a random dance move"""
        if not self.is_flying:
            return
            
        # Ensure minimum time between commands
        current_time = time.time()
        if current_time - self.last_command_time < self.min_command_interval:
            return
            
        self.last_command_time = current_time
        
        if self.simulation_mode:
            self._perform_simulated_move()
        else:
            self._perform_real_move()
            
    def _perform_simulated_move(self):
        """Execute a simulated dance move"""
        moves = [
            (" Up 20cm", lambda: self._move_up(20)),
            (" Down 20cm", lambda: self._move_down(20)),
            (" Rotate Right", lambda: self._rotate(30)),
            (" Rotate Left", lambda: self._rotate(-30)),
            (" Left", lambda: self._move_left(30)),
            (" Right", lambda: self._move_right(30))
        ]
        move_name, move_func = random.choice(moves)
        print(f"Executing move: {move_name}")
        move_func()
        
    def _perform_real_move(self):
        """Execute a real dance move on the Tello drone"""
        try:
            # Simple rotation pattern
            self.drone.rotate_clockwise(90)
            time.sleep(0.5)
            self.drone.rotate_counter_clockwise(90)
            time.sleep(0.5)
            
            # Add more complex moves here
            # self.drone.flip_forward()
            # self.drone.move_up(20)
            # self.drone.move_down(20)
            
        except Exception as e:
            print(f"Dance move failed: {e}")
            
    # Simulation mode movement functions
    def _move_up(self, distance):
        if self.simulation_mode:
            print(f"Simulated: Moving up {distance}cm")
            self.current_height += distance
            
    def _move_down(self, distance):
        if self.simulation_mode:
            print(f"Simulated: Moving down {distance}cm")
            self.current_height = max(0, self.current_height - distance)
            
    def _rotate(self, angle):
        if self.simulation_mode:
            print(f"Simulated: Rotating {abs(angle)}° {'right' if angle > 0 else 'left'}")
            
    def _move_left(self, distance):
        if self.simulation_mode:
            print(f"Simulated: Moving left {distance}cm")
            
    def _move_right(self, distance):
        if self.simulation_mode:
            print(f"Simulated: Moving right {distance}cm")
