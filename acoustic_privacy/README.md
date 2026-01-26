# Speech Guard - Acoustic Privacy Protection

This module provides acoustic privacy protection for speech signals using frequency warping techniques.

## Overview

The system consists of three main components:

1. **Protection** (`ours-protect.py`): Applies frequency warping to protect speaker identity while maintaining speech intelligibility
2. **Attack** (`ours-attack.py`): Simulates an adversary attempting to recover protected speech without knowing the true parameters
3. **Recovery** (`ours-recover.py`): Recovers original speech using the stored protection parameters

## Architecture

### Core Module (`predefined.py`)

Contains common utility functions shared across all components:

- **Utterance Class**: Represents speech with lazy-loaded acoustic features (F0, spectrogram, aperiodicity)
- **Audio I/O**: Load/save audio files with parallel processing support
- **VTLN Functions**: Vocal Tract Length Normalization for frequency warping
- **Warping Functions**: Multi-segment linear frequency transformation functions

### Protection Module (`ours-protect.py`)

Protects speech by applying random frequency warping within a specified distortion range:

```python
# Configure paths
input_paths = [r"samples/original"]
output_path = r"samples/protected"
```

**Key Features:**
- Random parameter generation (1-10 control points)
- Distortion strength control (default: 0.5-0.6)
- Saves protection parameters to CSV for recovery

### Attack Module (`ours-attack.py`)

Simulates an adversary who doesn't know the protection parameters:

```python
# Configure paths
input_paths = [r"samples/protected"]
output_path = r"samples/attack"
```

**Key Features:**
- Guesses random inverse transformations
- Tests effectiveness of protection against blind attacks
- Records attempted parameters

### Recovery Module (`ours-recover.py`)

Recovers original speech using stored parameters:

```python
# Configure paths
input_paths = [r"samples/protected"]
output_path = r"samples/recovered"
csv_file_path = os.path.join(output_path, 'protection_params.csv')
```

**Key Features:**
- Reads parameters from CSV
- Applies exact inverse transformations
- Achieves near-perfect recovery

## Usage

### 1. Protect Speech

```bash
python ours-protect.py
```

This will:
- Load audio from `input_paths`
- Apply frequency warping protection
- Save protected audio to `output_path`
- Save parameters to CSV

### 2. Attempt Attack (Optional)

```bash
python ours-attack.py
```

This simulates an adversary trying to recover the speech without knowing the parameters.

### 3. Recover Original Speech

```bash
python ours-recover.py
```

This recovers the original speech using the saved parameters from the CSV file.

## Configuration

Before running, update the paths in each file:

- `input_paths`: List of directories containing audio files
- `output_path`: Directory for output files
- `csv_file_path`: Path to CSV file for storing/reading parameters
- `nb_proc`: Number of parallel processes (default: 2)

## Requirements

```
numpy
scipy
pyworld
soundfile
tqdm
pandas
```

## Technical Details

### Frequency Warping

The system uses piecewise linear frequency warping:

- **Control Points**: 1-10 randomly selected points in [0, π]
- **Alpha**: Original frequency positions
- **Beta**: Warped frequency positions
- **Distortion Strength**: Integral of |f(x) - x| over [0, π]

### Acoustic Features

Speech is decomposed using PyWorld vocoder:

- **F0**: Fundamental frequency (HARVEST algorithm)
- **Spectrogram**: Spectral envelope (CheapTrick algorithm)
- **Aperiodicity**: Aperiodic components (D4C algorithm)

Only the spectrogram is warped; F0 and aperiodicity remain unchanged to preserve prosody.

## File Structure

```
acoustic_privacy/
├── predefined.py          # Common utility functions
├── ours-protect.py        # Protection module
├── ours-attack.py         # Attack simulation module
├── ours-recover.py        # Recovery module
└── README.md              # This file
```

## Notes

- All audio files should be in WAV format (FLAC files are automatically converted)
- The system creates necessary directories automatically
- Processing time is logged for each speaker
- Parameters are stored in CSV format for easy inspection

## Citation

If you use this code in your research, please cite the original paper.
