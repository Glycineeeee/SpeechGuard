"""
SpeechGuard - Content Privacy Module
Step 2: Locate Sensitive Words in Audio

Locates sensitive words in audio files using Montreal Forced Aligner (MFA) output.
Creates a file with word positions (start and end times) for encryption.
"""

import textgrid
import os
import csv
import time


# Configuration
# TODO: Update these paths according to your setup
SENSITIVE_WORDS_CSV = "samples/sensitive_words/selected_words.csv"  # CSV with selected sensitive words
MFA_OUTPUT_DIR = "samples/mfa_output"  # Directory containing MFA TextGrid files
OUTPUT_FILE = "samples/word_positions/positions.txt"  # Output file with word positions


def get_textgrid_files(root_dir, suffix=".TextGrid"):
    """
    Recursively find all TextGrid files in directory.
    
    Args:
        root_dir: Root directory to search
        suffix: File suffix to match (default: .TextGrid)
        
    Returns:
        List of paths to TextGrid files
    """
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(suffix):
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    return file_list


def load_sensitive_words(csv_path):
    """
    Load sensitive words for each speaker from CSV.
    
    Args:
        csv_path: Path to CSV file with sensitive words
        
    Returns:
        Dictionary mapping speaker_id to list of sensitive words (lowercase)
    """
    sensitive_words_dict = {}
    
    with open(csv_path, 'r', encoding='utf-8') as sensitive_file:
        sensitive_reader = csv.reader(sensitive_file)
        next(sensitive_reader)  # Skip header
        
        for row in sensitive_reader:
            speaker_id = row[0]
            words = [word.lower() for word in row[1].split()]
            sensitive_words_dict[speaker_id] = words
    
    return sensitive_words_dict


def locate_words_in_textgrids(textgrid_files, sensitive_words_dict, output_file):
    """
    Locate sensitive words in TextGrid files and save positions.
    
    Args:
        textgrid_files: List of paths to TextGrid files
        sensitive_words_dict: Dictionary mapping speaker_id to sensitive words
        output_file: Path to output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for grid_path in textgrid_files:
            # Extract file_id and speaker_id from path
            # Assumes format: speaker_id-chapter-utterance.TextGrid
            file_id = os.path.basename(grid_path)[:-9]  # Remove .TextGrid
            speaker_id = file_id.split('-')[0]
            
            # Get sensitive words for this speaker
            sensitive_words = sensitive_words_dict.get(speaker_id, [])
            if not sensitive_words:
                continue
            
            # Read TextGrid file
            try:
                tg = textgrid.TextGrid.fromFile(grid_path)
            except Exception as e:
                print(f"Error reading {grid_path}: {e}")
                continue
            
            # Locate sensitive words in the word tier (usually tier 0)
            for item in tg[0]:
                if item.mark.lower() in sensitive_words:
                    # Write: file_id word start_time end_time
                    out_file.write(f"{file_id} {item.mark} {item.minTime} {item.maxTime}\n")
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")


if __name__ == '__main__':
    """
    Main process:
    1. Load sensitive words from CSV
    2. Find all TextGrid files from MFA output
    3. Locate sensitive words and save positions
    """
    
    print("Loading sensitive words...")
    sensitive_words_dict = load_sensitive_words(SENSITIVE_WORDS_CSV)
    print(f"Loaded sensitive words for {len(sensitive_words_dict)} speakers")
    
    print("Finding TextGrid files...")
    textgrid_files = get_textgrid_files(MFA_OUTPUT_DIR)
    print(f"Found {len(textgrid_files)} TextGrid files")
    
    print("Locating sensitive words...")
    locate_words_in_textgrids(textgrid_files, sensitive_words_dict, OUTPUT_FILE)
    
    print(f"Word positions saved to {OUTPUT_FILE}")
    print("Done!")