# MIDI-LSTM

I took the Tensorflow RNN implementation from https://github.com/sherjilozair/char-rnn-tensorflow and modified it to generate MIDI-files.
The LSTM learns a next-character probability distribution from text files. Given a starting string, it can then generate text following the learned text-style.  
To make this work for MIDI-files, I translated the MIDI-messages to "chars".  
Note-on-events are coded to numbers according to their note-value 0-127, Note-off-events to 128-255.  
To encode the time between two messages, I used the intervalls 1, 5, 15, 30, 60, 120, 240, 480, 960 MIDI-ticks and coded them to the
numbers 256-264. Finally the end-of-file-message is coded to 265.  
Velocity and track-nrs are ignored for now to keep it simple.  
Training data:
113 ragtime piano songs all transposed to C-major or to its parallel key a-minor.

The main modification to the original RNN-implementation is the way the samples are generated. I tried 4 modes to choose the next message:
1. The maximum probability.
2. If the maximum is a note-on then make a pick weighted by all probability values.
3. If the maximum is a note-on then choose another note-on by a weighted pick according to all note-on probability values.
4. If (iterator index) % (some handtuned value around 20) == 0 then choose mode 3 else choose mode 1.

Mode 4 yielded the best results. I've included 3 examples to listen to:  
[song-wo-3-3-long.mid](song-wo-3-3-long.mid)  
[song-wo-3-4-solo1.mid](song-wo-3-4-solo1.mid)  
[song-wo-3-5-solo2.mid](song-wo-3-5-solo2.mid)

Best-of video:  
[![Example](https://img.youtube.com/vi/GBI8ViPjCSo/0.jpg)](https://www.youtube.com/watch?v=GBI8ViPjCSo)
