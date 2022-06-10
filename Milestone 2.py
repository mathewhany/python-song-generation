'''
We import Python modules that we are going to use in our program
(numpy) is used to do all calculations required to construct the signals
(matplotlib.pyplot) is used to plot the sound signal
(sounddevice) is used to play the sound signal

Added for milestone 2:
(fft from scipy.fftpack) to get the fourier transform of our song
'''
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

'''
We store frequencies of piano notes in variables so we can easily
access them by their names.
'''
c = 130.81
d = 146.83
e = 164.81
f = 174.61
g = 196
a = 220
b = 246.93

'''
We will also use the variable (rest) to indicate any silence periods in the
song. It is simply a note with frequency equal to zero, which is the same as
a constant signal with amplitude 0.
'''
rest = 0


# The song's duration (How song the long will be?)
song_duration_in_sec = 3   

'''
In music, time is measured by beats. In particular, the number of beats per 
minutes (BPM). The higher the number the faster the song. We will store the 
number of beats per minute and calculate how long a beat will be using the 
formula => Beat Duration In Seconds = 60 Seconds / Beats Per Minute
'''
beats_per_minute = 140
beat_duration_in_seconds = 60 / beats_per_minute

'''
Each beat in music is broken down into smaller units, a whole note takes
the duration of a whole beat, a half note takes half the duration of single 
beat, a quarter note takes quarter the duration of a single beat and so on.

For most basic songs, its enough to just use whole, half and quarter notes, 
so we will calculate these here and store them for later use.
'''
whole  = beat_duration_in_seconds
half = beat_duration_in_seconds / 2
quarter = beat_duration_in_seconds / 4


'''
We will generate an array for the time-axis, starting from 0 up to song's 
duration, and we will divide it into 12 * 1024 equal parts which represent 
the number of samples.
'''
t = np.linspace(0, song_duration_in_sec, 12 * 1024)

'''
A function that takes a frequency and generates 2 sin wave signals,
one for the given frequency and another for double that frequency. (In music
doubling the frequency results in the same note but at the next octave)

We add the two sin waves together to have a signal for the note we want to play.
'''
def note(freq):
    octave1 = freq
    octave2 = octave1 * 2
    
    note1 = np.sin(2 * np.pi * octave1 * t)
    note2 = np.sin(2 * np.pi * octave2 * t)
    
    return note1 + note2

'''
A function that takes an array of arrays, the outer array represent the whole
song, the inner arraies represent each single note, the frequency of a note 
as the first item, and the duration of the note as the second item.

For example [ [c, quarter], [d, whole] ] is a song that has 2 notes,
C playeWd for quarter beat,
D played for a whole beat

Steps:
1. Create an accumulator where we add the signals to construct the song
2. Create a variable to store the time when the next note should start playing.
   It is initially set to 0 because the first note should start at time 0.
3. Loop over the notes and for each note:
    1. Extract the note's frequency and duration from the array and store 
    them in variables.
    2. Generates a sin wave signal using the (note) helper function above.
    3. Generate a pulse function (difference between 2 unit step functions),
       The pulse will be from (Start of Next Note) till (Next Note Start + Duration)
    4. Add the note's duration to the (Start of Next Note) variable so that
       The next note starts after the current note. Also add a little bit of 
       delay (Quarter note / 4) so that notes will have some silence in between.
    5. Multiply the sin wave signal by the pulse to get a sin wave signal that
       starts at the correct time and last for the note's duration.
    6. Add the note's signal to the accumulator.

4. Return the final song.
'''
def generate_song(notes):
    song = 0
    next_note_start = 0
    for current_note in notes:
        freq = current_note[0]
        duration = current_note[1]
        pulse = (t >= next_note_start) & (t <= next_note_start + duration)
        next_note_start += duration + quarter / 4
        song += note(freq) * pulse
    return song
    


