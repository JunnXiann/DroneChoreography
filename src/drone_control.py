import time
from queue import Queue
import threading
import random
from djitellopy import Tello

class DroneController:
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode
        self.is_flying = False
        self.current_height = 0
        self.counter = 0
        self.last_command_time = 0
        self.min_command_interval = 1.0  # Minimum time between moves
        self.command_queue = []
        self.max_queue_size = 3  # Maximum number of queued moves
        
        if not simulation_mode:
            self.drone = Tello()
            
    def connect(self):
        """Connect to the drone"""
        if not self.simulation_mode:
            self.drone.connect()
            print("Connected to Tello drone")
        else:
            print("Drone connected (SIMULATION MODE)")
            
    def takeoff(self):
        """Take off the drone"""
        if not self.simulation_mode:
            self.drone.takeoff()
        else:
            print("Taking off... (SIMULATION MODE)")
            self.current_height = 100  # Initial height in cm
            
        self.is_flying = True
        print("Drone is airborne!")
        
    def land(self):
        """Land the drone"""
        if not self.simulation_mode:
            self.drone.land()
        else:
            print("Landing... (SIMULATION MODE)")
            self.current_height = 0
            
        self.is_flying = False
        print("Drone has landed")
        
    def perform_dance_move(self):
        """Queue a dance move to be performed"""
        if not self.is_flying:
            return
            
        current_time = time.time()
        
        # Add move to queue if not full
        if len(self.command_queue) < self.max_queue_size:
            self.command_queue.append(current_time)
            
            # If it's time for a new move, execute it
            if current_time - self.last_command_time >= self.min_command_interval:
                self._execute_next_move()
                
    def _execute_next_move(self):
        """Execute the next move in the queue"""
        if not self.command_queue:
            return
            
        # Update timing
        self.last_command_time = time.time()
        self.command_queue.pop(0)  # Remove executed move
        
        if self.simulation_mode:
            self._perform_simulated_move()
        else:
            self._perform_real_move()
            
    def _perform_simulated_move(self):
        """Execute a simulated dance move"""
        print("\n=== Simulated Drone Move ===")
        print(f"Move #{self.counter + 1} (Queue: {len(self.command_queue)})")
        
        if self.counter == 0:
            print(" Rotating 45° clockwise")
        elif self.counter == 1:
            print("  Moving forward 30cm")
        elif self.counter == 2:
            print("  Moving up 20cm")
            self.current_height += 20
            print(f"Current height: {self.current_height}cm")
        elif self.counter == 3:
            print("  Moving left 30cm")
            
        self.counter = (self.counter + 1) % 4
        if self.counter == 0:
            print("\n=== Dance Sequence Complete ===")
            
    def _perform_real_move(self):
        """Execute a real dance move"""
        try:
            if self.counter == 0:
                self.drone.rotate_clockwise(45)
            elif self.counter == 1:
                self.drone.move_forward(30)
            elif self.counter == 2:
                self.drone.move_up(20)
            elif self.counter == 3:
                self.drone.move_left(30)
                
            self.counter = (self.counter + 1) % 4
            
        except Exception as e:
            print(f"Error executing move: {e}")
