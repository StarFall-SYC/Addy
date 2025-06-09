# addy_core/asr_module.py

import speech_recognition as sr
import time

# addy_core/asr_module.py

import speech_recognition as sr
import time
import io
import wave

# Configuration for ASR (can be moved to a config file later)
DEFAULT_LANGUAGE = 'zh-CN'  # Default language for speech recognition
DEFAULT_TIMEOUT = 5  # Seconds to wait for speech before timing out
DEFAULT_PHRASE_TIME_LIMIT = 10  # Max seconds for a single phrase
AMBIENT_NOISE_DURATION = 0.5  # Seconds to adjust for ambient noise
CONTINUOUS_LISTEN_TIMEOUT = 0.5 # Timeout for listen_continuous's listen call
CONTINUOUS_PHRASE_TIME_LIMIT = 5 # Max duration for a single phrase in continuous mode
CONTINUOUS_MAX_RECORD_SECONDS = 30 # Max total recording time in continuous mode
CONTINUOUS_SILENCE_THRESHOLD = 1 # Seconds of silence to consider speech ended

class ASRModule:
    def __init__(self, language=DEFAULT_LANGUAGE, recognizer_settings=None, asr_engine='google'):
        """Initializes the ASR module.

        Args:
            language (str): The language for speech recognition (e.g., 'en-US', 'zh-CN').
            recognizer_settings (dict, optional): Advanced settings for the recognizer.
                                                  Example: {'energy_threshold': 300, 'pause_threshold': 0.8}
            asr_engine (str): The ASR engine to use ('google', 'whisper', etc.). Placeholder for future.
        """
        self.recognizer = sr.Recognizer()
        self.microphone = None  # Initialize microphone only when needed
        self.language = language
        self.is_listening = False
        self.asr_engine = asr_engine # TODO: Implement engine switching

        if recognizer_settings and isinstance(recognizer_settings, dict):
            for key, value in recognizer_settings.items():
                if hasattr(self.recognizer, key):
                    setattr(self.recognizer, key, value)
                else:
                    print(f"ASR Warning: Invalid recognizer setting '{key}'.")

        print(f"ASR Module Initialized. Language: {self.language}. Engine: {self.asr_engine}.")
        if self.asr_engine == 'google':
            print("Note: Google Speech Recognition requires internet. Consider alternatives for offline/production use.")
        # TODO: Add initialization for other engines like Whisper

    def _initialize_microphone(self):
        """Initializes the microphone if not already done."""
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone()
                print("ASR: Microphone initialized.")
            except Exception as e:
                print(f"ASR Error: Failed to initialize microphone: {e}")
                self.microphone = None  # Ensure it's None if failed
                return False
        return True

    def listen_and_recognize(self, timeout=DEFAULT_TIMEOUT, phrase_time_limit=DEFAULT_PHRASE_TIME_LIMIT):
        """
        Listens for a single utterance from the microphone and transcribes it.

        Args:
            timeout (int): Seconds to wait for speech to start before timing out.
            phrase_time_limit (int): Maximum seconds a phrase can be.

        Returns:
            str or None: The transcribed text in lowercase, or None if recognition fails or times out.
        """
        if not self._initialize_microphone() or self.microphone is None:
            return None

        with self.microphone as source:
            if self.is_listening:
                print("ASR Warning: Already listening. Call ignored.")
                return None
            self.is_listening = True
            print("ASR: Adjusting for ambient noise...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
                print(f"ASR: Listening for command (timeout: {timeout}s, phrase limit: {phrase_time_limit}s)...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("ASR: No speech detected within timeout.")
                self.is_listening = False
                return None
            except Exception as e:
                print(f"ASR Error: Microphone listening error: {e}")
                self.is_listening = False
                return None
            finally:
                self.is_listening = False  # Ensure flag is reset

        print("ASR: Processing speech...")
        return self.recognize_audio_data(audio)

    def listen_continuous(self, 
                          max_record_seconds=CONTINUOUS_MAX_RECORD_SECONDS, 
                          silence_threshold=CONTINUOUS_SILENCE_THRESHOLD,
                          phrase_time_limit=CONTINUOUS_PHRASE_TIME_LIMIT):
        """
        Listens continuously after a wake word, accumulating audio until silence or max time.

        Args:
            max_record_seconds (int): Maximum total seconds to record after wake word.
            silence_threshold (float): Seconds of silence to consider the utterance finished.
            phrase_time_limit (int): Max duration for a single phrase chunk during listening.

        Returns:
            sr.AudioData or None: The accumulated audio data, or None if error.
        """
        if not self._initialize_microphone() or self.microphone is None:
            return None

        print(f"ASR: Continuous listening started. Max duration: {max_record_seconds}s, Silence threshold: {silence_threshold}s")
        
        audio_frames = []
        start_time = time.time()
        last_speech_time = start_time
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
            print("ASR: Listening for continuous input...")
            
            while True:
                current_time = time.time()
                if current_time - start_time > max_record_seconds:
                    print("ASR: Max recording time reached.")
                    break
                if current_time - last_speech_time > silence_threshold and audio_frames:
                    print("ASR: Silence detected, stopping continuous listen.")
                    break
                
                try:
                    # Listen for a short chunk of audio
                    audio_chunk = self.recognizer.listen(source, 
                                                         timeout=CONTINUOUS_LISTEN_TIMEOUT, 
                                                         phrase_time_limit=phrase_time_limit)
                    audio_frames.append(audio_chunk.get_raw_data())
                    last_speech_time = time.time() # Reset silence timer on speech
                    print(f"ASR: ... captured audio chunk ({len(audio_frames)} total) ...")
                except sr.WaitTimeoutError:
                    # This is expected if there's silence, continue checking silence_threshold
                    if not audio_frames and current_time - start_time > DEFAULT_TIMEOUT: # If no audio at all after default timeout
                        print("ASR: No speech detected in continuous mode after initial timeout.")
                        return None
                    pass 
                except Exception as e:
                    print(f"ASR Error during continuous listen: {e}")
                    return None
        
        if not audio_frames:
            print("ASR: No audio captured in continuous mode.")
            return None

        # Combine audio frames into a single AudioData object
        # Assuming microphone's sample rate and width are consistent
        frame_data = b''.join(audio_frames)
        combined_audio = sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
        print(f"ASR: Continuous listening finished. Total audio duration: {combined_audio.duration:.2f}s")
        return combined_audio

    def recognize_audio_data(self, audio_data):
        """
        Recognizes speech from an sr.AudioData instance using the configured engine.

        Args:
            audio_data (sr.AudioData): The audio data to transcribe.

        Returns:
            str or None: The transcribed text in lowercase, or None if recognition fails.
        """
        if not isinstance(audio_data, sr.AudioData):
            print("ASR Error: Invalid audio_data type. Expected sr.AudioData.")
            return None
        try:
            if self.asr_engine == 'google':
                text = self.recognizer.recognize_google(audio_data, language=self.language)
            # TODO: Add other ASR engines here
            # elif self.asr_engine == 'whisper':
            #     # Placeholder for Whisper integration (would require openai-whisper library)
            #     # model = whisper.load_model("base") # Or other model sizes
            #     # result = model.transcribe(audio_data.get_wav_data(), language=self.language)
            #     # text = result["text"]
            #     print("ASR: Whisper engine not yet implemented.")
            #     return None
            else:
                print(f"ASR Error: Unknown ASR engine '{self.asr_engine}'.")
                return None
            
            print(f"ASR: Recognized ({self.asr_engine}): '{text}'")
            return text.lower()
        except sr.UnknownValueError:
            print(f"ASR: {self.asr_engine.capitalize()} Speech Recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"ASR: {self.asr_engine.capitalize()} Speech Recognition request failed; {e}.")
            return None
        except Exception as e:
            print(f"ASR: Unexpected error during speech recognition with {self.asr_engine}: {e}")
            return None

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    print("Initializing ASR Module for testing...")
    asr = ASRModule(language='zh-CN') # Default engine is 'google'

    if not asr.microphone:
        print("ASR module could not initialize microphone. Microphone tests will be skipped.")

    print("\n--- Test Case 1: Standard Listen and Recognize (single utterance) ---")
    if asr.microphone:
        speak_now_prompt = f"Please speak a command (e.g., '你好世界'). Waiting for {DEFAULT_TIMEOUT}s..."
        print(speak_now_prompt)
        time.sleep(1)
        recognized_text = asr.listen_and_recognize()
        if recognized_text:
            print(f"--- You said (standard): '{recognized_text}' ---")
        else:
            print("--- No command recognized (standard). ---")
    else:
        print("Skipping standard microphone test.")

    print("\n--- Test Case 2: Continuous Listen and Recognize (simulating post-wake word) ---")
    if asr.microphone:
        print(f"Simulating continuous listening. Speak after this message. Max {CONTINUOUS_MAX_RECORD_SECONDS}s, silence {CONTINUOUS_SILENCE_THRESHOLD}s.")
        time.sleep(1) # Give user time to prepare
        
        continuous_audio = asr.listen_continuous()
        if continuous_audio:
            print("--- Continuous audio captured. Now recognizing... ---")
            recognized_continuous_text = asr.recognize_audio_data(continuous_audio)
            if recognized_continuous_text:
                print(f"--- You said (continuous): '{recognized_continuous_text}' ---")
            else:
                print("--- Could not recognize speech from continuous audio. ---")
        else:
            print("--- No audio captured in continuous listening test. ---")
    else:
        print("Skipping continuous microphone test.")

    print("\n--- Test Case 3: Recognizing from a pre-recorded audio file (conceptual) ---")
    # ... (existing test case for file recognition can remain, or be adapted)
    test_audio_file = None # Set to a path to a WAV file to test this
    if test_audio_file:
        try:
            with sr.AudioFile(test_audio_file) as source:
                print(f"Loading audio from file: {test_audio_file}")
                audio_data_from_file = asr.recognizer.record(source)
            print("Recognizing from loaded audio file...")
            recognized_from_file = asr.recognize_audio_data(audio_data_from_file)
            if recognized_from_file:
                print(f"--- Recognized from file: '{recognized_from_file}' ---")
            else:
                print("--- Could not recognize speech from file. ---")
        except FileNotFoundError:
            print(f"Test audio file '{test_audio_file}' not found. Skipping file recognition test.")
        except Exception as e:
            print(f"Error in file recognition test: {e}")
    else:
        print("No test audio file provided. Skipping file recognition test.")

    print("\nASR Module test finished.")
    print("If microphone tests were skipped or failed, ensure a microphone is connected and permissions are granted.")