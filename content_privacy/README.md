# Speech Guard - Content Privacy Protection

This module provides content privacy protection for speech by selectively encrypting sensitive words in audio files.

## Overview

The content privacy system protects sensitive information in speech while maintaining overall intelligibility. It works by:

1. Identifying sensitive words for each speaker
2. Locating these words in audio files using forced alignment
3. Encrypting only the audio segments containing sensitive words
4. Distributing decryption keys only to authorized speakers

## Pipeline

The system consists of 5 steps that should be executed in order:

### Step 1: Select Sensitive Words (`select_sensitive_words.py`)

Randomly selects sensitive words from each speaker's transcriptions.

```bash
python select_sensitive_words.py
```

**Input:**
- Transcription file with format: `speaker_id-chapter-utterance transcription`

**Output:**
- CSV file with selected sensitive words for each speaker

**Configuration:**
```python
TRANSCRIPTION_FILE = "samples/transcriptions/ground_truth.txt"
OUTPUT_CSV = "samples/sensitive_words/selected_words.csv"
NUM_WORDS_PER_SPEAKER = 5  # Number of words to select
```

### Step 2: Locate Words in Audio (`locate_words.py`)

Uses Montreal Forced Aligner (MFA) output to find exact time positions of sensitive words.

**Prerequisites:**
- Run MFA on your audio files to generate TextGrid files
- MFA command example:
  ```bash
  mfa align audio_dir lexicon.dict acoustic_model.zip output_dir
  ```

```bash
python locate_words.py
```

**Input:**
- CSV file with sensitive words (from Step 1)
- Directory with MFA TextGrid files

**Output:**
- Text file with word positions: `file_id word start_time end_time`

**Configuration:**
```python
SENSITIVE_WORDS_CSV = "samples/sensitive_words/selected_words.csv"
MFA_OUTPUT_DIR = "samples/mfa_output"
OUTPUT_FILE = "samples/word_positions/positions.txt"
```

### Step 3: Encrypt Sensitive Segments (`encrypt_sensitive.py`)

Encrypts audio segments containing sensitive words using AES encryption.

```bash
python encrypt_sensitive.py
```

**Input:**
- Word positions file (from Step 2)
- Original audio files

**Output:**
- Encrypted audio files (WAV format)
- Key files for each speaker (authorized speakers get decryption keys)

**Configuration:**
```python
WORD_POSITIONS_FILE = "samples/word_positions/positions.txt"
ORIGINAL_AUDIO_DIR = "samples/original_audio"
OUTPUT_DIR = "samples/encrypted_audio"
KEYS_OUTPUT_DIR = "samples/encryption_keys"
```

**Key Features:**
- Each sensitive word segment is encrypted with a unique random AES key
- Only the speaker who said the word receives the decryption key
- Other speakers can see that something was encrypted (time ranges) but cannot decrypt
- AES-ECB mode with 16-byte aligned encryption

### Step 4: Count Sensitive Words (`sensitive_numbers.py`)

Counts occurrences of sensitive words in transcriptions for evaluation.

```bash
python sensitive_numbers.py
```

Run this script on:
1. Ground truth transcriptions (baseline)
2. ASR transcriptions of original audio
3. ASR transcriptions of encrypted audio

**Input:**
- Transcription file
- CSV with sensitive words

**Output:**
- CSV with sensitive word counts per speaker

**Configuration:**
```python
TRANSCRIPTION_FILE = "samples/transcriptions/ground_truth.txt"
SENSITIVE_WORDS_CSV = "samples/sensitive_words/selected_words.csv"
OUTPUT_CSV = "samples/metrics/sensitive_word_count.csv"
```

### Step 5: Calculate FNR (`FNR.py`)

Calculates False Negative Rate to evaluate encryption effectiveness.

```bash
python FNR.py
```

**Input:**
- Word count CSVs from Step 4 (ground truth, original, encrypted)

**Output:**
- Console output with FNR analysis

**Configuration:**
```python
GROUND_TRUTH_CSV = "samples/metrics/sensitive_word_count_ground_truth.csv"
ORIGINAL_CSV = "samples/metrics/sensitive_word_count_original.csv"
ENCRYPTED_CSV = "samples/metrics/sensitive_word_count_encrypted.csv"
```

**Metrics:**
- **FNR (False Negative Rate)**: `(Ground Truth - Detected) / Ground Truth`
- Higher FNR for encrypted audio indicates better privacy protection
- FNR improvement shows how many sensitive words were hidden

