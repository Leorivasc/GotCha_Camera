# To add as a service:

Create the file: 

```
/etc/systemd/system/gotchacam.service
```

With the followig content and modify to fit your setup

```
[Unit]
Description=GotCha Camera Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/<your_path_to_venv>/VENV/bin/python3 /<path_to_script>/camera/stream_server_led.py
Restart=always
User=<user>

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


