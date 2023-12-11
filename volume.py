import pyaudio
import audioop
import math
import time
import threading
# Constants
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Single channel for microphone
RATE = 44100  # Sample rate

# Initialize PyAudio
audio = pyaudio.PyAudio()
# Open the stream for the microphone
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
# Define your time interval (in seconds)
interval = 0.1
# Compute the number of frames based on the interval
frames_per_interval = int(RATE * interval)

volume = 0
lock = threading.Lock()
def sample_loop():
    global volume
    while True:
        # Use a stream to continuously read data
        # Read a chunk of data
        data = stream.read(frames_per_interval, exception_on_overflow=False)
        
        # Compute the RMS value
        rms = audioop.rms(data, 2)
        with lock:
            volume = 20 * math.log10(rms) if rms > 0 else -math.inf
        time.sleep(interval)

def get_volume():
    global volume
    
    with lock:
        ret = volume
    return ret

thread = threading.Thread(target=sample_loop)
# Start the thread
thread.start()
# Stop and close the stream
# stream.stop_stream()
# stream.close()
# audio.terminate()