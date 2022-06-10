'''
We import Python modules that we are going to use in our program
(numpy) is used to do all calculations required to construct the signals
(matplotlib.pyplot) is used to plot the sound signal
(sounddevice) is used to play the sound signal
'''
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
    
4. After the whole song has been constructed, we plot the song's signal on the
y-axis and the time on the x-axis using the (matplotlib) package.
5. Finally, we use the (sounddevice) package to play the song on the speakers,
   using the (sd.play) function with sample rate 3* 1024.
'''
def play_song(notes):
    song = 0
    next_note_start = 0
    for current_note in notes:
        freq = current_note[0]
        duration = current_note[1]
        pulse = (t >= next_note_start) & (t <= next_note_start + duration)
        next_note_start += duration + quarter / 4
        song += note(freq) * pulse
    plt.plot(t, song)
    sd.play(song, 3 * 1024)
    


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


# Finally we call our method and give it the song to play.
play_song(pirates_of_the_caribbean)