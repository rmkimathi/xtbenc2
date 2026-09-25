#!/usr/bin/python3
# coding: utf-8

import os
import csv
import shlex
import subprocess
import PySimpleGUI as sg
import psgdnd

from about import show_about_window  
from editcsv import edit_csv_window  # Import decoupled function

sg.theme('LightGreen')
sg.set_options(font=('Consolas', 12))

# Define the menu structure
menu_def = [
    ['&File', ['E&xit']],
    ['&Help', ['&About']]
]

right_click_menu = ['', ['Select All', 'Copy']]

cpu, qsv, vaapi, nvenc = [], [], [], []
CONFIG_FILE = "config.txt"

def load_saved_config():
    """Reads the saved default input file and output directory from config.txt if it exists."""
    saved_infile = ''
    saved_outdir = ''
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                if len(lines) >= 1:
                    infile_path = lines[0].strip()
                    if os.path.isfile(infile_path) or infile_path == '':
                        saved_infile = infile_path
                if len(lines) >= 2:
                    outdir_path = lines[1].strip()
                    if os.path.isdir(outdir_path) or outdir_path == '':
                        saved_outdir = outdir_path
        except Exception:
            pass
    return saved_infile, saved_outdir

def save_config(infile_path, outdir_path):
    """Saves the input path and output directory to config.txt inside the working directory."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{infile_path.strip()}\n{outdir_path.strip()}")
    except Exception:
        pass

def load_csv_preset(file_path):
    """Loads CSV files, extracting raw text and cleaning up structural quote configurations."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            cleaned_rows = []
            for row in csv.reader(csvfile):
                if not row or not row[0]:
                    continue
                item = row[0].strip()
                
                if item.startswith('[') and item.endswith(']'):
                    item = item[1:-1].strip()
                if (item.startswith("'") and item.endswith("'")) or (item.startswith('"') and item.endswith('"')):
                    item = item[1:-1].strip()
                    
                if item:
                    cleaned_rows.append(item)
            return cleaned_rows if cleaned_rows else ['']
    return ['']

PRESET_FILES = {
    'CPU': '_internal/presets/CPU.csv',
    'QSV': '_internal/presets/QSV.csv',
    'VAAPI': '_internal/presets/VAAPI.csv',
    'NVENC': '_internal/presets/NVENC.csv',
}

cpu = load_csv_preset(PRESET_FILES['CPU'])
qsv = load_csv_preset(PRESET_FILES['QSV'])
vaapi = load_csv_preset(PRESET_FILES['VAAPI'])
nvenc = load_csv_preset(PRESET_FILES['NVENC'])

info_commands = ['-encoders', '-decoders', '-buildconf', '-h full', '-codecs', '-formats', '-protocols', '-pix_fmts']

# Load the saved configuration values on startup
initial_infile, initial_outdir = load_saved_config()

layout = [
    [sg.Menu(menu_def)],
    [sg.Text('Input', size=(11,1)), sg.InputText(default_text=initial_infile, key='_infile_', enable_events=True, expand_x=True), sg.FileBrowse(size=(12,1))],
    [sg.Text('Output Dir', size=(11,1)), sg.InputText(default_text=initial_outdir, key='_outdir_', enable_events=True, expand_x=True), sg.FolderBrowse(size=(12,1))],
    [sg.Text('Output File', size=(11,1)), sg.InputText(default_text='out.mp4', key='_outfilename_', expand_x=True)],
    
    [sg.Frame(layout=[[sg.Radio('CPU', "RADIO1", default=True, key='_CPU', enable_events=True),
                       sg.Radio('QSV', "RADIO1", key='_QSV', enable_events=True),
                       sg.Radio('VAAPI', "RADIO1", key='_VAAPI', enable_events=True),
                       sg.Radio('NVENC', "RADIO1", key='_NVENC', enable_events=True)]],
              title='CODEC', title_color='red', relief=sg.RELIEF_SUNKEN, expand_x=True)],
              
    [sg.Frame(layout=[[sg.Combo(values=cpu, default_value='-i {input} -c copy -map_metadata -1 {output_dir}', size=(136, 20), key='_editor_', expand_x=True)]], 
              title='Templates:', expand_x=True)],
              
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
     sg.Button('Clear', button_color=('white', 'blue')), sg.Button('Exit', button_color=('white','firebrick3'))]
]

window = sg.Window('XTB Encoder', layout, finalize=True, resizable=True, icon='_internal/presets/xtbenc.ico')

psgdnd.register_element_dnd(window['_infile_'], window, psgdnd.DROP_TYPE_FILES)

def drop_input_file(event):
    file_path = event.data
    if file_path.startswith('{') and file_path.endswith('}'):
        file_path = file_path[1:-1]
    window['_infile_'].update(file_path)
    save_config(file_path, window['_outdir_'].get())

try:
    window.TKroot.tk.call('package', 'require', 'tkdnd')
    window.TKroot.drop_target_register('DND_Files')
    window.TKroot.dnd_bind('<<Drop>>', drop_input_file)
except Exception:
    pass

