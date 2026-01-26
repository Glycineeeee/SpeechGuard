"""
Speech Guard - Protection Module
Applies acoustic privacy protection to speech signals using frequency warping.
"""

import concurrent.futures
import os
import random
import numpy as np
import tqdm
import csv
import time
import scipy.integrate
import predefined


# Configuration
suffix = 'ours-protect'
# TODO: Update these paths according to your setup
input_paths = [r"samples/original"]  # Path to original audio files
output_path = r"samples/protected"  # Output path for protected audio
csv_file_path = os.path.join(output_path, 'protection_params.csv')  # CSV file to save protection parameters
nb_proc = 2  # Number of parallel processes


class Transformer():
    """
    Transformer for protection: applies frequency warping to protect speech identity.
    
    Generates random warping parameters within a specified distortion range
    to transform the acoustic characteristics while maintaining intelligibility.
    """

    def __init__(self, distortion_range=(0.5, 0.6)) -> None:
        """
        Initialize the Transformer.
        
        Args:
            distortion_range: Tuple of (min, max) distortion strength
        """
        self.distortion_range = distortion_range

    def transform(self, utterance):
        """
        Transform an utterance by applying frequency warping protection.
        
        Args:
            utterance: Input Utterance object
            
        Returns:
            Tuple of (n, Alpha, Beta, transformed_utterance)
        """
        # Randomly select number of control points
        n = random.randint(1, 10)  # n in [1, 10]

        # Generate random warping parameters within distortion range
        while True:
            Alpha = [val * np.pi for val in self.generate_unique_values(n)]
            Beta = [val * np.pi for val in self.generate_unique_values(n)]

            multi_function = self.multi(n, Alpha, Beta)
            dist_strength = self.distortion_strength(multi_function)
        
            if self.distortion_range[0] <= dist_strength <= self.distortion_range[1]:
                break

        # Apply frequency warping to spectrogram
        new_spectrogram = predefined.vtln_on_spectrogram(utterance.spectrogram, multi_function)

        # Synthesize new audio from modified spectrogram
        import pyworld
        new_data = pyworld.synthesize(utterance.f0, new_spectrogram,
                                      utterance.aperiodicity, utterance.sample_rate, utterance.frame_length_in_ms)

        return n, Alpha, Beta, predefined.Utterance(new_data, utterance.sample_rate)

    @staticmethod
    def generate_unique_values(n):
        """
        Generate n unique random values between 0.25 and 1.
        
        Args:
            n: Number of values to generate
            
        Returns:
            Sorted list of n unique values
        """
        values = set()
        while len(values) < n:
            values.add(random.uniform(0.25, 1))
        return sorted(list(values))

    @staticmethod
    def multi(n, Alpha, Beta):
        """
        Create a multi-linear warping function.
        
        Args:
            n: Number of control points
            Alpha, Beta: Control point coordinates
            
        Returns:
            Warping function
        """
        def f(omega):
            return predefined.multi_linear_function(n, Alpha, Beta)(omega)
        return f
    
    @staticmethod
    def distortion_strength(f):
        """
        Compute distortion strength as integral of |f(x) - x| over [0, π].
        
        Args:
            f: Warping function
            
        Returns:
            Distortion strength value
        """
        return scipy.integrate.quad(lambda x: abs(f(x) - x), 0, np.pi)[0]


if __name__ == '__main__':
    """
    Main protection process:
    1. Load original audio files
    2. Apply frequency warping protection
    3. Save protected audio and parameters to CSV
    """

    paths = predefined.load_librispeech(input_paths)
    print("Number of speakers:", len(paths))

    # Create output directory and CSV file
    os.makedirs(output_path, exist_ok=True)
    csv_file = open(csv_file_path, mode='w', newline='')
    fieldnames = ['AudioFilePath', 'n', 'Alpha', 'Beta']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

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
                    total=len(utterances), desc='Step 2/2: Protection conversion'):
                
                # Prepare output path
                output_subset = input_subset.split(os.sep)[-1] + '_' + suffix
                os.makedirs(os.path.join(output_path, output_subset, *path.split('/')[:-1]), exist_ok=True)
                
                # Apply protection transformation
                n, Alpha, Beta, transformed_utt = transformer.transform(original_utt)
                
                # Save protected audio
                audio_file_path = os.path.join(output_path, output_subset, path)
                wav_path = predefined.change_file_extension(audio_file_path)
                predefined.create_path_if_not_exists(wav_path)
                transformed_utt.save(wav_path)

                # Write parameters to CSV
                alpha_str = ",".join(map(str, Alpha))
                beta_str = ",".join(map(str, Beta))
                writer.writerow({'AudioFilePath': wav_path, 'n': n, 'Alpha': alpha_str, 'Beta': beta_str})

            end_time = time.time()
            sum_time += end_time - start_time

    csv_file.close()

    print(f"Total execution time: {sum_time:.2f} seconds")