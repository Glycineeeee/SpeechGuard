# Speech Guard

A comprehensive speech privacy protection system that provides both acoustic and content privacy for speech data.

## Overview

Speech Guard protects speech privacy through two complementary approaches:

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
Speech Guard
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

## Use Cases

### Acoustic Privacy

- **Anonymous Speech Sharing**: Share speech data without revealing speaker identity
- **Voice Conversion Research**: Protect speaker identities in research datasets
- **Privacy-Preserving ASR**: Train speech recognition without exposing identities
- **Voice Assistant Privacy**: Protect user voice characteristics

### Content Privacy

- **Sensitive Information Protection**: Encrypt names, numbers, addresses in recordings
- **Medical Privacy**: Protect patient information in medical recordings
- **Legal Compliance**: Meet data protection requirements (GDPR, HIPAA)
- **Secure Communication**: Selective encryption for multi-party conversations

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
Speech_Guard/
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
├── samples/                    # Example data (create as needed)
│   ├── 1/
│   ├── 2/
│   └── 3/
│
└── README.md                   # This file
```

## Configuration

Each module contains configuration variables at the top of each file. Update these according to your setup:

```python
# Example configuration (acoustic_privacy/ours-protect.py)
input_paths = [r"samples/original"]
output_path = r"samples/protected"
nb_proc = 2  # Number of parallel processes
```

All paths use generic "samples/" directories by default. Update to match your data locations.

## Performance

### Acoustic Privacy
- **Processing Speed**: ~0.5-2 seconds per utterance (depends on length)
- **Parallelization**: Multi-threaded processing supported
- **Memory**: Moderate (loads full utterances)

### Content Privacy
- **Encryption Speed**: Real-time or faster
- **Bottleneck**: Forced alignment (external MFA step)
- **Scalability**: Handles large datasets efficiently

## Evaluation Metrics

### Acoustic Privacy
- **Speaker Verification EER**: Measures identity protection
- **ASR WER**: Measures intelligibility preservation
- **Distortion Strength**: Measures transformation magnitude

### Content Privacy
- **False Negative Rate (FNR)**: Measures content protection
- **Word Error Rate (WER)**: Measures overall quality
- **Encryption Coverage**: Percentage of sensitive words protected

## Known Limitations

### Acoustic Privacy
- Requires parameter storage for recovery
- May affect prosody slightly
- Not effective against sophisticated speaker recognition with training data

### Content Privacy
- Requires accurate forced alignment
- Encrypted segments may affect ASR performance
- Key management must be handled securely in production

## Security Considerations

### Acoustic Privacy
- Parameters must be kept secret for privacy
- Transformation is deterministic (same parameters = same output)
- Multiple transformations can be chained for stronger protection

### Content Privacy
- Keys must be distributed securely
- Use proper key management in production (not plain text files)
- Consider additional authentication for key access
- Encrypted segments are identifiable by unusual acoustic properties

## Citation

If you use this code in your research, please cite:

```bibtex
@article{yourpaper,
  title={Speech Guard: Comprehensive Privacy Protection for Speech Data},
  author={Your Name},
  journal={Your Journal},
  year={2026}
}
```

## License

[Specify your license here]

## Contact

[Your contact information]

## Acknowledgments

This project uses:
- PyWorld for vocoder operations
- Montreal Forced Aligner for word-level alignment
- Cryptodome for encryption
- Various open-source Python libraries

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Submit a pull request

## Troubleshooting

### Common Issues

**Import errors for pyworld/soundfile:**
- These are optional for development
- Install with: `pip install pyworld soundfile`

**MFA not found (content privacy):**
- Install Montreal Forced Aligner separately
- See: https://montreal-forced-aligner.readthedocs.io/

**Audio format issues:**
- Install ffmpeg for audio conversion
- Ensure pydub can access ffmpeg

**Path errors:**
- Update configuration paths in each script
- Use absolute paths or ensure relative paths are correct
- Create necessary directories before running

For more issues, see module-specific README files.
