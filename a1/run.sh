#!/bin/bash
cd /home/ubuntu/Desktop/ECE1779-CC/a1/
/home/ubuntu/Desktop/ece1779/venv1/bin/gunicorn -b 0.0.0.0:5000 -w 1 app:webapp
