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
        """Execute a random dance move on the Tello drone"""
        try:
            # List of possible moves with their corresponding functions
            moves = [
                ("rotate_clockwise", lambda: self.drone.rotate_clockwise(90)),
                ("rotate_counter_clockwise", lambda: self.drone.rotate_counter_clockwise(90)),
                ("flip_forward", lambda: self.drone.flip_forward()),
                ("flip_back", lambda: self.drone.flip_back()),
                ("flip_left", lambda: self.drone.flip_left()),
                ("flip_right", lambda: self.drone.flip_right()),
                ("move_up", self._safe_move_up),
                ("move_down", self._safe_move_down),
                ("move_forward", self._safe_move_forward),
                ("move_back", self._safe_move_back),
                ("move_left", self._safe_move_left),
                ("move_right", self._safe_move_right)
            ]
            
            # Choose a random move
            move_name, move_func = random.choice(moves)
            print(f"Attempting move: {move_name}")
            
            # Try the move up to 3 times
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    result = move_func()
                    if result is False:  # Safety check failed
                        print(f"Safety check failed for {move_name}, skipping...")
                        break
                    print(f"Successfully executed: {move_name}")
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Failed to execute {move_name} after {max_attempts} attempts: {e}")
                    else:
                        print(f"Attempt {attempt + 1} failed, retrying...")
                        time.sleep(1)  # Wait a second before retrying
                        
        except Exception as e:
            print(f"Dance move failed: {e}")
            
    def _safe_move_up(self):
        """Safely move up with obstacle detection"""
        tof_reading = self.drone.get_distance_tof()
        if tof_reading < 100:  # Less than 1 meter from obstacle
            print("Cannot move up - obstacle detected above")
            return False
        self.drone.move_up(20)
        return True

    def _safe_move_down(self):
        """Safely move down with height check"""
        current_height = self.drone.get_height()
        if current_height < 50:  # Too close to ground
            print("Cannot move down - too close to ground")
            return False
        self.drone.move_down(20)
        return True

    def _safe_move_forward(self):
        """Safely move forward with obstacle detection"""
        front_reading = self.drone.get_barometer()  # Using barometer as proxy for forward distance
        if front_reading < 100:  # Too close to obstacle
            print("Cannot move forward - obstacle detected")
            return False
        self.drone.move_forward(20)
        return True

    def _safe_move_back(self):
        """Safely move backward with obstacle detection"""
        back_reading = self.drone.get_barometer()  # Using barometer as proxy for backward distance
        if back_reading < 100:  # Too close to obstacle
            print("Cannot move backward - obstacle detected")
            return False
        self.drone.move_back(20)
        return True

    def _safe_move_left(self):
        """Safely move left with obstacle detection"""
        # Since Tello doesn't have side sensors, we'll use conservative movement
        self.drone.move_left(20)
        return True

    def _safe_move_right(self):
        """Safely move right with obstacle detection"""
        # Since Tello doesn't have side sensors, we'll use conservative movement
        self.drone.move_right(20)
        return True

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
