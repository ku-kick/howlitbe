
DEST="mininet@192.168.138.129"
rsync -zarv --include *sh --exclude *.deb --exclude .git --exclude venv . $DEST:~/Documents/PROJECT-Containernet/network-scripts
