#!.venv/bin/python3
# coding: utf-8

import os
import csv
import PySimpleGUI as sg

def edit_csv_window(file_path, reload_preset_callback):
    """
    Opens a modal window to edit a preset CSV file. 
    Triggers a callback to refresh the main window layout upon saving.
    """
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            data = csvfile.read()
    except Exception as e:
        sg.popup_error(f"Could not read file: {e}")
        return

    layout = [
        [sg.Multiline(data, expand_x=True, expand_y=True, key='_text_')], 
        [sg.Button('Save'), sg.Button('Cancel')]
    ]
    
    edit_window = sg.Window(
        f'Editing {file_path}', 
        layout, 
        modal=True, 
        resizable=True, 
        size=(800, 600), 
        icon='_internal/presets/xtbenc.ico'
    )
    
    while True:
        event, values = edit_window.read()
        if event in (sg.WINDOW_CLOSED, 'Cancel'): 
            break
            
        if event == 'Save':
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    csvfile.write(values['_text_'])
            except Exception as e:
                sg.popup_error(f"Could not save file: {e}")
                break

            filename = os.path.basename(file_path).upper()
            codec = {
                'CPU.CSV': 'CPU',
                'QSV.CSV': 'QSV',
                'VAAPI.CSV': 'VAAPI',
                'NVENC.CSV': 'NVENC'
            }.get(filename)

            if codec:
                # Execute callback function passing back the targeted codec
                reload_preset_callback(codec)

            sg.popup(f'{file_path} saved and presets reloaded.')
            break
            
    edit_window.close()
