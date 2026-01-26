"""
SpeechGuard - Content Privacy Module
Step 4: Count Sensitive Word Occurrences

Counts how many times sensitive words appear in transcriptions.
Used to evaluate the False Negative Rate (FNR) of the encryption system.
"""

import csv
import os


# Configuration
# TODO: Update these paths according to your setup
TRANSCRIPTION_FILE = "samples/transcriptions/ground_truth.txt"  # Transcription file to analyze
SENSITIVE_WORDS_CSV = "samples/sensitive_words/selected_words.csv"  # CSV with sensitive words
OUTPUT_CSV = "samples/metrics/sensitive_word_count.csv"  # Output CSV with word counts


def load_sensitive_words(csv_path):
    """
    Load sensitive words for each speaker from CSV.
    
    Args:
        csv_path: Path to CSV file with sensitive words
        
    Returns:
        Dictionary mapping speaker_id to list of sensitive words (uppercase)
    """
    sensitive_words_dict = {}
    
    with open(csv_path, 'r', encoding='utf-8') as sensitive_file:
        sensitive_reader = csv.reader(sensitive_file)
        next(sensitive_reader)  # Skip header
        
        for row in sensitive_reader:
            speaker_id = row[0]
            # Store words in uppercase for case-insensitive matching
            words = [word.upper() for word in row[1].split()]
            sensitive_words_dict[speaker_id] = words
    
    return sensitive_words_dict


def load_speaker_transcriptions(file_path):
    """
    Load and organize transcriptions by speaker.
    
    Args:
        file_path: Path to transcription file
        
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
        speech = ' '.join(parts[1:]).upper()  # Convert to uppercase for matching
        
        # Check if current speaker changed
        if speaker_id != current_speaker:
            current_speaker = speaker_id
            speaker_lines[current_speaker] = []
        
        # Add speech to speaker's list
        speaker_lines[current_speaker].append(speech)
    
    return speaker_lines


def count_sensitive_words(speaker_lines, sensitive_words_dict):
    """
    Count occurrences of sensitive words for each speaker.
    
    Args:
        speaker_lines: Dictionary mapping speaker_id to list of speeches
        sensitive_words_dict: Dictionary mapping speaker_id to sensitive words
        
    Returns:
        Dictionary mapping speaker_id to count of sensitive word occurrences
    """
    word_counts = {}
    
    for speaker_id, speeches in speaker_lines.items():
        # Get sensitive words for this speaker
        sensitive_words = sensitive_words_dict.get(speaker_id, [])
        
        # Count occurrences of each sensitive word in all speeches
        count = 0
        for word in sensitive_words:
            for speech in speeches:
                count += speech.count(word)
        
        word_counts[speaker_id] = count
    
    return word_counts


def save_counts_to_csv(word_counts, output_path):
    """
    Save word counts to CSV file.
    
    Args:
        word_counts: Dictionary mapping speaker_id to word count
        output_path: Path to output CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write CSV header
        csv_writer.writerow(['speaker_id', 'sensitive_word_count'])
        
        # Write counts for each speaker
        for speaker_id, count in word_counts.items():
            csv_writer.writerow([speaker_id, count])


if __name__ == '__main__':
    """
    Main process:
    1. Load sensitive words from CSV
    2. Load transcriptions
    3. Count occurrences of sensitive words
    4. Save results to CSV
    
    This can be run on:
    - Ground truth transcriptions (to get baseline)
    - Transcriptions of encrypted audio (to measure FNR)
    - Transcriptions of recovered audio (to verify recovery)
    """
    
    print(f"Loading sensitive words from {SENSITIVE_WORDS_CSV}...")
    sensitive_words_dict = load_sensitive_words(SENSITIVE_WORDS_CSV)
    print(f"Loaded sensitive words for {len(sensitive_words_dict)} speakers")
    
    print(f"Loading transcriptions from {TRANSCRIPTION_FILE}...")
    speaker_lines = load_speaker_transcriptions(TRANSCRIPTION_FILE)
    print(f"Loaded transcriptions for {len(speaker_lines)} speakers")
    
    print("Counting sensitive word occurrences...")
    word_counts = count_sensitive_words(speaker_lines, sensitive_words_dict)
    
    # Calculate total
    total_count = sum(word_counts.values())
    print(f"Total sensitive word occurrences: {total_count}")
    
    print(f"Saving results to {OUTPUT_CSV}...")
    save_counts_to_csv(word_counts, OUTPUT_CSV)
    
    print("Done!")
