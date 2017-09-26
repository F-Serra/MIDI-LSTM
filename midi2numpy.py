import numpy as np
import mido
import random
import math

lowest_note = 36
highest_note = 100
no_notes = 128
no_channels = 17
msg_list = []
keys_list = open("keys.txt").read().split("\n")

def c_major(n, i):
	trans_dict = dict([('A major', 3),('A- major', 4),('a minor', 0),('B- major', 2),('b minor', -2),('b- minor', -1),('C major', 0),('c minor', -3),('C# major', -1),('D major', -2),('d minor', -5),('E major', -4),('E- major', -3),('e minor', 5),('F major', -5),('f minor', 4),('G major', 5),('g minor', 2)])
	modulator = trans_dict[keys_list[i]]
	return (n + modulator)

def normalize_time(t):
	return (t / 35756)

def one_hot_channel(ch):
	re = np.zeros(no_channels)
	re[ch] = 1.0
	return re

def one_hot_note(n, i):
	n = c_major(n, i)
	octave = np.zeros(11)
	octave[math.floor(n/12)] = 1.0
	note = np.zeros(12)
	note[n%12] = 1.0
	return np.concatenate((octave, note))

def one_hot_eof():
	re = np.zeros(1 + 1 + 11 + 12 + 1)
	re[0] = 1.0
	return re

def one_hot_msg(m, tpb, tempo, wt, i):
	oh_time = np.zeros(1)
	ticks = mido.second2tick(m.time+wt, tpb, tempo)
	#print(m.time)
	#print(tpb)
	#print(tempo)
	#print(ticks)
	oh_time[0] = normalize_time(round(ticks*(960/tpb)))
	#print(oh_time[0])
	oh_eof = np.zeros(1)
	oh_type = np.ones(1)
	if m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
		oh_type[0] = 0.0
	#oh_ch = one_hot_channel(m.channel)
	oh_note = one_hot_note(m.note, i)
	re = np.concatenate((oh_eof, oh_type, oh_note, oh_time))

	return re

def read():
	#mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime (3).mid")
	mid = mido.MidiFile("D:/MyPrograms/midilstm/songs/song-0.mid")
	print(mid.ticks_per_beat)
	for msg in mid:
		print(msg)
		# if msg.is_meta:
		# 	print(msg)
		# elif msg.type != "note_on" and msg.type != "note_off":
		#  	print(msg)
		# 	#print(one_hot_channel(msg.channel))
		# 	#print(one_hot_note(msg.note))
		# 	#print(np.argmax(one_hot_note(msg.note)))
		# 	#print(one_hot_msg(msg))
		# if msg.type == "end_of_track":
		# 	print(msg)



def stats():

	no_notes_on = 0
	min_note = 100
	max_note = 0
	avg_note = 0
	no_notes_off = 0
	no_vel0 = 0
	max_channel = 0
	avg_time = 0
	min_time = 100
	max_time = 0
	no_files = 2 #18145
	no_msg = 0
	no_msgs = 0
	avg_note_1 = 0

	for i in range(no_files):
		filename = str(i+1)
		mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime ("+filename+").mid")
		print("file "+ str(i))
		for msg in mid:
			if not msg.is_meta:
				no_msg += 1
				if msg.type =="note_on" and msg.velocity > 0:
					no_notes_on += 1
					avg_time += msg.time
					avg_note += msg.note
					if msg.note < min_note:
						min_note = msg.note
					if msg.time > max_time:
						max_time = msg.time
					if msg.note > max_note:
						max_note = msg.note
				elif msg.type =="note_on" and msg.velocity == 0:
					no_vel0 += 1
					avg_time += msg.time
					avg_note += msg.note
					if msg.note < min_note:
						min_note = msg.note
					if msg.time > max_time:
						max_time = msg.time
					if msg.note > max_note:
						max_note = msg.note
				elif msg.type =="note_off":
					no_notes_off += 1
					avg_time += msg.time
					avg_note += msg.note
					if msg.note < min_note:
						min_note = msg.note
					if msg.time > max_time:
						max_time = msg.time
					if msg.note > max_note:
						max_note = msg.note
		avg_note_1 += avg_note/no_msg
		avg_note = 0
		no_msgs += no_msg
		no_msg = 0

	no_notes_on = no_notes_on/no_files
	no_notes_off_all = (no_vel0+no_notes_off)/no_files
	avg_time = avg_time/(no_vel0+no_notes_on+no_notes_off)
	avg_note_1 = avg_note_1/(no_files)
	print("no_of_msgs: " +str(no_msgs))
	print("no_of_notes_on: " +str(no_notes_on))
	print("no_of_notes_off: " +str(no_notes_off_all))
	print("avg_time: " +str(avg_time))
	print("max_time: " +str(max_time))
	print("max_channel: " +str(max_channel))
	print("max_note : " +str(max_note))
	print("min_note : " +str(min_note))
	print("avg_note : " +str(avg_note_1))

