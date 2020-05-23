#!/bin/bash
pkg install python
python3 -m venv ~/heroscript/venv
~/heroscript/venv/bin/pip install -r ~/heroscript/venv/reqirements.txt
~/heroscript/venv/bin/pip install stravalib


