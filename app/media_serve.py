"""Отдача /static/ и /media/ с поддержкой Range-запросов.

На сервере файлы отдаёт сам Django (nginx нет, см. project/urls.py), а
django.views.static.serve всегда отвечает файлом целиком. Safari (iPhone,
iPad, Mac) без ответа 206 на Range-запрос видео не воспроизводит — поэтому
видео в Instagram-блоке и в шапке главной на этих устройствах не играли бы.
"""
import re

from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from django.views.static import serve

RANGE_RE = re.compile(r'^bytes=(\d*)-(\d*)$')
CHUNK = 64 * 1024


def _read_range(file, start, length):
    try:
        file.seek(start)
        while length > 0:
            data = file.read(min(CHUNK, length))
            if not data:
                break
            length -= len(data)
            yield data
    finally:
        file.close()


def serve_with_range(request, path, document_root=None, show_indexes=False):
    response = serve(request, path, document_root=document_root, show_indexes=show_indexes)
    if not isinstance(response, FileResponse) or response.status_code != 200:
        return response
    response['Accept-Ranges'] = 'bytes'

    match = RANGE_RE.match(request.headers.get('Range', '').strip())
    if not match or not match.group(1) + match.group(2):
        return response  # нет Range или он в неподдерживаемом виде — отдаём целиком

    size = int(response['Content-Length'])
    first, last = match.groups()
    if first:
        start = int(first)
        end = min(int(last), size - 1) if last else size - 1
    else:  # bytes=-500 — последние 500 байт
        start = max(size - int(last), 0)
        end = size - 1

    if start >= size or start > end:
        response.file_to_stream.close()
        unsatisfiable = HttpResponse(status=416)
        unsatisfiable['Content-Range'] = f'bytes */{size}'
        return unsatisfiable

    length = end - start + 1
    partial = StreamingHttpResponse(
        _read_range(response.file_to_stream, start, length),
        status=206,
        content_type=response['Content-Type'],
    )
    partial['Content-Length'] = str(length)
    partial['Content-Range'] = f'bytes {start}-{end}/{size}'
    partial['Accept-Ranges'] = 'bytes'
    if response.has_header('Last-Modified'):
        partial['Last-Modified'] = response['Last-Modified']
    return partial
