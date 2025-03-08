#!/bin/bash
rsync -rva --exclude .git --exclude venv ../howlitbe ubuntu@192.168.138.140:~
