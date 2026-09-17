"""
Point d'entrée reconnu automatiquement par Vercel (Python runtime WSGI).
En local, on continue d'utiliser run.py (plus pratique avec le mode debug).
"""
from app import create_app

app = create_app()