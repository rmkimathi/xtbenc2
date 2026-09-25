import webbrowser
import PySimpleGUI as sg

def show_about_window():
    """Displays a modal window containing version, credit, and contact information."""
    about_layout = [
        [sg.Text('XTB Encoder', font=('Consolas', 14, 'bold'))],
        [sg.Text('Version 2026.09.25', font=('Consolas', 10, 'italic'))],
        [sg.HSeparator()],
        
        # Website Section (Clickable)
        [sg.Text('Website:'), 
         sg.Text('rmkimathi.github.io', text_color='blue', enable_events=True, key='-URL-', font=('Consolas', 10, 'underline'))],
        
        # Email Section (Clickable)
        [sg.Text('Support:'), 
         sg.Text('rmkimathi@outlook.com', text_color='blue', enable_events=True, key='-EMAIL-', font=('Consolas', 10, 'underline'))],
        
        [sg.HSeparator()],
        
        # Credits & Copyright
        [sg.Text('Credits:', font=('Consolas', 10, 'bold'))],
        [sg.Text('• Lead Developer: R. Kimathi\n• UI Design: R. Kimathi')],
        [sg.Text('© 2026 XTB Encoder.', font=('Consolas', 9))],
        
        [sg.Button('Close', size=(10, 1), pad=((0, 0), (10, 0)))]
    ]

    about_win = sg.Window('About', about_layout, modal=True, element_justification='center', icon='_internal/presets/xtbenc.ico')

    while True:
        event, values = about_win.read()
        if event in (sg.WIN_CLOSED, 'Close'):
            break
        elif event == '-URL-':
            webbrowser.open('https://rmkimathi.github.io')
        elif event == '-EMAIL-':
            webbrowser.open('mailto:rmkimathi@outlook.com')

    about_win.close()
