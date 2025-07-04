import win32clipboard
import win32con
import struct
import json
import os
import logging
from typing import Dict, Any, Optional

#logging Setup  
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("clipboard_parser_debug.log"),
        logging.StreamHandler()
    ]
)

class ClipboardFormatParser:
    def __init__(self):
        self.parsers = {
            win32con.CF_TEXT: self._parse_text,
            win32con.CF_UNICODETEXT: self._parse_unicode_text,
            win32con.CF_BITMAP: self._parse_bitmap,
            win32con.CF_DIB: self._parse_dib,
            win32con.CF_HDROP: self._parse_hdrop,
            win32con.CF_HTML: self._parse_html,
        }
        logging.warning(
            "Privacy Notice: This parser may access and log clipboard contents, which could include sensitive data."
        )
    
    def parse_format(self, format_id: int) -> Dict[str, Any]:
        """Parse a specific clipboard format, with error handling."""
        parser = self.parsers.get(format_id, self._parse_generic)
        try:
            return parser(format_id)
        except Exception as e:
            logging.error(f"Error parsing format {format_id}: {e}")
            return {
                "type": "error",
                "format_id": format_id,
                "note": f"Exception occurred: {e}"
            }

    def _clipboard_retry(self, func, *args, **kwargs):
        """Retry clipboard access up to 3 times."""
        for attempt in range(3):
            try:
                win32clipboard.OpenClipboard()
                result = func(*args, **kwargs)
                win32clipboard.CloseClipboard()
                return result
            except Exception as e:
                logging.warning(f"Clipboard access failed (attempt {attempt+1}/3): {e}")
                time.sleep(0.2)
        logging.error("Failed to access clipboard after 3 attempts.")
        return None

    def _parse_text(self, format_id: int) -> Dict[str, Any]:
        """Parse CF_TEXT format (ASCII text)."""
        def get_data():
            data = win32clipboard.GetClipboardData(format_id)
            return {
                "type": "text",
                "encoding": "ascii",
                "length": len(data),
                "content": "[REDACTED FOR PRIVACY]",
                "lines": data.count('\n') + 1 if data else 0
            }
        result = self._clipboard_retry(get_data)
        if result is None:
            return {"type": "text", "note": "Unable to access clipboard"}
        return result

    def _parse_unicode_text(self, format_id: int) -> Dict[str, Any]:
        """Parse CF_UNICODETEXT format (UTF-16 text)."""
        def get_data():
            data = win32clipboard.GetClipboardData(format_id)
            return {
                "type": "unicode_text",
                "encoding": "utf-16",
                "length": len(data),
                "byte_size": len(data) * 2,
                "content": "[REDACTED FOR PRIVACY]",
                "lines": data.count('\n') + 1 if data else 0
            }
        result = self._clipboard_retry(get_data)
        if result is None:
            return {"type": "unicode_text", "note": "Unable to access clipboard"}
        return result

    def _parse_hdrop(self, format_id: int) -> Dict[str, Any]:
        """Parse CF_HDROP format (file list)."""
        def get_data():
            files = win32clipboard.GetClipboardData(format_id)
            try:
                total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            except Exception as e:
                logging.warning(f"Error calculating file sizes: {e}")
                total_size = -1
            return {
                "type": "file_list",
                "file_count": len(files),
                "files": files,
                "total_size": total_size
            }
        result = self._clipboard_retry(get_data)
        if result is None:
            return {"type": "file_list", "note": "Unable to access clipboard"}
        return result

    def _parse_html(self, format_id: int) -> Dict[str, Any]:
        """Parse HTML format."""
        def get_data():
            html_data = win32clipboard.GetClipboardData(format_id)
            try:
                content = html_data.decode('utf-8', errors='ignore')
            except Exception:
                content = "[Unable to decode HTML]"
            return {
                "type": "html",
                "raw_size": len(html_data),
                "content": "[REDACTED FOR PRIVACY]",
                "has_images": "<img" in content.lower(),
                "has_links": "<a" in content.lower()
            }
        result = self._clipboard_retry(get_data)
        if result is None:
            return {"type": "html", "note": "Unable to access clipboard"}
        return result

    def _parse_bitmap(self, format_id: int) -> Dict[str, Any]:
        """Stub for bitmap parsing."""
        # left as it was complex to implement , will do in future
        return {
            "type": "bitmap",
            "note": "Bitmap parsing not implemented for privacy and complexity reasons."
        }

    def _parse_dib(self, format_id: int) -> Dict[str, Any]:
        """Stub for DIB parsing."""
        return {
            "type": "dib",
            "note": "DIB parsing not implemented for privacy and complexity reasons."
        }

    def _parse_generic(self, format_id: int) -> Dict[str, Any]:
        """Generic parser for unknown formats."""
        return {
            "type": "unknown",
            "format_id": format_id,
            "note": "Binary data - parsing not implemented"
        }

