# MIDI-LSTM

I took the Tensorflow RNN implementation from ... and modified it to generate MIDI-files.
The LSTM learns a next-character probability distribution from text files. Given a starting string, it can then generate text following the learned text-style.
To make this work for MIDI-files, I translated the MIDI-messages to "chars". Note-on-events are coded to numbers 0-127, Note-off-events to 128-255.
To encode the time between two messages, I used the intervalls 1, 5, 15, 30, 60, 120, 240, 480, 960 MIDI-ticks and coded them to the
numbers 256-264. Finally the end-of-file-message is coded to 265. Velocity and track-nr are ignored for now to keep it simple.
Training data:
113 ragtime piano songs all transposed to C-major or to its parallel key a-minor.
