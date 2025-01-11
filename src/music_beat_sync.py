import librosa

class BeatSynchronizer:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_beats(self):
        """
        Analyzes the music file and returns a list of beat timestamps.
        """
        # Load the audio file
        print("Loading audio file...")
        y, sr = librosa.load(self.file_path)

        # Detect tempo and beats
        print("Detecting beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        print(f"Detected tempo: {tempo:.2f} BPM")
        return beat_times
