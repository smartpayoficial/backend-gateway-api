#!/bin/bash

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies con paquete de pruebas
pip install -r requirements.txt