'''
Here we store the song that we want to play in an array of arrays,
each inner array represent a single note, and each single note will have
a freqency at index 0, and a duration at index 1. The notes will be played
one after another.
'''
pirates_of_the_caribbean = [
   # We divide the note's freqency by 2 to get the same note in a lower octave
   [a / 2, quarter], 
   [c, quarter],
   [d, quarter],
   [rest, quarter],
   [d, quarter],
   [rest, quarter],
   
   [d, quarter],
   [e, quarter],
   [f, quarter],
   [rest, quarter],
   [f, quarter],
   [rest, quarter],
   
   [f, quarter],
   [g, quarter],
   [e, quarter],
   [rest, quarter],
   [e, quarter],
   [rest, quarter],
   
   [d, quarter],
   [c, quarter],
   [c, quarter],
   [d, quarter]
]


# Finally we call our method to generate the song
song_t = generate_song(pirates_of_the_caribbean)



#### Milestone 2 : Noise Cancellation ####


# We define the number of samples (Song Duration * 1024) and generate 
# our freqencies axis to range from 0 to 512.
N = 3 * 1024
f = np.linspace(0, 512, int(N/2))

# We use fast fourier transform (fft) to convert our song from the time domain
# to freqency domain.
song_f = fft(song_t)
song_f = 2 / N * np.abs(song_f[0:int(N/2)])

# We generate 2 random frequencies in our range from 0 to 512, they will
# be used as noise.
rand_noise_freq_1, rand_noise_freq_2 = np.random.randint(0, 512, 2)

# We use the 2 random frequences to construct our noise signal
noise = np.sin(2 * np.pi * rand_noise_freq_1 * t) + np.sin(2 * np.pi * rand_noise_freq_2 * t)

# Next we add the noise to our original song
song_with_noise_t = song_t + noise

# Next we convert our song with the added noise from time domain to freqency domain.
song_with_noise_f = fft(song_with_noise_t)
song_with_noise_f = 2 / N * np.abs(song_with_noise_f[0:int(N / 2)])


### In the next steps, we try to remove the noise that we have added ###

# We find the max frequency magnitude from the frequency domain of our original 
# song's without noise, and we round it up to the next integer
max_freq_mag = int(np.ceil(np.max(song_f)))

# Next, in the freqency domain of our song with added noise, we get the indices
# of all the freqencies that are greater than the max freqency 
# in our original song. These will be the indices of our noise freqencies.

(noise_freqs,) = np.where(song_with_noise_f > max_freq_mag)

# Next we loop on the the indices of the noises and for each one:
# we get the corresponding freqency from the freqencies axis (f), 
# we then round the freqency to integer values (since we generated only integer
# noise freqencies), then we construct a sin wave for the noise and add it to
# an accumulator.
noise_cancel = 0
for i in noise_freqs:
    noise_freq = f[i]
    noise_cancel += np.sin(2 * np.pi * np.round(noise_freq) * t)
    
    
# The accumulator (noise_cancel) now contains the noise signal, we subtract it
# from our song with noise to get our original song without noise.    
song_after_noise_cancel_t = song_with_noise_t - noise_cancel

# We convert our filtered song (that is now without noise) from time domain to
# freqency domain.
song_after_noise_cancel_f = fft(song_after_noise_cancel_t)
song_after_noise_cancel_f = 2 / N * np.abs(song_after_noise_cancel_f[0:int(N/2)])

# Then we plot our signals

# First figure for time domain plots
plt.figure(1)

# Song without noise in time domain
plt.subplot(3, 1, 1)
plt.plot(t, song_t)

# Song with noise in time domain
plt.subplot(3, 1, 2)
plt.plot(t, song_with_noise_t)

# Song after removing noise in time domain
plt.subplot(3, 1, 3)
plt.plot(t, song_after_noise_cancel_t)

# Second figure for freqency domain plots
plt.figure(2)

# Song without noise in freqency domain
plt.subplot(3, 1, 1)
plt.plot(f, song_f)

# Song with noise in freqency domain
plt.subplot(3, 1, 2)
plt.plot(f, song_with_noise_f)

# Song after removing noise in freqency domain
plt.subplot(3, 1, 3)
plt.plot(f, song_after_noise_cancel_f)

# Show both figures
plt.show()

# We play our song after removing the noise to make sure we get the original
# song without any noise.
sd.play(song_after_noise_cancel_t, N)
