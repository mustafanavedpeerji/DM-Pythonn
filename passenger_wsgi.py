import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from main import app

# ASGI to WSGI adapter for FastAPI
try:
    from asgiref.wsgi import WsgiToAsgi
    application = WsgiToAsgi(app)
except ImportError:
    # If asgiref not available, try a2wsgi
    try:
        from a2wsgi import ASGIMiddleware
        application = ASGIMiddleware(app)
    except ImportError:
        # Fallback - this might not work perfectly with FastAPI
        application = app