def read_all():
	no_files = 230
	for i in range(no_files):
		filename = str(i+1)
		mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime ("+filename+").mid")
		tpb = mid.ticks_per_beat
		#print("tpb",tpb)
		temp = 0
		print("file "+ str(i))
		wait_time  = 0
		for msg in mid:
			if msg.type == "note_on" or msg.type == "note_off":
				msg_list.append(one_hot_msg(msg,tpb,temp,wait_time, i))
				wait_time  = 0
			elif msg.type == "end_of_track":
				msg_list.append(one_hot_eof())
			elif msg.type == "set_tempo":
				temp = msg.tempo
			elif not msg.is_meta:
				wait_time += msg.time

# chars: note-on[0-127] note-off[128-255] pause[256-264] eof[265] 1, 5, 15, 30, 60, 120, 240, 480, 960
def time_list(t, tpb, temp, w_time):
	time_symbols = np.array([960,480,240,120,60,30,15,5,1])
	ticks = mido.second2tick(t+w_time, tpb, temp)	
	ticks_norm = round(ticks*(960/tpb))
	return_list = list()
	#print("ticks", ticks_norm)
	for i, el in enumerate(time_symbols):
		while(ticks_norm>=el):
			return_list.append(256+i)
			ticks_norm -= el
	#print(return_list)
	return return_list

def msg2char(msg, i):
	n_trans = c_major(msg.note, i)
	if msg.type == "note_on" and msg.velocity > 0:
		if n_trans > 127:
			n_trans -= 12
		if n_trans < 0:
			n_trans += 12
		return n_trans
	else:
		if n_trans > 127:
			n_trans -= 12
		if n_trans < 0:
			n_trans += 12
		return 128+n_trans


def eof2char():
	return 265


def read_all_c():
	no_files = 230
	for i in range(no_files):
		filename = str(i+1)
		mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime ("+filename+").mid")
		tpb = mid.ticks_per_beat
		#print("tpb",tpb)
		print("file "+ str(i))
		temp = 0
		wait_time  = 0
		global msg_list
		for msg in mid:
			if msg.type == "note_on" or msg.type == "note_off":
				msg_list += time_list(msg.time, tpb, temp, wait_time)
				#print(msg2char(msg, i))
				msg_list.append(msg2char(msg, i)) 
				wait_time  = 0
			elif msg.type == "end_of_track":
				msg_list.append(eof2char())
			elif msg.type == "set_tempo":
				temp = msg.tempo
			elif not msg.is_meta:
				wait_time += msg.time


def save_list():
	npy = np.stack(msg_list)
	print(npy.shape)
	np.save("data/messages",npy)

def load_list():
	msg_list = np.load("messages.npy")

def rag_stats():
	no_files = 230
	tempo_l = list()
	tpb_l = list()
	num_l = list()
	denom_l = list()
	for i in range(no_files):
		filename = str(i+1)
		mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime ("+filename+").mid")
		print("-------------------------------------------")
		print("file ", filename)
		channels = set()
		tempi = set()
		key = "N/A"
		tempo = 0
		num = 0
		denom = 0
		for msg in mid:
			if msg.type == "key_signature":
				key = msg.key
			if msg.type == "time_signature":
				num = msg.numerator
				denom = msg.denominator
			if msg.type == "set_tempo":
				tempo = msg.tempo
				tempi.add(tempo)
			if msg.type == "note_on":
				channels.add(msg.channel)
		tempo_l.append(tempi)
		tpb_l.append(mid.ticks_per_beat)
		num_l.append(num)
		denom_l.append(denom)
		print("Key :", key)
		print("Tempo :", tempi)
		print("Tpb :", mid.ticks_per_beat)
		print("TS: ", num , denom)
		print("Channels: ", channels)
	for i in range(no_files):
		print(tempo_l[i], tpb_l[i], num_l[i], denom_l[i])

def pure_rag():
	pure_l = open("pure_ragtime.txt").read().split("\n")
	for el in pure_l:
		nr = int(el) +1
		mid = mido.MidiFile("D:/MyPrograms/midilstm/ragtime/ragtime ("+str(nr)+").mid")
		tpb = mid.ticks_per_beat
		#print("tpb",tpb)
		print("file "+ str(nr))
		temp = 0
		wait_time  = 0
		global msg_list
		for msg in mid:
			if msg.type == "note_on" or msg.type == "note_off":
				msg_list += time_list(msg.time, tpb, temp, wait_time)
				#print(msg2char(msg, i))
				msg_list.append(msg2char(msg, int(el))) 
				wait_time  = 0
			elif msg.type == "end_of_track":
				msg_list.append(eof2char())
			elif msg.type == "set_tempo":
				temp = msg.tempo
			elif not msg.is_meta:
				wait_time += msg.time


pure_rag()
save_list()