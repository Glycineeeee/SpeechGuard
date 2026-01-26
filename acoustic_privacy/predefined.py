"""
SpeechGuard - Acoustic Privacy Module
Common utility functions for speech signal processing and manipulation.
"""

import os
import glob
import pyworld
import soundfile as sf
import numpy as np
import queue
import tqdm
import threading
import scipy.integrate


def load_librispeech(input_paths):
    """
    Load LibriSpeech dataset structure from given paths.
    
    Args:
        input_paths: List of paths to LibriSpeech subsets
        
    Returns:
        Dictionary mapping speaker IDs to list of utterance tuples (subset_path, relative_path, None)
    """
    speakers = {}

    for subset_path in input_paths:
        # Remove trailing slash
        if subset_path[-1] == '/':
            subset_path = subset_path[:-1]

        if os.path.isdir(subset_path):
            for speaker_id in os.listdir(subset_path):
                speaker_path = os.path.join(subset_path, speaker_id)
                speaker_utterances = []

                if os.path.isdir(speaker_path):
                    for chapter in os.listdir(speaker_path):
                        chapter_path = os.path.join(speaker_path, chapter)

                        if os.path.isdir(chapter_path):
                            speaker_utterances.extend([(subset_path, os.path.relpath(p, subset_path), None)
                                                       for p in glob.glob(chapter_path + '/*.wav')])
                    speakers[speaker_id] = speaker_utterances

    return speakers


class Utterance:
    """
    Represents a speech utterance with acoustic features.
    
    Provides lazy loading of acoustic features (f0, spectrogram, aperiodicity, etc.)
    using PyWorld vocoder for speech signal decomposition.
    """

    def __init__(self, data, sample_rate, frame_length_in_ms=20, voiced_threshold_factor=0.06):
        """
        Initialize an Utterance instance.
        
        Args:
            data: Audio waveform data (numpy array)
            sample_rate: Sample rate in Hz
            frame_length_in_ms: Frame length for analysis in milliseconds (default: 20ms)
            voiced_threshold_factor: Threshold factor for voiced frame detection (default: 0.06)
        """
        self.data = data
        self.sample_rate = sample_rate
        self.frame_length_in_ms = frame_length_in_ms
        self.voiced_threshold_factor = voiced_threshold_factor

        self._f0 = None
        self._timeaxis = None
        self._spectrogram = None
        self._aperiodicity = None
        self._voiced_frames = None

    def save(self, path):
        """
        Save audio data to file.
        
        Args:
            path: Output file path
        """
        with open(path, mode='wb') as f:
            sf.write(f, self.data, self.sample_rate)

    @property
    def f0(self):
        """
        Fundamental frequency (F0) contour.
        Computed using HARVEST algorithm if not already cached.
        """
        if self._f0 is None:
            self._harvest()
        return self._f0

    @property
    def timeaxis(self):
        """Time axis for the acoustic features."""
        if self._timeaxis is None:
            self._harvest()
        return self._timeaxis

    @property
    def spectrogram(self):
        """
        Spectral envelope (spectrogram).
        Computed using CheapTrick algorithm.
        """
        if self._spectrogram is None:
            self._spectrogram = pyworld.cheaptrick(self.data, self.f0, self.timeaxis, self.sample_rate)
        return self._spectrogram

    @property
    def aperiodicity(self):
        """
        Aperiodicity measure for each frequency band.
        Computed using D4C algorithm.
        """
        if self._aperiodicity is None:
            self._aperiodicity = pyworld.d4c(self.data, self.f0, self.timeaxis, self.sample_rate)
        return self._aperiodicity

    @property
    def voiced_frames(self):
        """
        Indices of voiced frames in the utterance.
        Frames with energy above threshold are considered voiced.
        """
        if self._voiced_frames is None:
            self._voiced_frames = self._get_voiced_frames(self.spectrogram, self.voiced_threshold_factor)
        return self._voiced_frames

    def _harvest(self):
        """Extract F0 and time axis using HARVEST algorithm."""
        self._f0, self._timeaxis = pyworld.harvest(self.data, self.sample_rate, frame_period=self.frame_length_in_ms)

    def decompose(self):
        """
        Decompose the utterance into all acoustic features.
        Computes F0, spectrogram, and aperiodicity.
        """
        self._f0, self._timeaxis = pyworld.harvest(self.data, self.sample_rate, frame_period=self.frame_length_in_ms)
        self._spectrogram = pyworld.cheaptrick(self.data, self.f0, self.timeaxis, self.sample_rate)
        self._aperiodicity = pyworld.d4c(self.data, self.f0, self.timeaxis, self.sample_rate)

    @classmethod
    def _get_voiced_frames(cls, squared_magnitude_spectrogram, threshold_factor):
        """
        Detect voiced frames based on energy threshold.
        
        Args:
            squared_magnitude_spectrogram: Spectrogram with squared magnitudes
            threshold_factor: Factor to multiply mean energy for threshold
            
        Returns:
            Array of indices for voiced frames
        """
        energy = np.sum(squared_magnitude_spectrogram, axis=1)
        threshold = np.mean(energy) * threshold_factor
        return np.asarray(energy > threshold).nonzero()[0]
    

