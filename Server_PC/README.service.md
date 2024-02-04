# To add as a service:

Create the file: 

```
/etc/systemd/system/gotchacam.service
```

With the followig content and modify to fit your setup

```
[Unit]
Description=GotCha Web Service
After=multi-user.target

[Service]
Type=idle

WorkingDirectory=<Path to>/Server_PC

#Two paths here, the one pointing to libraries, the other for executables (gunicorn)
Environment="PATH=<Path to VENV>/lib/python3.11/site-packages:<Path to VENV>/bin"


ExecStart=<Path to VENV>/bin/python3 <Path to>/Server_PC/launch.py
Restart=always
User=leo
Group=leo

[Install]
WantedBy=multi-user.target

```

Then run:

```
sudo systemctl enable gotchacam
sudo systemctl start gotchacam
```

To apply changes:

```
sudo systemctl daemon-reload
```