## Complete Workflow

```bash
# Step 1: Select sensitive words from transcriptions
python select_sensitive_words.py

# Step 2: Run MFA to align audio (external tool)
# mfa align audio_dir lexicon.dict acoustic_model.zip output_dir

# Step 3: Locate sensitive words in aligned audio
python locate_words.py

# Step 4: Encrypt sensitive word segments
python encrypt_sensitive.py

# Step 5: Transcribe encrypted audio using ASR (external tool)
# Then count sensitive words
python sensitive_numbers.py

# Step 6: Calculate FNR to evaluate privacy protection
python FNR.py
```

## Technical Details

### Encryption Method

- **Algorithm**: AES-128 in ECB mode
- **Key Generation**: Random 100-byte password → MD5 hash → 16-byte key
- **Segment Alignment**: Audio segments are aligned to 16-byte boundaries for AES
- **Key Distribution**: Each speaker receives keys only for their own sensitive words

### Audio Processing

- **Input Formats**: FLAC, WAV (automatically converted)
- **Output Format**: WAV
- **Sampling**: Preserves original sample rate and bit depth
- **Frame Alignment**: Sample-accurate encryption based on forced alignment

### Privacy Model

The system implements a **selective disclosure** model:

- **Authorized Speaker**: Can decrypt their own sensitive words
- **Other Speakers**: Know something is encrypted but cannot access content
- **Attackers**: Cannot distinguish encrypted segments or access any keys

## Requirements

```
pycryptodomex
pydub
textgrid
pandas
```

For audio processing:
```
ffmpeg  # Required by pydub
```

For forced alignment (external):
```
montreal-forced-aligner (MFA)
```

## Directory Structure

```
content_privacy/
├── select_sensitive_words.py  # Step 1: Select sensitive words
├── locate_words.py            # Step 2: Locate words using MFA
├── encrypt_sensitive.py       # Step 3: Encrypt audio segments
├── sensitive_numbers.py       # Step 4: Count word occurrences
├── FNR.py                     # Step 5: Calculate FNR metric
└── README.md                  # This file

samples/
├── transcriptions/            # Input transcriptions
├── sensitive_words/           # Selected sensitive words (CSV)
├── mfa_output/                # MFA TextGrid files
├── word_positions/            # Word time positions
├── original_audio/            # Original audio files
├── encrypted_audio/           # Encrypted audio output
├── encryption_keys/           # Decryption keys for speakers
└── metrics/                   # Word counts and FNR results
```

## Example Data Format

### Transcription File
```
121-127105-0001 THIS IS A SAMPLE TRANSCRIPTION
121-127105-0002 ANOTHER SENTENCE WITH WORDS
```

### Sensitive Words CSV
```
speaker_id,sampled_words
121,SAMPLE TRANSCRIPTION WORDS SENTENCE ANOTHER
```

### Word Positions File
```
121-127105-0001 SAMPLE 1.23 1.56
121-127105-0001 TRANSCRIPTION 2.45 2.89
```

### Key File (for speaker 121)
```
121-127105-0001 1.23 1.56 a1b2c3d4e5f6g7h8
121-127105-0001 2.45 2.89 x9y8z7w6v5u4t3s2
```

### Key File (for other speakers)
```
121-127105-0001 1.23 1.56
121-127105-0001 2.45 2.89
```

## Evaluation Metrics

### False Negative Rate (FNR)

Measures how many sensitive words are NOT detected in transcriptions:

```
FNR = (Ground Truth Count - Detected Count) / Ground Truth Count
```

**Interpretation:**
- FNR = 0: All sensitive words detected (no privacy)
- FNR = 1: No sensitive words detected (perfect privacy, but may affect quality)
- Target: High FNR for encrypted audio, low FNR for authorized decryption

### Privacy-Utility Trade-off

- **Privacy**: Higher FNR for unauthorized listeners
- **Utility**: Low FNR for authorized listeners after decryption
- **Goal**: Maximize privacy while maintaining utility for authorized users

## Notes

- All audio files are automatically converted to WAV format if needed
- Encryption preserves all non-sensitive audio content
- The system creates necessary directories automatically
- Keys are stored in plain text files (use proper key management in production)
- Segment times are from forced alignment and sample-accurate

## Citation

If you use this code in your research, please cite the original paper.
