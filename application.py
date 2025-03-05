import os
from pathlib import Path
from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper

def application(environ, start_response):
    # Get the requested path
    path = environ.get('PATH_INFO', '').lstrip('/')
    
    # Default to index.html if no path specified
    if path == '':
        path = 'sunshine/index.html'
    
    # Get file path
    file_path = os.path.join(os.getcwd(), path)
    
    # Check if file exists
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Get file extension for content type
        _, ext = os.path.splitext(file_path)
        content_type = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif',
        }.get(ext.lower(), 'application/octet-stream')
        
        # Send successful response
        start_response('200 OK', [('Content-Type', content_type)])
        
        # Return file content
        with open(file_path, 'rb') as f:
            return FileWrapper(f)
    else:
        # File not found
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'File not found']