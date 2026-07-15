#!/usr/bin/env python3
"""
Module Description: Brief summary of what this script does.
Author: Your Name
Date: 2026-06-30
"""

""" Rationale

if __name__ == "__main__":: Ensures your script only runs code when executed directly, not when imported as a module by another script.

argparse: Makes it easy to pass variables/flags from the terminal right out of the box.

logging instead of print(): Better for production because it automatically includes timestamps, severity levels (INFO, DEBUG, ERROR), and can easily be redirected to a file later.

Graceful Exit handling: The try/except block catches Ctrl+C (KeyboardInterrupt) and unexpected crashes cleanly without printing ugly tracebacks to the user unless you want them to.
"""


import argparse
import logging
import sys
import torch
import soundfile as sf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Script description goes here.")

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )

    parser.add_argument(
        "filenames",
        nargs="+",
        help="One or more filenames to process"
    )

    return parser.parse_args()


def main():
    """Main execution logic."""
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    for filename in args.filenames:
        # Your code logic goes here
        if filename:
            logger.info(f"Processing input file: {filename}")
        else:
            logger.info("No input file provided.")

        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
        (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

        # Load your audio file (Must be 16000Hz or 8000Hz)
        wav = read_audio(filename, sampling_rate=16000)

        # Get speech timestamps
        speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

        if speech_timestamps:
            print(f"Speech detected in {filename}! Found {len(speech_timestamps)} segments of speech.")
            # for segment in speech_timestamps:
            #     print(f"  From {int(segment['start'] / 960000)}:{segment['start'] / 16000 - int(segment['start'] / 960000) * 60.:.1f} to {int(segment['end'] / 960000)}:{segment['end'] / 16000 - int(segment['end'] / 960000) * 60 :.1f}: {segment['start'] / 16000:.1f} {segment['end'] / 16000 - segment['start'] / 16000:.1f}")
            if len(speech_timestamps) == 1:
                print(f"  From {int(segment['start'] / 960000)}:{segment['start'] / 16000 - int(segment['start'] / 960000) * 60.:.1f} to {int(segment['end'] / 960000)}:{segment['end'] / 16000 - int(segment['end'] / 960000) * 60 :.1f}: {segment['start'] / 16000:.1f} {segment['end'] / 16000 - segment['start'] / 16000:.1f}")
            else:
                start = int(speech_timestamps[0]['start'] / 16000)
                last_segment_start = start
                last_segment_end = speech_timestamps[0]['end'] / 16000
                for i in range(1, len(speech_timestamps)):
                    if speech_timestamps[i]['start'] / 16000 - last_segment_start <= 10:
                        last_segment_start = speech_timestamps[i]['start'] / 16000
                        last_segment_end = speech_timestamps[i]['end'] / 16000
                    else:
                        print(f"ffplay -ss {start} -t {last_segment_end - start} -autoexit -nodisp \"{filename}\"")
                        start = int(speech_timestamps[i]['start'] / 16000)
                        last_segment_start = start
                        last_segment_end = speech_timestamps[i]['end'] / 16000
        else:
            print("No speech detected in {filename} (just silence or noise).")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.warning("\nExecution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(99)
