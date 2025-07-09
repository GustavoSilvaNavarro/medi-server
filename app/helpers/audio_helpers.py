from io import BytesIO

from mutagen import MutagenError
from mutagen.mp3 import MP3

from app.adapters import logger
from app.utils import MAX_AUDIO_DURATION_SECONDS


def audio_length_under_limit(audio: bytes) -> bool:
    """Check if an audio in bytes is an MP3 file and is under a certain duration.

    Args:
        audio (bytes): The audio data as bytes.

    Returns:
        bool: if audit is within limits.
    """
    audio_file_like = BytesIO(audio)

    try:
        # Attempt to parse the bytes specifically as an MP3 file
        audio_info = MP3(audio_file_like)

        if hasattr(audio_info.info, "length"):
            duration = audio_info.info.length
            return duration < MAX_AUDIO_DURATION_SECONDS

        # This case is highly unlikely for a valid MP3 parsed by mutagen
        logger.info("MP3 file parsed, but duration information is missing (unexpected).")
        return False  # noqa: TRY300
    except (MutagenError, Exception) as err:
        logger.error(f"Error parsing audio bytes => {err}")
        return False
