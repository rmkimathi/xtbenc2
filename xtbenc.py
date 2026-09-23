#!/usr/bin/python3
# coding: utf-8

import PySimpleGUI as sg
import subprocess
import csv
import shlex
import os

sg.ChangeLookAndFeel('LightGreen')
sg.set_options(font=('Ubuntu Mono', 12))

right_click_menu = ['', ['Copy', 'Paste', 'Select All', 'Cut']]

cpu, qsv, vaapi, nvenc = [], [], [], []

def load_csv_preset(file_path):
    """Loads CSV files, extracting raw text and cleaning up structural quote configurations."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            cleaned_rows = []
            # Using csv.reader natively handles the primary outer layer of double quotes
            for row in csv.reader(csvfile):
                if not row or not row[0]:
                    continue
                item = row[0].strip()
                
                # Failsafe: Remove any extra literal string wrappers if they leak past the reader
                if item.startswith('[') and item.endswith(']'):
                    item = item[1:-1].strip()
                if (item.startswith("'") and item.endswith("'")) or (item.startswith('"') and item.endswith('"')):
                    item = item[1:-1].strip()
                    
                if item:
                    cleaned_rows.append(item)
            return cleaned_rows if cleaned_rows else ['']
    return ['']

cpu = load_csv_preset('_internal/presets/CPU.csv')
qsv = load_csv_preset('_internal/presets/QSV.csv')
vaapi = load_csv_preset('_internal/presets/VAAPI.csv')
nvenc = load_csv_preset('_internal/presets/NVENC.csv')

info_commands = ['-encoders', '-decoders', '-buildconf', '-h full', '-codecs', '-formats', '-protocols', '-pix_fmts']

layout = [
    [sg.Text('Input', size=(7,1)), sg.InputText(key='_infile_', expand_x=True), sg.FileBrowse(size=(10,1))],
    [sg.Text('Output', size=(7,1)), sg.InputText(key='_outfile_', expand_x=True), sg.SaveAs(size=(10,1))],
    
    [sg.Frame(layout=[[sg.Radio('CPU', "RADIO1", default=True, key='_CPU', enable_events=True),
                       sg.Radio('QSV', "RADIO1", key='_QSV', enable_events=True),
                       sg.Radio('VAAPI', "RADIO1", key='_VAAPI', enable_events=True),
                       sg.Radio('NVENC', "RADIO1", key='_NVENC', enable_events=True)]],
              title='CODEC', title_color='red', relief=sg.RELIEF_SUNKEN, expand_x=True)],
              
    [sg.Frame(layout=[[sg.Combo(values=cpu, default_value='', size=(136, 20), key='_editor_', expand_x=True)]], 
              title='Extra Options (after input):', expand_x=True)],
              
    [sg.Frame(layout=[[sg.Multiline(key='-PREVIEW-', size=(100, 4), expand_x=True)]], 
              title='Command Line (Preview/Edit):', expand_x=True)],
    
    [sg.Button('ffprobe_in'), 
     sg.Button('ffprobe_out'), 
     sg.Text(' |  FFmpeg Diagnostics:', pad=((10,5),(0,0))),
     sg.Combo(values=info_commands, default_value='-encoders', key='-INFO-CMD-', size=(15,1)),
     sg.Text('Filter text (grep):', pad=((10,2),(0,0))),
     sg.InputText(key='-FILTER-', size=(15,1), tooltip='Case-insensitive text filter (e.g. avc, h264, nvenc)'),
     sg.Button('Run Info'),
     sg.Button('Edit CSV', pad=((10,0),(0,0)))],
    
    [sg.Frame(layout=[[sg.Output(key='-OUTPUT-', size=(100, 20), expand_x=True, expand_y=True, right_click_menu=right_click_menu)]], 
              title='LOG', expand_x=True, expand_y=True)],
              
    [sg.Button('Preview'), sg.Button('Run'), sg.Button('Cancel Run', button_color=('white', 'orange'), disabled=True), 
     sg.Button('Clear', button_color=('white', 'blue')), sg.SimpleButton('Exit', button_color=('white','firebrick3'))]
]

window = sg.Window('XTB Encoder', layout, finalize=True, resizable=True, icon='_internal/presets/xtbenc.png')

def drop_input_file(event):
    file_path = event.data
    if file_path.startswith('{') and file_path.endswith('}'):
        file_path = file_path[1:-1]
    window['_infile_'].update(file_path)

try:
    window.TKroot.tk.call('package', 'require', 'tkdnd')
    window.TKroot.drop_target_register('DND_Files')
    window.TKroot.dnd_bind('<<Drop>>', drop_input_file)
except Exception:
    pass

def edit_csv_window(file_path):
    with open(file_path, newline='') as csvfile:
        data = csvfile.read()
    layout = [[sg.Multiline(data, expand_x=True, expand_y=True, key='_text_', right_click_menu=right_click_menu)], [sg.Button('Save'), sg.Button('Cancel')]]
    edit_window = sg.Window(f'Editing {file_path}', layout, modal=True, resizable=True, size=(800, 600))
    while True:
        event, values = edit_window.read()
        if event in (sg.WINDOW_CLOSED, 'Cancel'): break
        if event == 'Save':
            with open(file_path, 'w', newline='') as csvfile:
                csvfile.write(values['_text_'])
            sg.popup(f'{file_path} saved.')
            break
    edit_window.close()

active_process = None

while True:
    event, values = window.Read(timeout=100 if active_process else None)
    if event in ('Exit', None):
        if active_process: active_process.kill()
        break           

    if active_process:
        line = active_process.stderr.readline()
        if line: print(line.strip())
        if active_process.poll() is not None:
            remaining_logs = active_process.stderr.read()
            if remaining_logs: print(remaining_logs.strip())
            print(f'\nProcess finished with returncode: {active_process.returncode}\n\n**********\n')
            active_process = None
            window['Cancel Run'].update(disabled=True)
            window['Run'].update(disabled=False)

    if event == 'Cancel Run' and active_process:
        active_process.kill()
        print("\n[INFO] Encoding Cancelled by user.")
        active_process = None
        window['Cancel Run'].update(disabled=True)
        window['Run'].update(disabled=False)

    if event == 'Clear':
        window['-OUTPUT-'].update('')

    if event == 'Edit CSV':
        file_path = sg.popup_get_file('Select CSV', file_types=(('CSV', '*.csv'),), initial_folder='_internal/presets')
        if file_path: edit_csv_window(file_path)

    if values:
        video_in, video_out = values['_infile_'], values['_outfile_']
        myargs = values['_editor_']
        cmd1 = f'ffmpeg -v verbose -y -i "{video_in}" {myargs} "{video_out}"' if not values['_VAAPI'] else f'ffmpeg -v verbose -y -vaapi_device "/dev/dri/renderD128" -i "{video_in}" {myargs} "{video_out}"'
    else:
        video_in, video_out, myargs, cmd1 = '', '', '', ''

    if event == '_CPU': window['_editor_'].Update(values=cpu, set_to_index=0)
    if event == '_QSV': window['_editor_'].Update(values=qsv, set_to_index=0)
    if event == '_VAAPI': window['_editor_'].Update(values=vaapi, set_to_index=0)
    if event == '_NVENC': window['_editor_'].Update(values=nvenc, set_to_index=0)

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    if event == 'ffprobe_in' and video_in:
        print('MEDIA INFO (Input):')
        res = subprocess.run(['ffprobe', '-hide_banner', video_in], stderr=subprocess.PIPE, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        print(res.stderr, '\n\n**********\n')

    if event == 'ffprobe_out' and video_out:
        print('MEDIA INFO (Output):')
        res = subprocess.run(['ffprobe', '-hide_banner', video_out], stderr=subprocess.PIPE, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        print(res.stderr, '\n\n**********\n')

    if event == 'Run Info' and values:
        info_flag = values['-INFO-CMD-'].strip()
        filter_term = values['-FILTER-'].strip().lower()
        
        if info_flag:
            parsed_args = shlex.split(info_flag)
            full_command = ['ffmpeg', '-hide_banner'] + parsed_args
            
            if filter_term:
                print(f'RUNNING FFMPEG DIAGNOSTIC: {" ".join(full_command)} (Filtered for: "{filter_term}")')
            else:
                print(f'RUNNING FFMPEG DIAGNOSTIC: {" ".join(full_command)}')
            
            res = subprocess.run(full_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if filter_term:
                filtered_lines = [line for line in res.stdout.splitlines() if filter_term in line.lower()]
                if filtered_lines:
                    print('\n'.join(filtered_lines))
                else:
                    print(f'[INFO] No matching entries found containing "{filter_term}".')
            else:
                print(res.stdout)
                
            print('\n**********\n')

    if event == 'Preview':
        window['-PREVIEW-'].update(cmd1)

    if event == 'Run' and not active_process:
        ffmpeg_cmd_str = window['-PREVIEW-'].get().strip()
        
        # Strip out literal brackets if they sneak into the input field
        if ffmpeg_cmd_str.startswith('[') and ffmpeg_cmd_str.endswith(']'):
            ffmpeg_cmd_str = ffmpeg_cmd_str[1:-1].strip()
            
        # Strip string-wrapped quotes if they encapsulate the entire argument string
        if (ffmpeg_cmd_str.startswith("'") and ffmpeg_cmd_str.endswith("'")) or (ffmpeg_cmd_str.startswith('"') and ffmpeg_cmd_str.endswith('"')):
            ffmpeg_cmd_str = ffmpeg_cmd_str[1:-1].strip()

        if not ffmpeg_cmd_str:
            print("[ERROR] Set up valid arguments before running.")
            continue
            
        print('INPUT:', video_in)
        print('Executing:', ffmpeg_cmd_str, '\n')
        try:
            active_process = subprocess.Popen(
                shlex.split(ffmpeg_cmd_str), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            window['Cancel Run'].update(disabled=False)
            window['Run'].update(disabled=True)
        except Exception as e:
            print(f"Error starting process: {e}\n")
            active_process = None

window.close()
