#!/usr/bin/env python3
"""
WSGI Entrypoint for Gunicorn
Project: AWS VPC – Public and Private Subnet Demonstration
"""

from app import app

if __name__ == "__main__":
    app.run()

