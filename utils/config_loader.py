# utils/config_loader.py

import configparser
import os

CONFIG_FILE_NAME = 'config.ini'
EXAMPLE_CONFIG_FILE_NAME = 'config.ini.example'
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')

DEFAULT_CONFIG = {
    'General': {
        'language': 'zh-CN',
        'wake_word_engine': 'porcupine',
        'wake_words': 'addy你好',
    },
    'Porcupine': {
        'access_key': '',
        'library_path': '',
        'model_path': '',
        'keyword_paths': '',
        'sensitivities': '0.5',
    },
    'Snowboy': {
        'snowboy_common_model': '',
        'snowboy_personal_model': '',
        'sensitivity': '0.5',
        'audio_gain': '1.0',
    },
    'AzureSpeech': {
        'speech_key': '',
        'service_region': '',
    },
    'TTS': {
        'tts_engine': 'pyttsx3',
        'pyttsx3_voice_id': '',
    },
    'Paths': {
        'log_file': 'addy_assistant.log',
    },
    'Miscellaneous': {
        'command_listen_timeout': '7',
        'command_phrase_limit': '7',
        'debug_mode': 'False',
    },
    'NLP': {
        'engine': 'rule_based',  # rule_based or llm
        'llm_service': 'openai' # openai, claude, tongyi, gemini, etc. (if engine is llm)
    },
    'LLM_Service': { # Generic LLM Service Configuration
        'api_type': 'openai', # Defines the API structure (e.g., openai, claude, tongyi, gemini)
        'api_key': '',
        'model': '',
        'api_base': '', # Optional: For self-hosted or proxy
        'api_secret': '', # Optional: For services like Tongyi
        'anthropic_version': '' # Optional: For Claude
    }
}

def get_config_path():
    """Returns the absolute path to the config.ini file."""
    return os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)

def get_example_config_path():
    """Returns the absolute path to the config.ini.example file."""
    return os.path.join(CONFIG_DIR, EXAMPLE_CONFIG_FILE_NAME)

def load_config():
    """Loads configuration from config.ini.
    If config.ini doesn't exist, it attempts to guide the user or uses defaults.
    """
    config_path = get_config_path()
    example_config_path = get_example_config_path()
    config = configparser.ConfigParser()

    # Apply defaults first
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in options.items():
            config.set(section, key, value)

    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR)
            print(f"Created config directory: {CONFIG_DIR}")
        except OSError as e:
            print(f"Error creating config directory {CONFIG_DIR}: {e}")
            # Proceed with defaults if directory creation fails
            return config 

    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
            print(f"Configuration loaded from: {config_path}")
        except configparser.Error as e:
            print(f"Error reading config file {config_path}: {e}. Using default values.")
            # Config remains default if read fails
        return config
    else:
        print(f"'{CONFIG_FILE_NAME}' not found in '{CONFIG_DIR}'.")
        if os.path.exists(example_config_path):
            print(f"An example configuration file exists at: {example_config_path}")
            print(f"Please copy it to '{CONFIG_FILE_NAME}' and customize it.")
        else:
            print(f"No example configuration ('{EXAMPLE_CONFIG_FILE_NAME}') found either.")
            print("Using default configuration values. Some features might not work without API keys.")
        # Optionally, create a default config.ini from example or defaults
        # For now, we'll just return the default config object
        return config

def get_llm_service_config(config):
    """Extracts LLM service configuration based on the 'NLP' section.

    Args:
        config: The loaded ConfigParser object.

    Returns:
        A dictionary containing the specific LLM service configuration
        (api_key, model, api_base, api_type, etc.) or None if not configured.
    """
    if not config.has_section('NLP') or not config.has_option('NLP', 'engine'):
        print("NLP engine type not specified in config.")
        return None

    nlp_engine = config.get('NLP', 'engine', fallback='rule_based').lower()
    if nlp_engine != 'llm':
        return None # Not using LLM

    if not config.has_section('LLM_Service'):
        print("LLM_Service section not found in config.")
        return None

    llm_config = dict(config.items('LLM_Service'))
    
    # Ensure essential keys are present, even if empty, to avoid KeyErrors later
    # api_type is crucial for the factory to know how to interpret other keys
    llm_config.setdefault('api_type', 'openai') 
    llm_config.setdefault('api_key', '')
    llm_config.setdefault('model', '')
    llm_config.setdefault('api_base', None) # None is better than empty string for optional URL
    llm_config.setdefault('api_secret', None)
    llm_config.setdefault('anthropic_version', None)

    return llm_config


# Example usage:
if __name__ == '__main__':
    print(f"Attempting to load configuration...")
    print(f"Expected config file location: {get_config_path()}")
    print(f"Example config file location: {get_example_config_path()}")
    
    cfg = load_config()

    print("\nLoaded Configuration (or defaults):")
    for section in cfg.sections():
        print(f"[{section}]")
        for key, value in cfg.items(section):
            print(f"  {key} = {value}")
    
    print("\nAccessing a specific value (e.g., General language):")
    print(f"General.language = {cfg.get('General', 'language', fallback=DEFAULT_CONFIG['General']['language'])}")
    print(f"Porcupine.access_key = {cfg.get('Porcupine', 'access_key', fallback=DEFAULT_CONFIG['Porcupine']['access_key'])}")
    print(f"Debug mode = {cfg.getboolean('Miscellaneous', 'debug_mode', fallback=DEFAULT_CONFIG['Miscellaneous']['debug_mode'] == 'True')}")

    # Test if config dir exists, if not, it means it was created or failed
    if not os.path.exists(CONFIG_DIR):
        print(f"\nConfig directory {CONFIG_DIR} was not found or could not be created.")
    elif not os.path.exists(get_config_path()):
         print(f"\n'{CONFIG_FILE_NAME}' was not found. Please create it from the example or run the main application to potentially generate one.")