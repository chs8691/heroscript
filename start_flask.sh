#!/bin/bash
source venv/bin/activate
export FLASK_APP=heroWeb.py
export FLASK_ENV=development 
flask run

