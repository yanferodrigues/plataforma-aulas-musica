"""
Transcodificação de vídeos em múltiplas resoluções para qualidade adaptativa.

Dispara em thread separada após salvar uma aula no Studio. Gera apenas as
qualidades que ainda não existem e nunca faz upscaling (não gera 1080p de
um vídeo 720p, por exemplo).

Requer ffmpeg + ffprobe no PATH.
"""
import logging
import os
import shutil
import subprocess
import threading

logger = logging.getLogger(__name__)

# label: (altura, CRF de vídeo, kbps de áudio, nome do FileField, subpasta)
QUALITY_SPECS = [
    ('1080p', 1080, 22, 192, 'video_file_1080p', '1080p'),
    ('720p',   720, 23, 128, 'video_file_720p',  '720p'),
    ('480p',   480, 24, 128, 'video_file_480p',  '480p'),
    ('360p',   360, 26,  96, 'video_file_360p',  '360p'),
]


def ffmpeg_available():
    return bool(shutil.which('ffmpeg')) and bool(shutil.which('ffprobe'))


def _probe_height(path):
    try:
        out = subprocess.check_output(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=height', '-of', 'csv=p=0', path],
            text=True, timeout=30,
        )
        return int(out.strip().splitlines()[0])
    except Exception as exc:
        logger.warning('ffprobe falhou em %s: %s', path, exc)
        return 9999  # assume alta resolução — geramos tudo


def _run_ffmpeg(src, dst, height, crf, audio_kbps):
    cmd = [
        'ffmpeg', '-y', '-i', src,
        '-vf', f'scale=trunc(oh*a/2)*2:{height}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', str(crf),
        '-c:a', 'aac', '-b:a', f'{audio_kbps}k',
        '-movflags', '+faststart',
        dst,
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=7200)


def _transcode_missing(lesson_pk):
    from courses.models import Lesson
    lesson = Lesson.objects.filter(pk=lesson_pk).first()
    if not lesson or not lesson.video_file:
        return
    if not ffmpeg_available():
        logger.warning('ffmpeg não encontrado — pulando geração de qualidades.')
        return

    src_path = lesson.video_file.path
    if not os.path.exists(src_path):
        logger.warning('Arquivo original não existe: %s', src_path)
        return

    src_height = _probe_height(src_path)
    base = os.path.splitext(os.path.basename(src_path))[0]
    media_videos_dir = os.path.dirname(src_path)  # .../media/lessons/videos

    for label, height, crf, audio_kbps, field_name, subdir in QUALITY_SPECS:
        if getattr(lesson, field_name):
            continue  # já existe
        if height >= src_height:
            continue  # não fazer upscale

        out_dir = os.path.join(media_videos_dir, subdir)
        os.makedirs(out_dir, exist_ok=True)
        out_name = f'{base}_{label}.mp4'
        out_path = os.path.join(out_dir, out_name)

        try:
            logger.info('Gerando %s para aula %s…', label, lesson_pk)
            _run_ffmpeg(src_path, out_path, height, crf, audio_kbps)
        except subprocess.CalledProcessError as exc:
            logger.error('ffmpeg falhou (%s): %s', label, exc.stderr[:500] if exc.stderr else exc)
            if os.path.exists(out_path):
                try: os.remove(out_path)
                except OSError: pass
            continue
        except Exception as exc:
            logger.error('Erro inesperado gerando %s: %s', label, exc)
            continue

        rel_path = f'lessons/videos/{subdir}/{out_name}'
        Lesson.objects.filter(pk=lesson_pk).update(**{field_name: rel_path})
        logger.info('Aula %s · %s pronta.', lesson_pk, label)


def has_missing_qualities(lesson):
    """True se a aula tem video_file mas falta alguma qualidade adaptativa."""
    if not lesson.video_file:
        return False
    for _, _, _, _, field_name, _ in QUALITY_SPECS:
        if not getattr(lesson, field_name):
            return True
    return False


def trigger_async(lesson_pk):
    """Dispara a transcodificação em thread daemon (não bloqueia a request)."""
    t = threading.Thread(target=_transcode_missing, args=(lesson_pk,), daemon=True)
    t.start()
