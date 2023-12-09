To add as a service:

create the file: 

```
/etc/systemd/system/gotchacam.service
```

With the followig content:

```
[Unit]
Description=GotCha Camera Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/leo/VENV/bin/python3 /home/leo/CamTests/camera/stream_server_led.py
Restart=always
User=leo

[Install]
WantedBy=multi-user.target

```

Then run:

sudo systemctl enable gotchacam
sudo systemctl start gotchacam