def load_utterance(path, frame_length_in_ms=20, voiced_threshold_factor=0.06, lazy=True):
    """
    Load an audio file and create an Utterance object.
    
    Args:
        path: Path to audio file
        frame_length_in_ms: Frame length in milliseconds (default: 20ms)
        voiced_threshold_factor: Threshold for voiced frame detection (default: 0.06)
        lazy: If True, defer acoustic feature extraction until accessed (default: True)
        
    Returns:
        Utterance object
    """
    with open(path, 'rb') as f:
        data, sample_rate = sf.read(f)

    utterance = Utterance(data, sample_rate,
                          frame_length_in_ms=frame_length_in_ms,
                          voiced_threshold_factor=voiced_threshold_factor)

    if not lazy:
        utterance.decompose()

    return utterance


def load_utterances_parallel(path_to_utterances, pool, desc='Load data'):
    """
    Load multiple utterances in parallel using a thread pool.
    
    Args:
        path_to_utterances: List of paths to audio files
        pool: ThreadPoolExecutor for parallel processing
        desc: Description for progress bar (default: 'Load data')
        
    Returns:
        List of Utterance objects
    """
    def update_progressbar(q, total):
        progress_bar = tqdm.tqdm(total=total, leave=False, desc=desc)
        while q.get():
            progress_bar.update()

    # Create a queue and a thread to display a progress bar
    q = queue.Queue()
    progress_thread = threading.Thread(target=update_progressbar, args=(q, len(path_to_utterances)))
    progress_thread.start()

    # Analyze the utterances in parallel using a thread pool
    utterances = list(pool.map(_get_utterance_data_wrapper, [(path, q) for path in path_to_utterances]))

    # Stop the progress bar thread
    q.put(None)
    progress_thread.join()

    return utterances


def _get_utterance_data_wrapper(args):
    """Wrapper function for parallel utterance loading."""
    path, q = args
    return _get_utterance_data(path, q)


def _get_utterance_data(path, q):
    """
    Load utterance and update progress queue.
    
    Args:
        path: Path to audio file
        q: Queue for progress tracking
        
    Returns:
        Utterance object
    """
    utt = load_utterance(path, lazy=False)
    q.put(1)  # Update progress bar
    return utt


def vtln_on_frame(frame, warping_fn):
    """
    Apply Vocal Tract Length Normalization (VTLN) to a single spectral frame.
    
    Args:
        frame: Spectral frame (frequency magnitudes)
        warping_fn: Frequency warping function
        
    Returns:
        Warped spectral frame
    """
    m = len(frame)
    omega = np.array([((i + 1) * np.pi) / m for i in range(m)])  # [PI/m, 2PI/m, ... PI]
    
    # Create interpolation function
    f = scipy.interpolate.interp1d(omega, frame, kind='linear', fill_value='extrapolate')

    # Apply warping function to frequency axis
    omega_warped = []
    for omega_i in omega:
        warped_i = warping_fn(omega_i)
        omega_warped.append(warped_i)
    
    return f(omega_warped)


def vtln_on_spectrogram(spectrogram, warping_fn):
    """
    Apply VTLN to an entire spectrogram.
    
    Args:
        spectrogram: 2D array of spectral frames
        warping_fn: Frequency warping function
        
    Returns:
        Warped spectrogram
    """
    warped_spectrogram = np.empty_like(spectrogram)
    
    for j, frame in enumerate(spectrogram):
        # Warp the frequencies for each frame in the spectrogram
        warped_frame = vtln_on_frame(frame, warping_fn)
        warped_spectrogram[j] = warped_frame
    
    return warped_spectrogram


def multi_linear_function(n, Alpha, Beta):
    """
    Create a multi-segment linear frequency warping function.
    
    Args:
        n: Number of internal control points
        Alpha: List of n frequency values in original domain [0, π]
        Beta: List of n frequency values in warped domain [0, π]
        
    Returns:
        Warping function that maps frequencies using piecewise linear interpolation
    """
    def f(omega):
        if not (len(Alpha) == len(Beta) == n):
            raise ValueError("Lengths of Alpha and Beta should be equal to n.")

        # Add boundary values (0 and π) to control points
        alpha_values = [0] + list(Alpha) + [np.pi]
        beta_values = [0] + list(Beta) + [np.pi]

        # Find the appropriate segment and apply linear interpolation
        for i in range(1, n + 2):
            if alpha_values[i - 1] <= omega <= alpha_values[i]:
                return ((beta_values[i] - beta_values[i - 1]) / 
                        (alpha_values[i] - alpha_values[i - 1])) * (omega - alpha_values[i]) + beta_values[i]

    return f


def re_multi_linear_function(n, Alpha, Beta):
    """
    Create an inverse multi-segment linear warping function.
    Swaps Alpha and Beta to create the inverse transformation.
    
    Args:
        n: Number of internal control points
        Alpha: List of n frequency values in original domain
        Beta: List of n frequency values in warped domain
        
    Returns:
        Inverse warping function
    """
    return multi_linear_function(n, Beta, Alpha)
    

def change_file_extension(audio_file_path, new_extension='.wav'):
    """
    Change file extension from .flac to specified extension.
    
    Args:
        audio_file_path: Original file path
        new_extension: New extension (default: '.wav')
        
    Returns:
        File path with new extension (unchanged if not .flac)
    """
    if audio_file_path.lower().endswith('.flac'):
        new_file_path = os.path.splitext(audio_file_path)[0] + new_extension
        return new_file_path
    else:
        return audio_file_path


def create_path_if_not_exists(file_path):
    """
    Create directory structure for file path if it doesn't exist.
    
    Args:
        file_path: Complete file path (including filename)
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
