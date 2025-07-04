import win32clipboard
import win32con
import win32api
import win32process
import psutil
import time
import win32gui
import json
from datetime import datetime
from typing import Dict, List, Any

class ClipboardJourney:
    def __init__(self):
        self.last_sequence = 0
        self.journey_log = []
        self.format_names = self._build_format_map()
        print(" Privacy Notice: This tool displays clipboard contents in your terminal, which may include sensitive data.")
        print("   Do not copy passwords or confidential information while running this tool.\n")

    def _build_format_map(self) -> Dict[int, str]:
        """Build mapping of format IDs to names"""
        standard_formats = {
            1: "CF_TEXT", 2: "CF_BITMAP", 3: "CF_METAFILEPICT",
            4: "CF_SYLK", 5: "CF_DIF", 6: "CF_TIFF", 7: "CF_OEMTEXT",
            8: "CF_DIB", 9: "CF_PALETTE", 10: "CF_PENDATA", 11: "CF_RIFF",
            12: "CF_WAVE", 13: "CF_UNICODETEXT", 14: "CF_ENHMETAFILE",
            15: "CF_HDROP", 16: "CF_LOCALE", 17: "CF_DIBV5"
        }
        return standard_formats.copy()

    def get_format_name(self, fmt_id: int) -> str:
        """Get human-readable format name"""
        if fmt_id in self.format_names:
            return self.format_names[fmt_id]
        try:
            return win32clipboard.GetClipboardFormatName(fmt_id)
        except Exception:
            return f"Unknown({fmt_id})"

    def get_clipboard_owner_process(self) -> Dict[str, Any]:
        """Get process that owns the clipboard"""
        try:
            hwnd = win32clipboard.GetClipboardOwner()
            if not hwnd:
                # No owner, normal for screenshots and some system actions
                return {"pid": 0, "name": "Unknown", "exe": "", "window_title": ""}
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "exe": process.exe(),
                "window_title": win32gui.GetWindowText(hwnd)

            }
        except Exception as e:
            # Only print unexpected errors
            print(f"Unexpected error getting clipboard owner process: {e}")
            return {"pid": 0, "name": "Unknown", "exe": "", "window_title": ""}

    def enumerate_all_formats(self) -> List[Dict[str, Any]]:
        """Get all available clipboard formats and their data (with retry logic)"""
        formats = []
        for attempt in range(3):
            try:
                win32clipboard.OpenClipboard()
                fmt = win32clipboard.EnumClipboardFormats(0)
                while fmt:
                    format_info = {
                        "id": fmt,
                        "name": self.get_format_name(fmt),
                        "data_size": 0,
                        "data_preview": "",
                        "memory_handle": None
                    }
                    try:
                        if fmt == win32con.CF_UNICODETEXT:
                            data = win32clipboard.GetClipboardData(fmt)
                            format_info["data_size"] = len(data) * 2
                            format_info["data_preview"] = data[:100] + "..." if len(data) > 100 else data
                        elif fmt == win32con.CF_TEXT:
                            data = win32clipboard.GetClipboardData(fmt)
                            format_info["data_size"] = len(data)
                            format_info["data_preview"] = data[:100] + "..." if len(data) > 100 else data
                        elif fmt == win32con.CF_HDROP:
                            files = win32clipboard.GetClipboardData(fmt)
                            format_info["data_size"] = len(str(files))
                            format_info["data_preview"] = f"Files: {files}"
                        else:
                            format_info["data_preview"] = f"<{self.get_format_name(fmt)} data>"
                    except Exception as e:
                        format_info["data_preview"] = "<Unable to read>"
                        print(f"Error reading clipboard format {fmt}: {e}")
                    formats.append(format_info)
                    fmt = win32clipboard.EnumClipboardFormats(fmt)
                win32clipboard.CloseClipboard()
                break  # Success,this exit the retry loop
            except Exception as e:
                print(f"Clipboard access failed (attempt {attempt+1}/3): {e}")
                time.sleep(0.2)
        else:
            print("Failed to access clipboard after 3 attempts.")
        return formats

    def track_clipboard_journey(self):
        """Main journey tracking function"""
        print("🔍 Clipboard Journey Tracker Started")
        print("=" * 60)
        debounce_time = 3  # in seconds 
        last_event_time = 0

        try:
            while True:
                try:
                    current_sequence = win32clipboard.GetClipboardSequenceNumber()
                    now = time.time()
                    if current_sequence != self.last_sequence:
                        # Debounce: skip if event is too close to the last one
                        if now - last_event_time < debounce_time:
                            time.sleep(0.1)
                            continue
                        journey_event = self._capture_clipboard_event()
                        self.journey_log.append(journey_event)
                        self._display_journey_event(journey_event)
                        self.last_sequence = current_sequence
                        last_event_time = now
                    time.sleep(0.1)  # Check more frequently for responsiveness
                except KeyboardInterrupt:
                    print("\nJourney tracking stopped by user.")
                    self._save_journey_log()
                    break
                except Exception as e:
                    print(f"Error in journey tracking: {e}")
                    time.sleep(1)
        except Exception as e:
            print(f"Fatal error in journey tracker: {e}")

    def _capture_clipboard_event(self) -> Dict[str, Any]:
        """Capture a complete clipboard event"""
        timestamp = datetime.now()
        owner_process = self.get_clipboard_owner_process()
        formats = self.enumerate_all_formats()
        return {
            "timestamp": timestamp.isoformat(),
            "sequence_number": win32clipboard.GetClipboardSequenceNumber(),
            "owner_process": owner_process,
            "formats": formats,
            "format_count": len(formats),
            "total_data_size": sum(f.get("data_size", 0) for f in formats)
        }

    def _display_journey_event(self, event: Dict[str, Any]):
        """Display clipboard journey event"""
        print(f"\n📝 CLIPBOARD JOURNEY EVENT")
        print(f"⏰ Time: {event['timestamp']}")
        print(f"🔢 Sequence: {event['sequence_number']}")
        print(f"🔑  Owner: {event['owner_process']['name']} (PID: {event['owner_process']['pid']})")
        print(f"📑 Window: {event['owner_process']['window_title']}")
        print(f"📒 Formats: {event['format_count']} total, {event['total_data_size']} bytes")
        print("\n DATA FORMATS JOURNEY:")
        for i, fmt in enumerate(event['formats'], 1):
            print(f"  {i}. {fmt['name']} (ID: {fmt['id']})")
            print(f"     Size: {fmt['data_size']} bytes")
            print(f"     Preview: {fmt['data_preview']}")
        print("=" * 60)

    def _save_journey_log(self):
        """Save journey log to file"""
        filename = f"clipboard_journey_{int(time.time())}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.journey_log, f, indent=2)
            print(f" Journey log saved to {filename}")
        except Exception as e:
            print(f"Error saving log: {e}")
 #emample 
if __name__ == "__main__":
    tracker = ClipboardJourney()
    tracker.track_clipboard_journey()
