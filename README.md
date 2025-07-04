Clipify: Clipboard Journey Tracker

1) Overview

Clipify is a Windows clipboard tracker for developers, students, and anyone curious about how copy-paste works under the hood. It logs every change to your clipboard . This tool is especially useful for reverse engineering, debugging, or simply understanding the clipboard’s behavior in real time.

2) Features

- Live clipboard monitoring: Tracks every clipboard change and displays detailed information in your terminal in every periodic time interval .
- Data previews: Shows a preview of the actual data copied (text, file paths, etc.), including the format and size.
- Process insight: Identifies the process and window (when available) that placed data on the clipboard.
- Debounce logic: Prevents duplicate logs for rapid, multi-format clipboard updates (like screenshots). // this was so hard to debug😭
- Event logging: Optionally saves your clipboard journey to a JSON file for later analysis.

3) Privacy Notice

This tool displays clipboard contents in your terminal, which may include sensitive data.
Do not copy passwords or confidential information while Clipify is running.

4)  Installation

1. Clone or download the repository

   git clone https://github.com/yourusername/clipify.git
   cd clipify

2. Install dependencies

   Make sure you have Python 3.7+ installed. Then run:

   pip install pywin32 psutil

and after this 

1. Run the tracker from the root folder 

   python -m clipboard_inspector.main

2. Copy something 

   Copy text, files, or  a path.
   Watch the terminal for detailed clipboard events.

3. Stop tracking

   Press Ctrl+C to stop.
   The clipboard journey log will be saved as a JSON file in the current directory but one thing keep in mind  Object of type bytes is not JSON serializable .


5) Example Output

📝 CLIPBOARD JOURNEY EVENT
⏰ Time: 2025-07-04T10:46:07.710898
🔢 Sequence: 301
🔑  Owner: explorer.exe (PID: 4678)
📑 Window: Downloads
📒 Formats: 4 total, 114 bytes

 DATA FORMATS JOURNEY:
  1. CF_UNICODETEXT (ID: 13)
     Size: 76 bytes
     Preview: "C:\Users\xyz\lmn\images.jpeg"
  2. CF_LOCALE (ID: 16)
     Size: 0 bytes
     Preview: 
  3. CF_TEXT (ID: 1)
     Size: 38 bytes
     Preview: b'"C:\\Users\\xyz\\lmn\\images.jpeg"'
  4. CF_OEMTEXT (ID: 7)
     Size: 0 bytes
     Preview: 
 
 This the terminal output whn we copy a text :
  ![](screenshot/example.png)

6) Working
- The tracker checks the clipboard every periodic interval of time . 
- When it detects a change (using the clipboard sequence number), it logs the event.
- Debounce logic ensures only one event is logged per user action, even if the clipboard is updated multiple times in quick succession.
- For each event, it shows:
  - Timestamp
  - Clipboard sequence number
  - Process and window that set the clipboard (if available)
  - All clipboard formats present, with data previews

7) Troubleshooting

  i) No window title or process name?  
     Some system actions (like screenshots) do not set a clipboard owner. This is normal.

  ii)Multiple events for one copy?  
     If you still see duplicates, try increasing the debounce time in the code in "journey.py" file

  iii) Permission errors
      Run your terminal as administrator if you have trouble accessing clipboard data from some apps.

8) Customization

Change debounce time:  
Edit the debounce_time variable in track_clipboard_journey to adjust how quickly events are logged.

Log file location:  
By default, logs are saved in the current directory. You can change the filename in the _save_journey_log method.

9) Contributing

Pull requests and suggestions are welcome. If you find a bug or want to add a feature, open an issue or submit a PR.

10) License

This project is open source and free to use for educational and personal purposes.

11) Acknowledgments

Built using Python and the pywin32 and psutil libraries.
Inspired by curiosity about how Windows handles copy-paste under the hood.

Curiosity takes you to places. 
