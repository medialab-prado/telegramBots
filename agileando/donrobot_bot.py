import sys
import time
import re
from pprint import pprint

import glob, os, json

from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import invert_phase, compress_dynamic_range

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import sys
from aubio import source, sink, pvoc

def vocoder(file_id):
	
	in_file = '/tmp/don_robot/output/' + file_id + ".mp3"
	out_file = '/tmp/don_robot/output/' + file_id + "-voc.mp3"

	samplerate = 44100
	f = source(in_file, samplerate, 256)
	g = sink(out_file, samplerate)
	total_frames, read = 0, 256

	win_s = 512                          # fft size
	hop_s = win_s // 2                   # hop size
	pv = pvoc(win_s, hop_s)              # phase vocoder

	while read:
		samples, read = f()
		spectrum = pv(samples)           # compute spectrum
		spectrum.norm *= .5             # reduce amplitude a bit .8
		spectrum.phas[:] = 0.            # zero phase
		new_samples = pv.rdo(spectrum)   # compute modified samples
		g(new_samples, read)             # write to output
 		total_frames += read

	format_str = "read {:d} samples from {:s}, written to {:s}"
	print(format_str.format(total_frames, f.uri, g.uri))
	return out_file

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):

	trim_ms = 0
	while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
		trim_ms += chunk_size
	return trim_ms

def clean_audio(file_id):

	print "Processing audio"
	file = origin_path + file_id
	sound = AudioSegment.from_ogg(file)

	start_trim = detect_leading_silence(sound)
	end_trim = detect_leading_silence(sound.reverse())
	duration = len(sound)    
	sound = sound[start_trim:duration-end_trim]
	sound = invert_phase(sound)

	output_file = "/tmp/don_robot/output/" + file_id + ".mp3"
	file_handle = sound.export( output_file, format="mp3")
	print("Output File....")
	pprint(file_handle)

def remove_files(file_id):

	file = "/tmp/don_robot/output/" + file_id + ".mp3"
	os.remove(file);
	file = "/tmp/don_robot/" + file_id + ".json"
	os.remove(file);
	file = "/tmp/don_robot/" + file_id
	os.remove(file);
	file = "/tmp/don_robot/output/" + file_id + "-voc.mp3"
	os.remove(file);


def on_voice_msg(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text='Calling....') 

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text='Calling....') 

def on_chat_msg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    robot = u'\U0001F916'

    print(content_type, chat_type, chat_id)

    if content_type == 'voice':

		print('Processing....')
		
		file_id = msg['voice']['file_id']
		file_dest = origin_path + file_id
		
		print('Creating file: ' + file_dest)
		bot.download_file(file_id, file_dest)
		with open(file_dest + '.json', 'w') as outfile:
			json.dump(msg, outfile)
		
		clean_audio(file_id)
		result_file = vocoder(file_id)
		bot.sendMessage(chat_id, 'Don Robot dice....')
		print("Sending..." + result_file)
		bot.sendVoice(chat_id, open(result_file, 'rb'))
		
		if DELETE:
			remove_files(msg_to_process['voice']['file_id'])

		print('Json Data: ')
		pprint(outfile)
		
		messages.append(msg)


    if content_type == 'text':

    	finder = re.compile(ur'/debug')
        if (re.search(finder, msg['text'])):
        	DELETE = False

    	finder = re.compile(ur'/clean')
        if (re.search(finder, msg['text'])):
        	DELETE = False

    	finder = re.compile(ur'/list')
        if (re.search(finder, msg['text'])):
        	for my_msg in messages:
        		bot.sendMessage(chat_id, 'file_id: ' + my_msg['voice']['file_id'] + " size: " + str(my_msg['voice']['file_size']))

        finder = re.compile(ur'/process')
        if (re.search(finder, msg['text'])):
        	msg_to_process = messages.pop()
        	clean_audio(msg_to_process['voice']['file_id'])
        	result_file = vocoder(msg_to_process['voice']['file_id'])
        	bot.sendMessage(chat_id, 'Don Robot dice....')
        	print("Sending..." + result_file)
        	bot.sendVoice(chat_id, open(result_file, 'rb'))
        	remove_files(msg_to_process['voice']['file_id'])

    if content_type == 'new_chat_member':
        bot.sendMessage(chat_id, "Wellcome to this awesome group!")
    if content_type == 'left_chat_member':
        bot.sendMessage(chat_id, "Sayonara baby")

TOKEN = sys.argv[1] 
DELETE = True

origin_path = '/tmp/don_robot/' 
os.chdir(origin_path)

messages = []

for file in glob.glob("*.json"):

	with open(file) as json_file:
		msg = json.load(json_file)

	print(msg)
	file_id = msg['voice']['file_id']
	print('Loading file : ' + str(file_id))
	messages.append(msg)
	
bot = telepot.Bot(TOKEN)
bot.message_loop({'chat': on_chat_msg,
                  'callback_query': on_callback_query})
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
