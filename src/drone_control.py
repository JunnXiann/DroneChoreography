import time
from queue import Queue
import threading
import random
from djitellopy import Tello
import logging

class DroneController:
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode
        self.is_flying = False
        self.current_height = 0
        self.counter = 0
        self.last_command_time = 0
        self.min_command_interval = 0.1  # Minimum time between moves
        self.command_queue = []
        self.max_queue_size = 5  # Maximum number of queued moves
        self.logger = logging.getLogger(__name__)
        
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
        
    def perform_dance_move(self, drum_type='kick'):
        """Queue a dance move to be performed based on drum type"""
        if not self.is_flying:
            return
            
        current_time = time.time()
        print(f"\nQueuing dance move for {drum_type} (Queue size: {len(self.command_queue)})")
        
        # Add move to queue if not full
        if len(self.command_queue) < self.max_queue_size:
            self.command_queue.append((current_time, drum_type))
            print(f"Move added to queue. New size: {len(self.command_queue)}")
            
            # If it's time for a new move, execute it
            if current_time - self.last_command_time >= self.min_command_interval:
                print("Executing move...")
                self._execute_next_move()
                
    def _execute_next_move(self):
        """Execute the next move in the queue"""
        if not self.command_queue:
            return
            
        # Update timing and get drum type
        self.last_command_time, drum_type = self.command_queue.pop(0)
        
        if self.simulation_mode:
            self._perform_simulated_move(drum_type)
        else:
            self._perform_real_move(drum_type)
            
    def _get_moves_for_drum(self, drum_type):
        """Get appropriate moves for each drum type"""
        if drum_type == 'kick':
            return ['move_up', 'move_down']  # Vertical movements for bass drums
        elif drum_type == 'snare':
            return ['move_left', 'move_right']  # Horizontal movements for snare
        elif drum_type == 'hihat':
            return ['rotate_clockwise', 'rotate_counter_clockwise']  # Rotations for hi-hats
        elif drum_type == 'toms':
            return ['move_forward', 'move_back']  # Forward/back for toms
        else:
            return ['flip_forward', 'flip_back', 'flip_left', 'flip_right']  # Default flips
            
    def _perform_simulated_move(self, drum_type='kick'):
        """Execute a simulated dance move based on drum type"""
        try:
            print("\n=== Simulated Drone Move ===")
            # Get moves appropriate for this drum type
            possible_moves = self._get_moves_for_drum(drum_type)
            move = random.choice(possible_moves)
            
            # Randomly choose a distance or angle
            if 'rotate' in move:
                value = random.choice([45, 90, 180])
            else:
                value = random.choice([20, 30, 50])
            
            # Log and print the move
            print(f"Drum type: {drum_type.upper()}")
            print(f"Executing move: {move}")
            if 'flip' not in move:
                print(f"Value: {value}")
            self.logger.info(f"Simulated move for {drum_type}: {move} {'with value ' + str(value) if 'flip' not in move else ''}")
            
            # Simulate the move with clear visual feedback
            if move == 'rotate_clockwise':
                print(f" Rotating {value}° clockwise")
            elif move == 'rotate_counter_clockwise':
                print(f" Rotating {value}° counter-clockwise")
            elif move == 'move_forward':
                print(f" Moving forward {value}cm")
            elif move == 'move_back':
                print(f" Moving back {value}cm")
            elif move == 'move_left':
                print(f" Moving left {value}cm")
            elif move == 'move_right':
                print(f" Moving right {value}cm")
            elif move == 'move_up':
                print(f" Moving up {value}cm")
                self.current_height += value
            elif move == 'move_down':
                print(f" Moving down {value}cm")
                self.current_height = max(0, self.current_height - value)
            elif move == 'flip_forward':
                print(" Flipping forward")
            elif move == 'flip_back':
                print(" Flipping back")
            elif move == 'flip_left':
                print(" Flipping left")
            elif move == 'flip_right':
                print(" Flipping right")
            
            print(f"Current height: {self.current_height}cm")
            print("=== Move Complete ===\n")
            
        except Exception as e:
            print(f"Error simulating move: {e}")

    def _perform_real_move(self, drum_type='kick'):
        """Execute a real dance move based on drum type"""
        try:
            print("\n=== Real Drone Move ===")
            # Get moves appropriate for this drum type
            possible_moves = self._get_moves_for_drum(drum_type)
            move = random.choice(possible_moves)
            
            # Randomly choose a distance or angle
            if 'rotate' in move:
                value = random.choice([45, 90, 180])
            else:
                value = random.choice([20, 30, 50])
            
            # Log and print the move
            print(f"Drum type: {drum_type.upper()}")
            print(f"Executing move: {move}")
            if 'flip' not in move:
                print(f"Value: {value}")
            self.logger.info(f"Real drone move for {drum_type}: {move} {'with value ' + str(value) if 'flip' not in move else ''}")
            
            # Execute the move
            if move == 'rotate_clockwise':
                print(f" Rotating {value}° clockwise")
                self.drone.rotate_clockwise(value)
            elif move == 'rotate_counter_clockwise':
                print(f" Rotating {value}° counter-clockwise")
                self.drone.rotate_counter_clockwise(value)
            elif move == 'move_forward':
                print(f" Moving forward {value}cm")
                self.drone.move_forward(value)
            elif move == 'move_back':
                print(f" Moving back {value}cm")
                self.drone.move_back(value)
            elif move == 'move_left':
                print(f" Moving left {value}cm")
                self.drone.move_left(value)
            elif move == 'move_right':
                print(f" Moving right {value}cm")
                self.drone.move_right(value)
            elif move == 'move_up':
                print(f" Moving up {value}cm")
                self.drone.move_up(value)
            elif move == 'move_down':
                print(f" Moving down {value}cm")
                self.drone.move_down(value)
            elif move == 'flip_forward':
                print(" Flipping forward")
                self.drone.flip_forward()
            elif move == 'flip_back':
                print(" Flipping back")
                self.drone.flip_back()
            elif move == 'flip_left':
                print(" Flipping left")
                self.drone.flip_left()
            elif move == 'flip_right':
                print(" Flipping right")
                self.drone.flip_right()
            
            print("=== Move Complete ===\n")
            
        except Exception as e:
            print(f"Error executing move: {e}")
