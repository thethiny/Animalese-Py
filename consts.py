codecs = {
    'h264': {
        'codec': 'libx264',
        'audio_codec': 'libfdk_aac'
    },
    'mp4':
    {
        'codec': 'libx264',
        'audio_codec': 'libmp3lame'
    },
    'mp4_alt':
    {
        'codec': 'libx264',
        'audio_codec': 'aac',
    },
    'mpeg4':
    {
        'codec': 'mpeg4',
        'audio_codec': 'libfdk_aac'
    }
    
}

codec_names = {
    'h264': {
        'video': 'h.264',
        'audio': 'm4a'
    },
    'mp4':
    {
        'video': 'h.264',
        'audio': 'mp3'
    },
    'mpeg4':
    {
        'video': 'MPEG4',
        'audio': 'm4a'
    }
}

def get_codec_info(codec):
    if codec == 'libx264':
        return 'h.264'
    if codec == 'mpeg4':
        return 'MPEG4'
    if codec == 'libmp3lame':
        return 'MP3'
    if codec == 'libfdk_aac':
        return 'AAC'

DEFAULT_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
FFMPEG_BINARY_AAC = "ffmpeg.exe"
FFPROBE_BINARY_AAC = "ffprobe.exe"
OUTPUT_FOLDER = "output"
TEXTS_FOLDER = "texts"
DATA_FOLDER = "input"