#!/bin/bash
rsync -rva --exclude .git --exclude venv ../howlitbe ubuntu@172.16.79.128:~