def reload_preset(codec):
    """Reload a codec preset CSV and refresh the Combo if it is active."""
    global cpu, qsv, vaapi, nvenc

    presets = load_csv_preset(PRESET_FILES[codec])

    if codec == 'CPU':
        cpu = presets
        active = window['_CPU'].get()
    elif codec == 'QSV':
        qsv = presets
        active = window['_QSV'].get()
    elif codec == 'VAAPI':
        vaapi = presets
        active = window['_VAAPI'].get()
    elif codec == 'NVENC':
        nvenc = presets
        active = window['_NVENC'].get()
    else:
        return

    if active:
        window['_editor_'].update(
            values=presets,
            value=presets[0] if presets else ''
        )

active_process = None

while True:
    # Modern lower-case syntax used for window.read()
    event, values = window.read(timeout=100 if active_process else None)
    if event in ('Exit', None, sg.WIN_CLOSED):
        if active_process: 
            active_process.kill()
        break           

    # --- HANDLE RIGHT-CLICK MENU ---
    elif event == 'Select All':
        window['-OUTPUT-'].Widget.tag_add("sel", "1.0", "end")
        
    elif event == 'Copy':
        try:
            selected_text = window['-OUTPUT-'].Widget.selection_get()
            window.TKroot.clipboard_clear()
            window.TKroot.clipboard_append(selected_text)
        except Exception:
            pass
    
    elif event == 'About':
        show_about_window()  

    if active_process:
        line = active_process.stderr.readline()
        if line: 
            print(line.strip())
        if active_process.poll() is not None:
            remaining_logs = active_process.stderr.read()
            if remaining_logs: 
                print(remaining_logs.strip())
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
        file_path = sg.popup_get_file('Select CSV', file_types=(('CSV', '*.csv'),), initial_folder='_internal/presets', icon='_internal/presets/xtbenc.ico')
        if file_path: 
            # Call decoupled UI frame and feed our reload logic pointer inside as a callback context
            edit_csv_window(file_path, reload_preset)

    if event in ('_infile_', '_outdir_') and values:
        save_config(values['_infile_'], values['_outdir_'])

    if values:
        video_in, output_dir = values['_infile_'], values['_outdir_']
        filename = values['_outfilename_'].strip()
        raw_args = values['_editor_']
        
        target_out = os.path.join(output_dir, filename) if (output_dir and filename) else ''
        
        quoted_in = f'"{video_in}"' if video_in else '""'
        quoted_out = f'"{target_out}"' if target_out else '""'
        
        rendered_args = raw_args.replace('{input}', quoted_in).replace('{output_dir}', quoted_out)
        cmd1 = f'ffmpeg -v verbose -hide_banner -y {rendered_args}'
        
        if event not in ('Run', 'Run Info', 'ffprobe_in', 'ffprobe_out'):
            window['-PREVIEW-'].update(cmd1)
    else:
        video_in, output_dir, filename, cmd1 = '', '', '', ''

    # Modern lower-case syntax used for element.update()
    if event == '_CPU': window['_editor_'].update(values=cpu, set_to_index=0)
    if event == '_QSV': window['_editor_'].update(values=qsv, set_to_index=0)
    if event == '_VAAPI': window['_editor_'].update(values=vaapi, set_to_index=0)
    if event == '_NVENC': window['_editor_'].update(values=nvenc, set_to_index=0)

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    if event == 'ffprobe_in' and video_in:
        print('MEDIA INFO (Input):')
        res = subprocess.run(['ffprobe', '-hide_banner', video_in], stderr=subprocess.PIPE, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        print(res.stderr, '\n\n**********\n')

    if event == 'ffprobe_out' and output_dir and filename:
        print('MEDIA INFO (Output File):')
        out_file = os.path.join(output_dir, filename)
        if os.path.exists(out_file):
            res = subprocess.run(['ffprobe', '-hide_banner', out_file], stderr=subprocess.PIPE, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            print(res.stderr, '\n\n**********\n')
        else:
            print(f'[INFO] "{filename}" not found in {output_dir} yet.\n\n**********\n')

    if event == 'Run Info':
        info_cmd = values['-INFO-CMD-']
        filter_text = values['-FILTER-'].strip().lower()
        print(f'FFMPEG DIAGNOSTIC ({info_cmd}):')
        cmd_parts = ['ffmpeg', '-hide_banner'] + info_cmd.split()
        res = subprocess.run(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if filter_text:
            filtered_lines = [line for line in res.stdout.splitlines() if filter_text in line.lower()]
            print('\n'.join(filtered_lines) if filtered_lines else '[INFO] No matching items found.')
        else:
            print(res.stdout)
        print('\n**********\n')

    if event == 'Run' and not active_process:
        final_cmd = values['-PREVIEW-'].strip()
        if final_cmd:
            print(f"Executing: {final_cmd}\n")
            try:
                cmd_parts = shlex.split(final_cmd)
                active_process = subprocess.Popen(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                window['Run'].update(disabled=True)
                window['Cancel Run'].update(disabled=False)
            except Exception as e:
                print(f"[ERROR] Failed to start process: {e}\n")
                active_process = None

window.close()
