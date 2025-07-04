from .journey import ClipboardJourney
from .format_parser import ClipboardFormatParser
import argparse

def main():
    parser = argparse.ArgumentParser(description='Clipboard Journey Tracker')
    parser.add_argument('--mode', choices=['journey', 'parse'], default='journey',
                       help='Run mode: journey tracking or format parsing')
    args = parser.parse_args()
    
    if args.mode == 'journey':
        tracker = ClipboardJourney()
        tracker.track_clipboard_journey()
    else:
        parser = ClipboardFormatParser()
        # Add format parsing logic here
        
if __name__ == "__main__":
    main()
