import numpy as np
import mido
import random
import math


msg_list = []

def read():
	mid = mido.MidiFile("D:/MyPrograms/midilstm/songs/song0.mid")
	for msg in mid:
		#if msg.is_meta:
		print(msg)
		

def denormalize_time(t):
	return (t * 35756)


def load_list():
	global msg_list
	msg_list = np.load("data/messages.npy")
	print(len(msg_list))

def print_times():
	f= open("times.txt", "a")
	max_1 = 0
	d = dict()

	for msg in msg_list:
		#f.write(str(msg[-1])+"\n")
		t = msg[-1]
		if t in d:
			d[t] += 1
		else:
			d[t] = 1
		if msg[-1] > max_1:
			max_1 = msg[-1]
	print("max", max_1)
	for el in d:
		print(d[el])

def npy2msg(arr):
	oct = np.argmax(arr[2:13])
	no = np.argmax(arr[13:25])
	n = 12*oct + no
	if n>127:
		n = n -12
	t = int(denormalize_time(arr[-1]))
	m_type = "note_on"
	if arr[1] == 0:
		m_type = "note_off"

	msg = mido.Message(m_type, note=n, velocity=127, time=t)
	if arr[0] == 1:
		msg = mido.MetaMessage("end_of_track", time=0)
	return msg

def npy2msg_c(n, t):
	# chars: note-on[0-127] note-off[128-255] pause[256-264] eof[265] 1, 5, 15, 30, 60, 120, 240, 480, 960
	n = int(n)
	if n <128:
		return mido.Message(type="note_on", note=n, velocity=127, time=t)
	else:
		return mido.Message(type="note_off", note=n-128, velocity=0, time=t)

	
	


def convert(arr, name):
	mid = mido.MidiFile()
	mid.ticks_per_beat = 960
	track = mido.MidiTrack()
	mid.tracks.append(track)
	track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
	track.append(mido.MetaMessage("set_tempo", tempo = 600000))
	
	i = 0
	first = 1

	for el in arr:
		#print(el)
		if el[0] == 1:
			track.append(npy2msg(el))
			mid.save('songs/'+name+str(i)+'.mid')
			i += 1
			first = 1
		elif first == 1:
			first = 0
			mid = mido.MidiFile()
			mid.ticks_per_beat = 960
			track = mido.MidiTrack()
			mid.tracks.append(track)
			track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
			track.append(mido.MetaMessage("set_tempo", tempo = 600000))
			track.append(npy2msg(el))
		else:
			track.append(npy2msg(el))
	mid.save('songs/'+name+str(i)+'.mid')


def convert_c(arr, name):
	mid = mido.MidiFile()
	mid.ticks_per_beat = 960
	track = mido.MidiTrack()
	mid.tracks.append(track)
	track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
	track.append(mido.MetaMessage("set_tempo", tempo = 600000))
	#960,480,240,120,60,30,15,5,1
	char2time = dict([(256, 960),(257, 480),(258, 240),(259, 120),(260, 60),(261, 30),(262, 15),(263, 5),(264, 1)])
	i = 0
	first = 1
	msg_time = 0
	for el in arr:
		#print(el)
		#if el > 256: print(el)		
		if first == 1:
			first = 0
			msg_time = 0
			mid = mido.MidiFile()
			mid.ticks_per_beat = 960
			track = mido.MidiTrack()
			mid.tracks.append(track)
			track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
			track.append(mido.MetaMessage("set_tempo", tempo = 600000))
		if el == 265:
			track.append(mido.MetaMessage("end_of_track", time=0))
			mid.save('songs/'+name+str(i)+'.mid')
			i += 1
			first = 1
		elif el in char2time:
			#print(el)
			msg_time += char2time[el]
		else:
			track.append(npy2msg_c(el,msg_time))
			msg_time = 0
	mid.save('songs/'+name+str(i)+'.mid')		


	



#load_list()
#convert_c(msg_list,"song")
#read()
