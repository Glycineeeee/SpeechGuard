"""
Speech Guard - Content Privacy Module
Step 3: Encrypt Sensitive Words in Audio

Encrypts sensitive word segments in audio files using AES encryption.
Each sensitive word segment is encrypted with a unique key, and keys are
distributed only to authorized speakers.
"""

from Cryptodome.Cipher import AES
from Crypto.Random import get_random_bytes
import wave
from pydub import AudioSegment
import os
import hashlib
import time


# Configuration
# TODO: Update these paths according to your setup
WORD_POSITIONS_FILE = "samples/word_positions/positions.txt"  # File with word positions
ORIGINAL_AUDIO_DIR = "samples/original_audio"  # Directory with original audio files
OUTPUT_DIR = "samples/encrypted_audio"  # Output directory for encrypted audio
KEYS_OUTPUT_DIR = "samples/encryption_keys"  # Output directory for encryption keys

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(KEYS_OUTPUT_DIR, exist_ok=True)


def convert_to_wav(audio_path, output_path):
    """
    Convert audio file to WAV format if needed.
    
    Args:
        audio_path: Path to input audio file
        output_path: Path to output WAV file
    """
    if not os.path.exists(output_path):
        audio = AudioSegment.from_file(audio_path)
        audio.export(output_path, format="wav")


def encrypt_audio_segment(file_id, start_time, end_time, speakers_dict):
    """
    Encrypt a specific time segment of an audio file.
    
    Args:
        file_id: Audio file identifier (format: speaker_id-chapter-utterance)
        start_time: Start time of segment in seconds
        end_time: End time of segment in seconds
        speakers_dict: Dictionary of speaker IDs to track
        
    Returns:
        Tuple of (encryption_key, encrypted successfully)
    """
    # Parse file path from file_id
    file_id_parts = file_id.split("-")
    speaker_id = file_id_parts[0]
    chapter_id = file_id_parts[1]
    
    # Find original audio file (supports .flac and .wav)
    audio_path = None
    for ext in ['.flac', '.wav']:
        potential_path = os.path.join(ORIGINAL_AUDIO_DIR, speaker_id, chapter_id, f"{file_id}{ext}")
        if os.path.exists(potential_path):
            audio_path = potential_path
            break
    
    if audio_path is None:
        print(f"Warning: Audio file not found for {file_id}")
        return None, False
    
    # Convert to WAV if needed
    wav_path = os.path.join(OUTPUT_DIR, f"{file_id}.wav")
    if not os.path.exists(wav_path):
        convert_to_wav(audio_path, wav_path)
    
    # Read WAV file
    with wave.open(wav_path, 'rb') as wav_file:
        params = wav_file.getparams()
        audio_data = wav_file.readframes(wav_file.getnframes())
    
    # Generate random encryption key
    password = get_random_bytes(100)
    key_hash = hashlib.md5(password).hexdigest()[:16]
    key = key_hash.encode()
    
    # Create AES cipher
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Calculate byte positions for encryption
    # Must be aligned to 16-byte blocks for AES
    bytes_per_sample = params.nchannels * params.sampwidth
    start_byte = round(params.framerate * start_time) * bytes_per_sample
    end_byte = round(params.framerate * end_time) * bytes_per_sample
    
    # Align to 16-byte blocks
    segment_length = end_byte - start_byte
    aligned_length = (segment_length // 16) * 16
    
    if aligned_length == 0:
        print(f"Warning: Segment too short to encrypt in {file_id}")
        return None, False
    
    # Encrypt the audio segment
    segment_to_encrypt = audio_data[start_byte:start_byte + aligned_length]
    encrypted_segment = cipher.encrypt(segment_to_encrypt)
    
    # Write encrypted audio file
    with wave.open(wav_path, 'wb') as encrypted_wav:
        encrypted_wav.setparams(params)
        encrypted_wav.writeframes(audio_data[:start_byte])
        encrypted_wav.writeframes(encrypted_segment)
        encrypted_wav.writeframes(audio_data[start_byte + aligned_length:])
    
    return key.decode(), True


def process_word_positions(positions_file, speakers_dict):
    """
    Process word positions file and encrypt each segment.
    
    Args:
        positions_file: Path to file with word positions
        speakers_dict: Dictionary mapping speaker_id to their key file path
    """
    start_time = time.time()
    
    # Initialize key files for each speaker
    key_files = {}
    for speaker_id, key_file_path in speakers_dict.items():
        key_files[speaker_id] = open(key_file_path, 'w', encoding='utf-8')
    
    try:
        with open(positions_file, 'r', encoding='utf-8') as pos_file:
            for line in pos_file:
                line = line.strip()
                if not line:
                    continue
                
                # Parse line: file_id word start_time end_time
                parts = line.split()
                if len(parts) < 4:
                    continue
                
                file_id = parts[0]
                word = parts[1]
                start_time_val = float(parts[2])
                end_time_val = float(parts[3])
                
                # Get speaker_id
                speaker_id = file_id.split('-')[0]
                
                # Encrypt segment
                key, success = encrypt_audio_segment(file_id, start_time_val, end_time_val, speakers_dict)
                
                if success and key:
                    # Write to key files
                    for spk_id, key_file in key_files.items():
                        if spk_id == speaker_id:
                            # Authorized speaker gets the key
                            key_file.write(f"{file_id} {start_time_val} {end_time_val} {key}\n")
                        else:
                            # Other speakers only get time ranges
                            key_file.write(f"{file_id} {start_time_val} {end_time_val}\n")
    
    finally:
        # Close all key files
        for key_file in key_files.values():
            key_file.close()
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")


def get_speakers_from_positions(positions_file):
    """
    Extract unique speaker IDs from positions file.
    
    Args:
        positions_file: Path to file with word positions
        
    Returns:
        Dictionary mapping speaker_id to key file path
    """
    speakers = set()
    
    with open(positions_file, 'r', encoding='utf-8') as pos_file:
        for line in pos_file:
            parts = line.strip().split()
            if parts:
                speaker_id = parts[0].split('-')[0]
                speakers.add(speaker_id)
    
    # Create key file paths for each speaker
    speakers_dict = {}
    for speaker_id in speakers:
        key_file_path = os.path.join(KEYS_OUTPUT_DIR, f"keys_for_{speaker_id}.txt")
        speakers_dict[speaker_id] = key_file_path
    
    return speakers_dict


if __name__ == '__main__':
    """
    Main encryption process:
    1. Extract speaker IDs from positions file
    2. Encrypt each sensitive word segment
    3. Distribute keys to authorized speakers
    """
    
    print("Extracting speaker information...")
    speakers_dict = get_speakers_from_positions(WORD_POSITIONS_FILE)
    print(f"Found {len(speakers_dict)} speakers")
    
    print("Encrypting sensitive word segments...")
    process_word_positions(WORD_POSITIONS_FILE, speakers_dict)
    
    print(f"Encrypted audio saved to {OUTPUT_DIR}")
    print(f"Encryption keys saved to {KEYS_OUTPUT_DIR}")
    print("Done!")