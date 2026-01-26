"""
SpeechGuard - Content Privacy Module
Step 1: Select Sensitive Words

Randomly selects sensitive words from each speaker's transcriptions.
These words will later be encrypted in the audio to protect content privacy.
"""

import random
import csv
import os


# Configuration
# TODO: Update these paths according to your setup
TRANSCRIPTION_FILE = "samples/transcriptions/ground_truth.txt"  # File with speaker transcriptions (format: speaker_id-chapter-utterance transcription)
OUTPUT_CSV = "samples/sensitive_words/selected_words.csv"  # Output CSV file with selected sensitive words
NUM_WORDS_PER_SPEAKER = 5  # Number of sensitive words to select per speaker


def load_speaker_transcriptions(file_path):
    """
    Load and organize transcriptions by speaker.
    
    Args:
        file_path: Path to transcription file with format "speaker_id-chapter-utterance transcription"
        
    Returns:
        Dictionary mapping speaker_id to list of their speeches
    """
    speaker_lines = {}
    current_speaker = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    for line in lines:
        # Extract speaker_id and speech content
        parts = line.strip().split(' ')
        if not parts:
            continue
            
        speaker_id = parts[0].split('-')[0]
        speech = ' '.join(parts[1:])
        
        # Check if current speaker changed
        if speaker_id != current_speaker:
            current_speaker = speaker_id
            speaker_lines[current_speaker] = []
        
        # Add speech to speaker's list
        speaker_lines[current_speaker].append(speech)
    
    return speaker_lines


def select_sensitive_words(speaker_lines, num_words=5):
    """
    Randomly select sensitive words for each speaker.
    
    Args:
        speaker_lines: Dictionary mapping speaker_id to list of speeches
        num_words: Number of words to select per speaker
        
    Returns:
        Dictionary mapping speaker_id to list of selected sensitive words
    """
    sensitive_words = {}
    
    for speaker_id, speeches in speaker_lines.items():
        # Get unique words from all speeches
        unique_words = set(' '.join(speeches).split())
        
        # Randomly sample words (up to num_words)
        sampled_words = random.sample(unique_words, min(num_words, len(unique_words)))
        sensitive_words[speaker_id] = sampled_words
    
    return sensitive_words


def save_to_csv(sensitive_words, output_path):
    """
    Save selected sensitive words to CSV file.
    
    Args:
        sensitive_words: Dictionary mapping speaker_id to list of sensitive words
        output_path: Path to output CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write CSV header
        csv_writer.writerow(['speaker_id', 'sampled_words'])
        
        # Write sensitive words for each speaker
        for speaker_id, words in sensitive_words.items():
            csv_writer.writerow([speaker_id, ' '.join(words)])


if __name__ == '__main__':
    """
    Main process:
    1. Load speaker transcriptions
    2. Randomly select sensitive words for each speaker
    3. Save to CSV file
    """
    
    print("Loading transcriptions...")
    speaker_lines = load_speaker_transcriptions(TRANSCRIPTION_FILE)
    print(f"Loaded transcriptions for {len(speaker_lines)} speakers")
    
    print(f"Selecting {NUM_WORDS_PER_SPEAKER} sensitive words per speaker...")
    sensitive_words = select_sensitive_words(speaker_lines, NUM_WORDS_PER_SPEAKER)
    
    print(f"Saving results to {OUTPUT_CSV}...")
    save_to_csv(sensitive_words, OUTPUT_CSV)
    
    print("Done!")