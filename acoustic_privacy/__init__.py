"""
SpeechGuard - Acoustic Privacy Module

This module provides acoustic privacy protection through frequency warping transformations.
"""

from .predefined import (
    Utterance,
    load_utterance,
    load_utterances_parallel,
    load_librispeech,
    vtln_on_frame,
    vtln_on_spectrogram,
    multi_linear_function,
    re_multi_linear_function,
    change_file_extension,
    create_path_if_not_exists,
)

__version__ = '1.0.0'
__all__ = [
    'Utterance',
    'load_utterance',
    'load_utterances_parallel',
    'load_librispeech',
    'vtln_on_frame',
    'vtln_on_spectrogram',
    'multi_linear_function',
    're_multi_linear_function',
    'change_file_extension',
    'create_path_if_not_exists',
]
