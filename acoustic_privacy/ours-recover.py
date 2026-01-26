"""
Speech Guard - Recovery Module
Recovers original speech from protected audio using stored parameters.
"""

import concurrent.futures
import os
import numpy as np
import tqdm
import time
import pandas as pd
import ast
import pyworld
import predefined


# Configuration
suffix = '-recover'
# TODO: Update these paths according to your setup
input_paths = [r"samples/protected"]  # Path to protected audio files
output_path = r"samples/recovered"  # Output path for recovered audio
csv_file_path = os.path.join(output_path, 'protection_params.csv')  # CSV file with protection parameters
nb_proc = 2  # Number of parallel processes


class Transformer():
    """
    Transformer for recovery: applies inverse transformations using known parameters.
    
    Uses the protection parameters stored in CSV to apply exact inverse transformations
    and recover the original speech.
    """

    def __init__(self) -> None:
        """Initialize the Transformer."""
        pass

    def transform(self, utterance, n, Alpha, Beta):
        """
        Transform an utterance by applying inverse frequency warping.
        
        Args:
            utterance: Input Utterance object (protected audio)
            n: Number of control points used in protection
            Alpha: Alpha parameters from protection
            Beta: Beta parameters from protection
            
        Returns:
            Recovered Utterance object
        """
        # Create inverse warping function by swapping Alpha and Beta
        re_multi_function = self.re_multi(n, Alpha, Beta)
        
        # Apply inverse warping to spectrogram
        new_spectrogram = predefined.vtln_on_spectrogram(utterance.spectrogram, re_multi_function)

        # Synthesize audio from recovered spectrogram
        new_data = pyworld.synthesize(utterance.f0, new_spectrogram,
                                      utterance.aperiodicity, utterance.sample_rate, utterance.frame_length_in_ms)

        return predefined.Utterance(new_data, utterance.sample_rate)

    @staticmethod
    def re_multi(n, Alpha, Beta):
        """
        Create an inverse multi-linear warping function.
        
        Args:
            n: Number of control points
            Alpha, Beta: Control point coordinates
            
        Returns:
            Inverse warping function
        """
        def f(omega):
            return predefined.re_multi_linear_function(n, Alpha, Beta)(omega)
        return f
    

if __name__ == '__main__':
    """
    Main recovery process:
    1. Load protected audio files
    2. Read protection parameters from CSV
    3. Apply inverse transformations to recover original audio
    """

    paths = predefined.load_librispeech(input_paths)

    # Load protection parameters from CSV
    df = pd.read_csv(csv_file_path)

    sum_time = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=nb_proc) as pool:

        for spk_id in tqdm.tqdm(paths):

            # Load utterances from current speaker
            path_to_utterances = paths[spk_id]
            utterances = predefined.load_utterances_parallel(
                [os.path.join(subset, path) for subset, path, _ in path_to_utterances],
                pool, desc='Step 1/2: Load data')
            
            # Create the transformer
            transformer = Transformer()

            start_time = time.time()

            for (input_subset, path, dialog_id), original_utt in tqdm.tqdm(
                    zip(path_to_utterances, utterances),
                    total=len(utterances), desc='Step 2/2: Recovery conversion'):
                
                # Read parameters for this audio file from CSV
                real_path = os.path.join(input_subset, path)
                result_row = df[df['AudioFilePath'] == real_path]
                
                if not result_row.empty:
                    # Parse parameters from CSV
                    n = result_row['n'].values[0]
                    Alpha = ast.literal_eval(result_row['Alpha'].values[0])
                    Alpha = [Alpha] if isinstance(Alpha, (int, float)) else Alpha
                    Beta = ast.literal_eval(result_row['Beta'].values[0])
                    Beta = [Beta] if isinstance(Beta, (int, float)) else Beta
                else:
                    print(f"Warning: Parameters not found for {real_path}")
                    continue

                # Prepare output path
                output_subset = input_subset.split(os.sep)[-1] + suffix
                os.makedirs(os.path.join(output_path, output_subset, *path.split('/')[:-1]), exist_ok=True)

                # Apply recovery transformation
                transformed_utt = transformer.transform(original_utt, n, Alpha, Beta)
                
                # Save recovered audio
                wav_path = os.path.join(output_path, output_subset, path)
                predefined.create_path_if_not_exists(wav_path)
                transformed_utt.save(wav_path)

            end_time = time.time()
            sum_time += end_time - start_time

    print(f"Total execution time: {sum_time:.2f} seconds")