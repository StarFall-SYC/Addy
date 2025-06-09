# addy_core/wake_word_detector.py

import time
import struct
import pyaudio # Required for audio input stream in example

# Attempt to import pvporcupine, provide guidance if not found
try:
    import pvporcupine
except ImportError:
    pvporcupine = None
    print("pvporcupine library not found. Please install it (`pip install pvporcupine`) and ensure you have the necessary Porcupine model and keyword files.")

class WakeWordDetector:
    def __init__(self, access_key=None, keyword_paths=None, sensitivities=None, library_path=None, model_path=None):
        """Initializes the wake word detector using Porcupine.

        Args:
            access_key (str): AccessKey obtained from Picovoice Console (https://console.picovoice.ai/).
            keyword_paths (list[str]): Absolute paths to Porcupine keyword files (.ppn).
            sensitivities (list[float]): Sensitivities for each keyword. A higher sensitivity
                                       reduces miss rate at the cost of increased false alarm rate.
                                       Values should be between 0 and 1.
            library_path (str, optional): Absolute path to the Porcupine dynamic library.
                                          If not specified, the default library bundled with pvporcupine will be used.
            model_path (str, optional): Absolute path to the Porcupine model file (.pv).
                                       If not specified, the default model bundled with pvporcupine will be used.
        """
        self.access_key = access_key
        self.keyword_paths = keyword_paths
        self.sensitivities = sensitivities
        self.library_path = library_path
        self.model_path = model_path
        self.porcupine = None

        if not pvporcupine:
            print("Cannot initialize WakeWordDetector: pvporcupine library is not available.")
            return

        if not self.access_key:
            print("Cannot initialize WakeWordDetector: Porcupine AccessKey is required.")
            # In a real app, you might raise an error or handle this more gracefully
            return

        if not self.keyword_paths or not isinstance(self.keyword_paths, list) or not all(isinstance(p, str) for p in self.keyword_paths):
            print("Cannot initialize WakeWordDetector: `keyword_paths` must be a list of strings.")
            return

        if self.sensitivities is None:
            # Default sensitivity if not provided, one for each keyword path
            self.sensitivities = [0.5] * len(self.keyword_paths)
        elif not isinstance(self.sensitivities, list) or len(self.sensitivities) != len(self.keyword_paths) or not all(isinstance(s, float) for s in self.sensitivities):
            print("Cannot initialize WakeWordDetector: `sensitivities` must be a list of floats, matching the number of keyword_paths.")
            return

        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                library_path=self.library_path,
                model_path=self.model_path,
                keyword_paths=self.keyword_paths,
                sensitivities=self.sensitivities
            )
            print(f"Porcupine wake word engine initialized. Listening for: {self.keyword_paths}")
            print(f"Frame length: {self.porcupine.frame_length} samples, Sample rate: {self.porcupine.sample_rate} Hz")
        except pvporcupine.PorcupineError as e:
            print(f"Error initializing Porcupine: {e}")
            print("Please ensure you have a valid AccessKey and correct paths to keyword/model files.")
            self.porcupine = None
        except Exception as e:
            print(f"An unexpected error occurred during Porcupine initialization: {e}")
            self.porcupine = None

    def process(self, audio_frame):
        """
        Processes an audio frame to detect the wake word.
        An audio frame is a list/array of 16-bit integers (PCM data).
        The number of samples per frame must be `self.porcupine.frame_length`.
        The audio must be single-channel and have a sample rate of `self.porcupine.sample_rate`.

        Args:
            audio_frame (list[int]): A frame of audio samples.

        Returns:
            int: Index of the detected keyword, or -1 if no keyword is detected.
                 Returns -2 if Porcupine is not initialized.
        """
        if not self.porcupine:
            # print("Porcupine not initialized, cannot process audio.")
            return -2 # Indicate Porcupine not ready

        if len(audio_frame) != self.porcupine.frame_length:
            print(f"Error: Audio frame length ({len(audio_frame)}) does not match Porcupine's required frame length ({self.porcupine.frame_length}).")
            return -1

        try:
            return self.porcupine.process(audio_frame)
        except pvporcupine.PorcupineError as e:
            print(f"Error processing audio with Porcupine: {e}")
            return -1
        except Exception as e:
            print(f"An unexpected error occurred during Porcupine processing: {e}")
            return -1

    def delete(self):
        """Releases resources used by the wake word detector."""
        if self.porcupine:
            try:
                self.porcupine.delete()
                print("Porcupine resources released.")
            except Exception as e:
                print(f"Error releasing Porcupine resources: {e}")
            finally:
                self.porcupine = None
        else:
            print("Wake Word Detector (Porcupine not initialized or already deleted). No resources to release.")

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    # IMPORTANT: Replace with your actual AccessKey from Picovoice Console
    # Get your AccessKey from https://console.picovoice.ai/
    PICOVOICE_ACCESS_KEY = "YOUR_ACCESS_KEY_HERE" # <--- REPLACE THIS

    # IMPORTANT: Download Porcupine keyword files (.ppn) for your desired wake words.
    # You can use pre-built keywords (e.g., "porcupine", "bumblebee") or create custom ones on Picovoice Console.
    # Ensure these paths are correct.
    # Example: keyword_paths = [pvporcupine.KEYWORD_PATHS["porcupine"]]
    # Or for custom keywords: keyword_paths = ["path/to/your/custom_keyword.ppn"]
    keyword_names = ["porcupine"] # Example, can be any keyword you have a .ppn file for
    try:
        keyword_paths = [pvporcupine.KEYWORD_PATHS[kw] for kw in keyword_names]
    except KeyError as e:
        print(f"Could not find built-in keyword path for '{e}'. Please ensure the keyword name is correct or provide a direct path to your .ppn file.")
        print(f"Available built-in keywords: {list(pvporcupine.KEYWORD_PATHS.keys())}")
        keyword_paths = [] # Prevent crash if keyword not found
    except AttributeError:
        print("pvporcupine.KEYWORD_PATHS not available. This might happen if pvporcupine is not fully installed or an older version is used.")
        print("Please provide direct paths to your .ppn files.")
        keyword_paths = []

    if PICOVOICE_ACCESS_KEY == "YOUR_ACCESS_KEY_HERE":
        print("ERROR: Please replace 'YOUR_ACCESS_KEY_HERE' with your actual Picovoice AccessKey.")
        print("You can obtain an AccessKey from https://console.picovoice.ai/")
    elif not keyword_paths:
        print("ERROR: Keyword paths are not set. Please configure `keyword_paths` with paths to your .ppn files.")
    else:
        detector = WakeWordDetector(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=keyword_paths,
            sensitivities=[0.5] * len(keyword_paths) # Adjust sensitivities as needed
        )

        if detector.porcupine:
            pa = pyaudio.PyAudio()
            audio_stream = None
            try:
                audio_stream = pa.open(
                    rate=detector.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=detector.porcupine.frame_length
                )

                print(f"Listening for wake word(s): {keyword_names} (Ctrl+C to stop)...")

                while True:
                    pcm = audio_stream.read(detector.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * detector.porcupine.frame_length, pcm)
                    
                    keyword_index = detector.process(pcm)
                    if keyword_index >= 0:
                        print(f"Wake word '{keyword_names[keyword_index]}' detected!")
                        # Here you would typically trigger the next action, like ASR.
                        # For this example, we'll just print and continue listening.
                        # If you want to stop after first detection, add a break here.

            except KeyboardInterrupt:
                print("Stopping...")
            except Exception as e:
                print(f"An error occurred during audio streaming: {e}")
            finally:
                if audio_stream is not None:
                    audio_stream.close()
                pa.terminate()
                detector.delete()
        else:
            print("Failed to initialize Porcupine. Exiting example.")