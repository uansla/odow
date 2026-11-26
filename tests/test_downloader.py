import threading
import pytest
from odow.downloader import QUALITY_FORMATS, build_options, is_supported_video_url

@pytest.mark.parametrize("url", ["https://www.youtube.com/watch?v=x", "https://youtu.be/x", "https://www.bilibili.com/video/BV1xx411c7mD", "https://b23.tv/abc"])
def test_supported_video_sites(url):
    assert is_supported_video_url(url)

def test_rejects_non_video_domains():
    assert not is_supported_video_url("https://youtube.com.example.org/watch?v=x")
    assert not is_supported_video_url("file:///etc/passwd")

def test_quality_options_cover_video_and_audio(tmp_path):
    for quality in QUALITY_FORMATS:
        options=build_options(str(tmp_path),quality)
        assert options['format'] and options['outtmpl'].startswith(str(tmp_path))
    assert '1080' in QUALITY_FORMATS['1080p max']
    assert 'postprocessors' not in build_options(str(tmp_path),'Best available')
    assert build_options(str(tmp_path),'Audio only (MP3)')['postprocessors'][0]['preferredcodec']=='mp3'

def test_cookie_file_is_passed_to_ytdlp(tmp_path):
    assert build_options(str(tmp_path),'720p max','/tmp/cookies.txt')['cookiefile']=='/tmp/cookies.txt'

def test_cancel_hook_raises_download_cancelled(tmp_path):
    from yt_dlp.utils import DownloadCancelled
    event=threading.Event(); event.set()
    hook=build_options(str(tmp_path),'Best available',cancel_event=event)['progress_hooks'][-1]
    with pytest.raises(DownloadCancelled): hook({'status':'downloading'})

def test_unknown_quality_is_rejected(tmp_path):
    with pytest.raises(ValueError,match='Unsupported quality'): build_options(str(tmp_path),'unlimited')
