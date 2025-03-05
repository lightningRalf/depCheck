import os
from pathlib import Path

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')[1:]  # Remove leading slash
    file_path = Path("sunshine") / path
    
    if file_path.is_file():
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            content_type = "application/json" if file_path.suffix == ".json" else "text/html"
            start_response('200 OK', [('Content-Type', content_type)])
            return [data]
        except Exception as e:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [f"Error: {e}".encode()]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'File not found']