# SpeechGuard

A comprehensive speech privacy protection system that provides both acoustic and content privacy for speech data.

## Overview

SpeechGuard protects speech privacy through two complementary approaches:

1. **Acoustic Privacy**: Protects speaker identity through frequency warping transformations
2. **Content Privacy**: Protects sensitive information by selectively encrypting specific words

## Modules

### Acoustic Privacy (`acoustic_privacy/`)

Protects speaker identity while maintaining speech intelligibility using Vocal Tract Length Normalization (VTLN) techniques.

**Features:**
- Random frequency warping transformations
- Configurable distortion strength
- Reversible with correct parameters
- Resistant to blind attacks

**Components:**
- `ours-protect.py`: Apply protection to original speech
- `ours-attack.py`: Simulate adversarial attacks
- `ours-recover.py`: Recover original speech with parameters
- `predefined.py`: Common utility functions

[See acoustic_privacy/README.md for details](acoustic_privacy/README.md)

### Content Privacy (`content_privacy/`)

Protects sensitive content by encrypting specific words in audio files using AES encryption.

**Features:**
- Selective word-level encryption
- Authorized key distribution
- Forced alignment-based localization
- Minimal impact on overall speech quality

**Components:**
- `select_sensitive_words.py`: Select words to protect
- `locate_words.py`: Find word positions in audio
- `encrypt_sensitive.py`: Encrypt sensitive segments
- `sensitive_numbers.py`: Count word occurrences
- `FNR.py`: Calculate privacy metrics

[See content_privacy/README.md for details](content_privacy/README.md)

## Quick Start

### Installation

```bash
# Install Python dependencies
pip install numpy scipy pyworld soundfile tqdm pandas
pip install pycryptodomex pydub textgrid

# For content privacy, also install:
# - ffmpeg (for audio processing)
# - Montreal Forced Aligner (for word alignment)
```

### Acoustic Privacy Example

```bash
cd acoustic_privacy

# Protect speech
python ours-protect.py

# Try to attack (without knowing parameters)
python ours-attack.py

# Recover with correct parameters
python ours-recover.py
```

### Content Privacy Example

```bash
cd content_privacy

# Step 1: Select sensitive words
python select_sensitive_words.py

# Step 2: Run MFA alignment (external tool)
# mfa align audio_dir lexicon.dict model.zip output_dir

# Step 3: Locate sensitive words
python locate_words.py

# Step 4: Encrypt sensitive segments
python encrypt_sensitive.py

# Step 5: Evaluate with FNR
python FNR.py
```

## System Architecture

```
SpeechGuard
│
├── Acoustic Privacy
│   ├── Input: Original speech
│   ├── Process: Frequency warping (VTLN)
│   ├── Output: Protected speech + parameters
│   └── Recovery: Inverse transformation
│
└── Content Privacy
    ├── Input: Original speech + transcriptions
    ├── Process: Word selection → Alignment → Encryption
    ├── Output: Encrypted audio + keys
    └── Evaluation: FNR analysis
```

## Technical Details

### Acoustic Privacy Technology

- **Method**: Multi-segment linear frequency warping (VTLN)
- **Parameters**: n control points, Alpha/Beta coordinates
- **Distortion**: Configurable strength (default: 0.5-0.6)
- **Reversibility**: Exact recovery with correct parameters
- **Processing**: PyWorld vocoder for speech decomposition/synthesis

### Content Privacy Technology

- **Encryption**: AES-128 in ECB mode
- **Alignment**: Montreal Forced Aligner (MFA)
- **Key Management**: Per-segment unique keys
- **Access Control**: Selective key distribution
- **Metric**: False Negative Rate (FNR)

## Requirements

### Core Requirements
```
numpy>=1.19.0
scipy>=1.5.0
pyworld>=0.3.0
soundfile>=0.10.0
tqdm>=4.50.0
pandas>=1.1.0
```

### Acoustic Privacy
```
pyworld  # For vocoder operations
```

### Content Privacy
```
pycryptodomex  # For AES encryption
pydub          # For audio format conversion
textgrid       # For MFA output parsing
ffmpeg         # Audio codec (system dependency)
```

### External Tools
```
montreal-forced-aligner  # For word-level alignment (content privacy)
```

## Project Structure

```
SpeechGuard/
├── acoustic_privacy/
│   ├── predefined.py           # Common utilities
│   ├── ours-protect.py         # Protection module
│   ├── ours-attack.py          # Attack simulation
│   ├── ours-recover.py         # Recovery module
│   └── README.md
│
├── content_privacy/
│   ├── select_sensitive_words.py  # Step 1: Word selection
│   ├── locate_words.py            # Step 2: Word localization
│   ├── encrypt_sensitive.py       # Step 3: Encryption
│   ├── sensitive_numbers.py       # Step 4: Word counting
│   ├── FNR.py                     # Step 5: FNR calculation
│   └── README.md
│
├── samples/                    # Example data
│   ├── 1/
│   ├── 2/
│   └── 3/
│
└── README.md                   # This file
```

## Citation

If you use this code in your research, please cite:

```bibtex
@article{zhang2025speechguard,
  title={SpeechGuard: Recoverable and Customizable Speech Privacy Protection},
  author={Zhang, Jingmiao and Liu, Suyuan and Hou, Jiahui and Wang, Zhiqiang and Yu, Haikuo and Li, Xiang-Yang},
  booktitle={34th USENIX Security Symposium (USENIX Security 25)},
  pages={5931--5948},
  year={2025}
}
```

## License

This project is released under the MIT License.

## Acknowledgments

This project uses:
- PyWorld for vocoder operations
- Montreal Forced Aligner for word-level alignment
- Cryptodome for encryption
- Various open-source Python libraries