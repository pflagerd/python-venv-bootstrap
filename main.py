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

    # Example arguments
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=False,
        help="Path to the input file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )

    return parser.parse_args()


def main():
    """Main execution logic."""
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    logger.info("Starting script execution...")

    # Your code logic goes here
    if args.input:
        logger.info(f"Processing input file: {args.input}")
    else:
        logger.info("No input file provided. Running default logic.")

    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # Load your audio file (Must be 16000Hz or 8000Hz)
    audio_path = 'V2026-01-15-13-03-16.WAV'
    wav = read_audio(audio_path, sampling_rate=16000)

    # Get speech timestamps
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

    if speech_timestamps:
        print(f"Speech detected! Found {len(speech_timestamps)} segments of speech.")
        for segment in speech_timestamps:
            print(f"  From {segment['start'] / 16000:.2f}s to {segment['end'] / 16000:.2f}s")
    else:
        print("No speech detected (just silence or noise).")

    logger.info("Script completed successfully.")

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