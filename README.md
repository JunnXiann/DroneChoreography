# Drone Choreography System

A real-time system that makes DJI Tello drones dance to music beats. The system detects beats from your computer's audio input and translates them into drone movements.

## Features
- Real-time beat detection using PyAudio
- Support for both simulated and real DJI Tello drones
- Customizable dance moves
- Safe drone control with error handling

## Requirements
- Python 3.11 or later
- PyAudio
- NumPy
- DJITelloPy (for real drone control)

## Installation
1. Install required packages:
```bash
pip install pyaudio numpy djitellopy
```

2. Clone this repository or download the source files

## Usage

### Simulation Mode (Default)
1. Navigate to the `src` directory
2. Run the main script:
```bash
python main.py
```
3. Play music near your microphone
4. Watch the simulated drone movements in the console
5. Press Ctrl+C to stop

### Real Drone Mode
1. Turn on your DJI Tello drone
2. Connect your computer to the drone's WiFi network
3. Edit `main.py` and change:
```python
drone = DroneController(simulation_mode=True)
```
to:
```python
drone = DroneController(simulation_mode=False)
```
4. Run the main script:
```bash
python main.py
```
5. Play music near your microphone
6. The drone will perform dance moves to the beats
7. Press Ctrl+C to safely land and stop

## Customizing the System

### Adding/Modifying Simulated Moves
In `drone_control.py`, find the `_perform_simulated_move()` method. The moves are defined in the `moves` list:
```python
moves = [
    (" Up 20cm", lambda: self._move_up(20)),
    (" Down 20cm", lambda: self._move_down(20)),
    (" Rotate Right", lambda: self._rotate(30)),
    # Add more moves here
]
```

### Adding/Modifying Real Drone Moves
In `drone_control.py`, find the `_perform_real_move()` method:
```python
def _perform_real_move(self):
    try:
        # Current moves
        self.drone.rotate_clockwise(90)
        time.sleep(0.5)
        self.drone.rotate_counter_clockwise(90)
        
        # Add more moves by uncommenting or adding new ones:
        # self.drone.flip_forward()
        # self.drone.move_up(20)
        # self.drone.move_down(20)
    except Exception as e:
        print(f"Dance move failed: {e}")
```

### Adjusting Beat Detection
In `music_beat_sync.py`, you can adjust these parameters:
- `energy_threshold`: Controls how sensitive the beat detection is (default: 0.01)
- `min_beat_interval`: Minimum time between beats in seconds (default: 0.2)

### Safety Features
- The system includes error handling for all drone operations
- Minimum intervals between moves to prevent overwhelming the drone
- Safe landing procedure when stopping
- Battery level check when connecting to real drone

## Contributing
Feel free to fork this repository and submit pull requests with your improvements!

## Safety Warning
When using a real drone:
1. Always operate in a spacious area
2. Keep a safe distance from the drone
3. Have the emergency land button ready (Ctrl+C)
4. Monitor the drone's battery level
5. Follow all local drone regulations