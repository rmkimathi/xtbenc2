#!/usr/bin/env python3
# coding: utf-8



import PySimpleGUI as sg
import subprocess
import csv


sg.ChangeLookAndFeel('LightGreen')


with open('presets/CPU.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile , delimiter=',', quotechar='"')
    for Tup1 in spamreader:
       cpu = (Tup1)


with open('presets/QSV.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile , delimiter=',', quotechar='"')
    for Tup2 in spamreader:
       qsv = (Tup2)


with open('presets/VAAPI.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile , delimiter=',', quotechar='"')
    for Tup3 in spamreader:
       vaapi = (Tup3)    


with open('presets/NVENC.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile , delimiter=',', quotechar='"')
    for Tup4 in spamreader:
       nvenc = (Tup4)


layout = [
    [sg.Text('Input', size=(7,1)),
     sg.InputText(key='_infile_', size=(116,1)),
     sg.FileBrowse(size=(8,1))],
    
    [sg.Text('Output', size=(7,1)),
     sg.InputText(key='_outfile_', size=(116,1)),
     sg.SaveAs(size=(8,1))],
    
    [sg.Frame(layout=[
        [sg.Radio('CPU', "RADIO1", default=True, key='_CPU', enable_events=True),
         sg.Radio('QSV', "RADIO1", key='_QSV', enable_events=True),
         sg.Radio('VAAPI', "RADIO1", key='_VAAPI', enable_events=True),
         sg.Radio('NVENC', "RADIO1", key='_NVENC', enable_events=True)]
    ], title='CODEC',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Use these to set flags')],
    
    [sg.Frame(layout=[
        [sg.Combo(values=cpu, default_value='', size=(134, 1), key='_editor_')]
    ], title='Extra Options (after input):')],
    
    [sg.Button('ffprobe_in'),
     sg.Button('ffprobe_out'),
     sg.Button('encoders')],
    
    [sg.Frame(layout=[
        [sg.Output(size=(134, 20), font=("Consolas", 10))]], title='LOG')],
    
    [sg.Button('Convert'),
     sg.SimpleButton('Exit', button_color=('white','firebrick3'))]
]


window = sg.Window('XTB Encoder', icon='presets/xtbenc.png') # icon='presets/xtbenc.ico' for Windows

window.Layout(layout)


# Loop taking in user input

while True:

	(event, values) = window.Read(timeout=10)

	#print(event, values) #debug

	if event == 'Exit' or event is None:

		break           # Exit button clicked



	video_in = values['_infile_']
	video_out = values['_outfile_']

	args1 = "ffmpeg -v verbose -y -i"
	args2 = "ffmpeg -v verbose -y -vaapi_device '/dev/dri/renderD128' -i"

	myargs = values['_editor_']

	ffp1 = ['ffprobe', '-hide_banner', video_in]
	ffp2 = ['ffprobe', '-hide_banner', video_out]

	ffm1 = ['ffmpeg', '-hide_banner', '-encoders']


	cmd1 = [] # Radio button selection

	if values['_CPU'] is True: cmd1 = args1 + " " + '"%s"'%video_in + " " + myargs + " " + '"%s"'%video_out

	if values['_QSV'] is True: cmd1 = args1 + " " + '"%s"'%video_in + " " + myargs + " " + '"%s"'%video_out

	if values['_VAAPI'] is True: cmd1 = args2 + " " + '"%s"'%video_in + " " + myargs + " " + '"%s"'%video_out

	if values['_NVENC'] is True: cmd1 = args1 + " " + '"%s"'%video_in + " " + myargs + " " + '"%s"'%video_out




	if event == '_CPU': window['_editor_'].Update(values=cpu, set_to_index=0)

	if event == '_QSV': window['_editor_'].Update(values=qsv, set_to_index=0)

	if event == '_VAAPI': window['_editor_'].Update(values=vaapi, set_to_index=0)

	if event == '_NVENC': window['_editor_'].Update(values=nvenc, set_to_index=0)



	if event == 'ffprobe_in':

		print('MEDIA INFO (Input):')

		ffp3 = subprocess.run(ffp1, stderr=subprocess.PIPE, text=True)

		print(ffp3.stderr)
		
		print( )

		print('**********')

		print( )


	if event == 'ffprobe_out':

		print('MEDIA INFO (Output):')

		ffp4 = subprocess.run(ffp2, stderr=subprocess.PIPE, text=True)

		print(ffp4.stderr)
		
		print( )

		print('**********')

		print( )


	if event == 'encoders':

		ffm2 = subprocess.run(ffm1, stdout=subprocess.PIPE, text=True)

		print(ffm2.stdout)
		
		print( )

		print('**********')

		print( )


	if event == 'Convert':

		print('INPUT:', video_in)

		print( )

		print('OUTPUT:', video_out)

		print( )

		print(cmd1)

		print( )

		window.refresh()

		p1 = subprocess.run(cmd1, shell=True)

		print( )

		print('returncode:', p1.returncode)

		print( )

		print('**********')

		print( )



window.close()

