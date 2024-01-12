# synth.py
import simpleaudio as sa
import numpy as np
import wave
import os
import logging

# Constants
SAMPLE_RATE = 44100  # Sampling rate in Hz
DURATION = 0.5       # Duration in seconds

# Define frequencies for one octave (add more as needed)
NOTE_FREQUENCIES = {
    "C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13,
    "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00,
    "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88
}


# At the beginning of synth_test_new.py, set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Function to load piano samples
def load_instrument_samples(sample_directory):
    try:
        samples = {}
        for note, freq in NOTE_FREQUENCIES.items():
            file_path = os.path.join(sample_directory, f"{freq:.2f}.wav")
            with wave.open(file_path, 'rb') as wave_file:
                frames = wave_file.readframes(wave_file.getnframes())
                samples[freq] = np.frombuffer(frames, dtype=np.int16) / (2**15)
        return samples
    except Exception as e:
        print(f"Error loading piano samples: {e}")
        return None

# Generate waveforms
def generate_waveform(freq, waveform_type='sine', duration=DURATION, adsr_params=None, delay_params=None, piano_samples=None, fm_params=None):
     # Initialize waveform to None or some default value
    logging.debug(f"Generating waveform: freq={freq}, type={waveform_type}")
    # Initialize waveform to sine by default
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    waveform = np.sin(2 * np.pi * freq * t)
    
    if waveform_type == 'piano':
        print("Piano samples in play_sound:", piano_samples)
        if freq in piano_samples:
            waveform = piano_samples[freq]
            sample_length = len(waveform) / SAMPLE_RATE
            if sample_length < duration:
                repeats = int(np.ceil(duration / sample_length))
                waveform = np.tile(waveform, repeats)[:int(SAMPLE_RATE * duration)]
            else:
                waveform = waveform[:int(SAMPLE_RATE * duration)]
        else:
            raise ValueError(f"No piano sample for frequency {freq}")
    elif waveform_type == 'flute':
        print("Flute samples in play_sound:", piano_samples)
        if freq in piano_samples:
            waveform = piano_samples[freq]
            sample_length = len(waveform) / SAMPLE_RATE
            if sample_length < duration:
                repeats = int(np.ceil(duration / sample_length))
                waveform = np.tile(waveform, repeats)[:int(SAMPLE_RATE * duration)]
            else:
                waveform = waveform[:int(SAMPLE_RATE * duration)]
        else:
            raise ValueError(f"No flute sample for frequency {freq}")
    elif waveform_type == 'trumpet':
        print("Trumpet samples in play_sound:", piano_samples)
        if freq in piano_samples:
            waveform = piano_samples[freq]
            sample_length = len(waveform) / SAMPLE_RATE
            if sample_length < duration:
                repeats = int(np.ceil(duration / sample_length))
                waveform = np.tile(waveform, repeats)[:int(SAMPLE_RATE * duration)]
            else:
                waveform = waveform[:int(SAMPLE_RATE * duration)]
        else:
            raise ValueError(f"No trumpet sample for frequency {freq}")
    elif waveform_type == 'fm':
        carrier_freq = freq
        if waveform_type == 'fm':
            if fm_params is None:
                fm_params = (220, 1)  # Default values for FM modulation
            modulator_freq, modulation_index = fm_params
            modulator = np.sin(2 * np.pi * modulator_freq * t)
            waveform = np.sin(2 * np.pi * freq * t + modulation_index * modulator)            
    else:
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        if waveform_type == 'sine':
            waveform = np.sin(2 * np.pi * freq * t)
        elif waveform_type == 'square':
            waveform = np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform_type == 'sine-square':
        # Placeholder for a trumpet-like sound synthesis
             waveform = np.sin(2 * np.pi * freq * t) * (np.sign(np.sin(2 * np.pi * freq * t)) + 1)    

    # Apply ADSR envelope if parameters are provided
    if adsr_params and waveform_type != 'piano':
        attack, decay, sustain, release = adsr_params
        waveform = apply_adsr_envelope(waveform, attack, decay, sustain, release)

    # Apply delay effect if parameters are provided
    if delay_params and waveform_type != 'piano':
        delay_time, feedback, mix = delay_params
        waveform = apply_delay(waveform, delay_time, feedback, mix)
        
    if waveform is None:
        logging.warning(f"Waveform type '{waveform_type}' not recognized. Returning silence.")
        waveform = np.zeros(int(SAMPLE_RATE * duration))  # Return silence if type not recognized    

    return waveform
# ADSR Envelope creation
def apply_adsr_envelope(waveform, attack, decay, sustain_level, release):
    # Ensure attack, decay, and release are non-zero to avoid divide-by-zero issues
    attack = max(attack, 1.0 / SAMPLE_RATE)
    decay = max(decay, 1.0 / SAMPLE_RATE)
    release = max(release, 1.0 / SAMPLE_RATE)

    # Calculate lengths of attack, decay, and release in samples
    attack_length = int(attack * SAMPLE_RATE)
    decay_length = int(decay * SAMPLE_RATE)
    release_length = int(release * SAMPLE_RATE)

    # Calculate the sustain length to make sure the envelope fits the waveform length
    sustain_length = len(waveform) - attack_length - decay_length - release_length
    if sustain_length < 0:
        sustain_length = 0
        release_length = len(waveform) - attack_length - decay_length
        if release_length < 0:
            decay_length = len(waveform) - attack_length
            if decay_length < 0:
                attack_length = len(waveform)
                decay_length = 0
            release_length = 0

    # Create the envelope
    envelope = np.concatenate([
        np.linspace(0, 1, attack_length),  # Attack
        np.linspace(1, sustain_level, decay_length),  # Decay
        np.ones(sustain_length) * sustain_level,  # Sustain
        np.linspace(sustain_level, 0, release_length)  # Release
    ])

    # Ensure the envelope is not longer than the waveform
    envelope = envelope[:len(waveform)]

    # Apply envelope to the waveform
    return waveform * envelope

# Delay Effect Function
def apply_delay(waveform, delay_time, feedback, mix):
    delay_samples = int(delay_time * SAMPLE_RATE)
    delayed_waveform = np.zeros(len(waveform) + delay_samples)
    delayed_waveform[:len(waveform)] = waveform

    for i in range(len(waveform)):
        delayed_waveform[i + delay_samples] += delayed_waveform[i] * feedback

    output = delayed_waveform[:len(waveform)] * mix + waveform * (1 - mix)
    return output


# Play waveform
def play_waveform(waveform):
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        audio = waveform * (2**15 - 1) / max_val
        audio = audio.astype(np.int16)
        play_obj = sa.play_buffer(audio, 1, 2, SAMPLE_RATE)
        play_obj.wait_done()
    else:
        # Handle the case where there is no sound to play
        print("No audio to play: waveform is silent.")

# Pre-generate waveforms for a set of frequencies
def pre_generate_waveforms(frequencies, waveform_type='sine', adsr=(0.01, 0.1, 0.7, 0.2), delay=(0, 0, 0)):
    waveforms = {}
    for freq in frequencies:
        waveform = generate_waveform(freq, waveform_type)
        waveform = apply_adsr_envelope(waveform, *adsr)
        waveform = apply_delay(waveform, *delay)
        waveforms[freq] = waveform
    return waveforms
