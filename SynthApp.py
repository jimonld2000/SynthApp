# projectGui.py
import tkinter as tk
import tkinter.messagebox
import threading
import time
from synth import pre_generate_waveforms, play_waveform, generate_waveform, load_instrument_samples, DURATION, NOTE_FREQUENCIES

# GUI Application

# Define frequencies for one octave
WHITE_KEYS = ["C", "D", "E", "F", "G", "A", "B"]
BLACK_KEYS = ["C#", "D#", "F#", "G#", "A#"]
NOTE_FREQUENCIES = {  # Octave frequencies
    "C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13,
    "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00,
    "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88
}



# GUI Application
class SynthApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SynthSim")
        self.geometry('1000x300')  # Adjust the size as needed

        # Pre-generate waveforms for each note and waveform type
        self.waveforms = {waveform: pre_generate_waveforms(NOTE_FREQUENCIES.values(), waveform) 
                          for waveform in ["sine", "sine-square", "square"]}

        # Create piano keys
        self.create_piano_keys()

        # Create sound effects options
        self.create_sound_effects()

        # Create a text entry for the note progression with a default message
        self.note_entry = tk.Entry(self)
        self.note_entry.insert(0, 'Insert notes to play progression')
        self.note_entry.place(x=0, y=200, width=200)

        # Bind the focus_in event to clear the default text
        self.note_entry.bind("<FocusIn>", self.clear_text)

        # Bind the focus_out event to stop taking input
        self.note_entry.bind("<FocusOut>", self.stop_input)

        # Bind the keyboard to the note_entry widget
        self.bind_keyboard(self.note_entry)

        # Create a button to play the note progression
        self.play_button = tk.Button(self, text="Play", command=self.play_progression)
        self.play_button.place(x=210, y=200)
        
         # FM Synthesis Parameters
        self.fm_mod_freq = tk.DoubleVar(value=220)  # Default modulator frequency
        self.fm_mod_index = tk.DoubleVar(value=1)   # Default modulation index

        # FM Controls
        fm_mod_freq_slider = tk.Scale(self, from_=0, to=1000, resolution=1, orient='horizontal', variable=self.fm_mod_freq, label="FM Mod Freq")
        fm_mod_freq_slider.place(x=475, y=180)

        fm_mod_index_slider = tk.Scale(self, from_=0, to=10, resolution=0.1, orient='horizontal', variable=self.fm_mod_index, label="FM Mod Ind")
        fm_mod_index_slider.place(x=580, y=180)


    def create_piano_keys(self):
        white_key_width = 100  # Width of the white keys
        black_key_width = white_key_width / 2  # Width of the black keys
        white_key_index = 0

        # Create white keys with labels positioned lower
        for key in WHITE_KEYS:
            freq = NOTE_FREQUENCIES[key]
            btn = tk.Button(self, text=key, bg='white', fg='black', anchor='s',
                            command=lambda f=freq: self.play_sound(f))
            btn.place(x=white_key_index * white_key_width, y=0,
                      width=white_key_width, height=180)
            white_key_index += 1

        # Create black keys with visible labels
        black_key_index = 0
        for key in BLACK_KEYS:
            freq = NOTE_FREQUENCIES[key]
            btn = tk.Button(self, text=key, bg='black', fg='white', 
                            command=lambda f=freq: self.play_sound(f))
            # Offset each black key to be between the white keys
            offset = (white_key_width - black_key_width) / 2
            btn.place(x=offset + black_key_index * white_key_width, y=0,
                      width=black_key_width, height=120)
            black_key_index += 1
            if key == "D#":  # Skip the gap between E and F
                black_key_index += 1

    def create_sound_effects(self):
        self.effect_var = tk.StringVar(value="sine")
        effects_frame = tk.Frame(self)
        effects_frame.place(x=0, y=180)  # Position the effects below the keys
        effects = ["sine", "square", "sine-square", "flute", "piano", "trumpet", "fm"]  # Add more as needed
        for effect in effects:
            rb = tk.Radiobutton(effects_frame, text=effect, variable=self.effect_var, value=effect)
            rb.pack(side=tk.LEFT)
        # ADSR controls
        self.adsr_values = {
            'attack': tk.DoubleVar(value=0.01),
            'decay': tk.DoubleVar(value=0.1),
            'sustain': tk.DoubleVar(value=0.7),
            'release': tk.DoubleVar(value=0.2)
        }
        for i, (name, var) in enumerate(self.adsr_values.items()):
            tk.Label(self, text=name).place(x=800, y=30*i)
            tk.Scale(self, from_=0, to=1, resolution=0.01, orient='horizontal', variable=var).place(x=850, y=30*i)

        # Delay controls
        self.delay_values = {
            'time': tk.DoubleVar(value=0),
            'feedback': tk.DoubleVar(value=0),
            'mix': tk.DoubleVar(value=0)
        }
        for i, (name, var) in enumerate(self.delay_values.items()):
            tk.Label(self, text=name).place(x=800, y=120+30*i)
            tk.Scale(self, from_=0, to=1, resolution=0.01, orient='horizontal', variable=var).place(x=850, y=120+30*i)    

    # Inside the SynthApp class in projectGui.py

    def play_sound(self, freq):
       # waveform_type = self.effect_var.get()
        waveform_type =  self.effect_var.get()  
        adsr_params = (
            self.adsr_values['attack'].get(),
            self.adsr_values['decay'].get(),
            self.adsr_values['sustain'].get(),
            self.adsr_values['release'].get()
        )
        delay_params = (
            self.delay_values['time'].get(),
            self.delay_values['feedback'].get(),
            self.delay_values['mix'].get()
        )
        duration = DURATION  # Make sure this matches the duration used in synth.py

          # Handle piano samples separately
        if waveform_type == 'piano':
            waveform = generate_waveform(freq, waveform_type, piano_samples=load_instrument_samples('samples\\piano'))
        elif waveform_type == 'flute':
            waveform = generate_waveform(freq, waveform_type, piano_samples=load_instrument_samples('samples\\flute'))
        elif waveform_type == 'trumpet':
            waveform = generate_waveform(freq, waveform_type, piano_samples=load_instrument_samples('samples\\trumpet')) 
        elif waveform_type == 'fm':
            fm_params = (self.fm_mod_freq.get(), self.fm_mod_index.get())
            waveform = generate_waveform(freq, waveform_type, duration=DURATION, adsr_params=adsr_params, fm_params=fm_params)                        
        else:
            waveform = generate_waveform(freq, waveform_type, duration=DURATION,
                                        adsr_params=adsr_params, delay_params=delay_params)

        threading.Thread(target=lambda: play_waveform(waveform)).start()
    def bind_keyboard(self, widget):
        keyboard_to_piano = {
            'a': 'C', 'w': 'C#', 's': 'D', 'e': 'D#', 'd': 'E', 'f': 'F', 't': 'F#',
            'g': 'G', 'y': 'G#', 'h': 'A', 'u': 'A#', 'j': 'B'
        }
        for key, note in keyboard_to_piano.items():
            self.bind(f"<KeyPress-{key}>", lambda event, f=NOTE_FREQUENCIES[note]: self.play_sound(f))    
    
    def clear_text(self, event):
        # Clear the text in the entry when it receives focus
        self.note_entry.delete(0, 'end')

    def stop_input(self, event):
        # Unbind the key press events when the entry loses focus
        self.note_entry.unbind("<KeyPress>")

                     
    def play_progression(self):
        # Get the note progression from the entry
        progression = self.note_entry.get().split()

        # Validate all the notes before playing
        for note in progression:
            # Check if the note is valid
            if note not in NOTE_FREQUENCIES:
                # If not, show an error message and return
                tkinter.messagebox.showerror("Error", "Illegal note inserted. Please respect the musical notations")
                return

        # Play each note in the progression
        for note in progression:
            # If the note is valid, play it
            self.play_sound(NOTE_FREQUENCIES[note])

            # Pause for a short duration before playing the next note
            time.sleep(0.5)  # Adjust this value as needed       

if __name__ == "__main__":
    app = SynthApp()
    app.mainloop()
