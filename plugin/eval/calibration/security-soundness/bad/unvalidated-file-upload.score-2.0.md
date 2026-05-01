# Code Sample — Unsafe file upload

```python
"""Unsafe file upload with multiple vulnerabilities."""

from flask import request, send_file


@app.route('/upload', methods=['POST'])
def upload_file():
    # Issue 1: No file type validation
    file = request.files['file']
    
    # Issue 2: No filename sanitization
    filename = file.filename  # User-controlled
    
    # Issue 3: Predictable path
    filepath = f"/uploads/{filename}"
    
    # Issue 4: Directory traversal possible
    # User could upload "../../../etc/passwd" or similar
    file.save(filepath)
    
    # Issue 5: Serve uploaded files directly (RCE if .php, .exe, etc.)
    return send_file(filepath)


@app.route('/download/<path:filename>')
def download(filename):
    # Issue 6: No access control
    # Users can guess filenames and download others' files
    return send_file(f"/uploads/{filename}")
```

Threats:
- File type not validated (could upload executable)
- Directory traversal (upload to parent directories)
- Remote code execution (serve .php as executable)
- File access control missing (anyone can download any file)
- Filename enumeration (guessing filenames works)
