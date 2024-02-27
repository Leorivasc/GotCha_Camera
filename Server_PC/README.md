# To add as a service:

Create the file: 

```
/etc/systemd/system/gotchaweb.service
```

With the followig content and adapt <path_to>, <user> and <group> to fit your setup

```
[Unit]
Description=GotCha Web Service
After=multi-user.target

[Service]
Type=idle

WorkingDirectory=<Path to>/Server_PC

#Two paths here, the one pointing to libraries, the other for executables (gunicorn)
Environment="PATH=<path_to>/VENV/lib/python3.11/site-packages:<path_to/VENV/bin"


ExecStart=<path_to>/VENV>/bin/python3 <path_to>/Server_PC/launch.py
Restart=always
User=<user>
Group=<group>

[Install]
WantedBy=multi-user.target

```

Then run:

```
sudo systemctl enable gotchaweb
sudo systemctl start gotchaweb
```

To apply changes:

```
sudo systemctl daemon-reload
```


