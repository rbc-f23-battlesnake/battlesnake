# How to set up a service to run always (ubuntu)

```
cd /etc/systemd/system
vi battlesnake.service
```

Insert

```
[Unit]
Description=Battlesnake Service
After=multi-user.target
[Service]
Type=simple
Restart=always
RestartSec=0
ExecStart=/usr/bin/python3.11 /root/code/battlesnake/main.py >/dev/null 2>&1
[Install]
WantedBy=multi-user.target
```

Start service

```
loginctl enable-linger
sudo systemctl daemon-reload

sudo systemctl enable battlesnake.service
sudo systemctl start battlesnake.service
```

Helpful commands

```
sudo systemctl stop battlesnake.service
sudo systemctl restart battlesnake.service
sudo systemctl status battlesnake.service


```