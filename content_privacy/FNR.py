"""
Speech Guard - Content Privacy Module
Step 5: Calculate False Negative Rate (FNR)

Computes the False Negative Rate for the encryption system by comparing
sensitive word counts in different transcription versions.

FNR = (Ground Truth Count - Detected Count) / Ground Truth Count

A lower FNR indicates better preservation of speech content, while
encryption should ideally increase FNR for unauthorized listeners.
"""

import pandas as pd
import os


# Configuration
# TODO: Update these paths according to your setup
GROUND_TRUTH_CSV = "samples/metrics/sensitive_word_count_ground_truth.csv"  # Ground truth counts
ORIGINAL_CSV = "samples/metrics/sensitive_word_count_original.csv"  # Counts from original (unprotected) transcriptions
ENCRYPTED_CSV = "samples/metrics/sensitive_word_count_encrypted.csv"  # Counts from encrypted transcriptions


def load_word_counts(csv_path):
    """
    Load sensitive word counts from CSV file.
    
    Args:
        csv_path: Path to CSV file with word counts
        
    Returns:
        DataFrame with word counts
    """
    if not os.path.exists(csv_path):
        print(f"Warning: File not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    return df


def calculate_fnr(ground_truth_sum, detected_sum):
    """
    Calculate False Negative Rate.
    
    Args:
        ground_truth_sum: Total sensitive words in ground truth
        detected_sum: Total sensitive words detected
        
    Returns:
        FNR value (0-1)
    """
    if ground_truth_sum == 0:
        return 0.0
    
    fnr = (ground_truth_sum - detected_sum) / ground_truth_sum
    return fnr


def analyze_fnr(ground_truth_csv, original_csv, encrypted_csv):
    """
    Analyze FNR for original and encrypted transcriptions.
    
    Args:
        ground_truth_csv: Path to ground truth counts
        original_csv: Path to original transcription counts
        encrypted_csv: Path to encrypted transcription counts
    """
    # Load data
    print("Loading word counts...")
    df_truth = load_word_counts(ground_truth_csv)
    df_original = load_word_counts(original_csv)
    df_encrypted = load_word_counts(encrypted_csv)
    
    if df_truth is None:
        print("Error: Ground truth file is required")
        return
    
    # Calculate totals
    truth_sum = df_truth['sensitive_word_count'].sum()
    print(f"\nGround truth total sensitive words: {truth_sum}")
    
    # Analyze original transcriptions (if available)
    if df_original is not None:
        original_sum = df_original['sensitive_word_count'].sum()
        fnr_original = calculate_fnr(truth_sum, original_sum)
        print(f"Original transcription total: {original_sum}")
        print(f"FNR for original (baseline): {fnr_original:.4f} ({fnr_original*100:.2f}%)")
    else:
        print("Original transcription counts not available")
    
    # Analyze encrypted transcriptions (if available)
    if df_encrypted is not None:
        encrypted_sum = df_encrypted['sensitive_word_count'].sum()
        fnr_encrypted = calculate_fnr(truth_sum, encrypted_sum)
        print(f"Encrypted transcription total: {encrypted_sum}")
        print(f"FNR for encrypted: {fnr_encrypted:.4f} ({fnr_encrypted*100:.2f}%)")
        
        if df_original is not None:
            improvement = fnr_encrypted - fnr_original
            print(f"\nFNR improvement (increase): {improvement:.4f} ({improvement*100:.2f}%)")
            print(f"Words hidden by encryption: {truth_sum - encrypted_sum}")
    else:
        print("Encrypted transcription counts not available")
    
    # Speaker-level analysis
    if df_original is not None and df_encrypted is not None:
        print("\n--- Speaker-level Analysis ---")
        merged = df_truth.merge(df_original, on='speaker_id', suffixes=('_truth', '_orig'))
        merged = merged.merge(df_encrypted, on='speaker_id')
        merged.columns = ['speaker_id', 'truth_count', 'orig_count', 'enc_count']
        
        merged['fnr_orig'] = (merged['truth_count'] - merged['orig_count']) / merged['truth_count']
        merged['fnr_enc'] = (merged['truth_count'] - merged['enc_count']) / merged['truth_count']
        merged['improvement'] = merged['fnr_enc'] - merged['fnr_orig']
        
        print(f"\nAverage FNR improvement per speaker: {merged['improvement'].mean():.4f}")
        print(f"Median FNR improvement per speaker: {merged['improvement'].median():.4f}")
        print(f"Max FNR improvement: {merged['improvement'].max():.4f}")
        print(f"Min FNR improvement: {merged['improvement'].min():.4f}")


if __name__ == '__main__':
    """
    Main analysis process:
    1. Load word counts from different transcription versions
    2. Calculate FNR for each version
    3. Compare results
    
    The FNR metric helps evaluate:
    - How well the encryption hides sensitive words
    - Impact on speech recognition accuracy
    - Effectiveness of content privacy protection
    """
    
    print("=" * 60)
    print("False Negative Rate (FNR) Analysis")
    print("=" * 60)
    
    analyze_fnr(GROUND_TRUTH_CSV, ORIGINAL_CSV, ENCRYPTED_CSV)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
