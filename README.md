# GitLab Events Listener
GitLab notification listener. This Service will send you emails about GitLab actions.

Preparation:
1. Open GitLab Dashboard.
2. Select the Groups and choose the Project.
3. Select Secure and Audit Events.
4. Select Streams
5. Click "Add streaming destination"
6. Select HTTP Endpoint
7. Destination URL - insert URL that is used for listening. Example https://events.myserver.com/
8. Custom HTTP headers push Add header. Set Header = Content-Type, Value = application/json
9. After, save the "Verification token"
10. Replace "Verification token" in gitlab_events_listener.py
11. Replace the mail server address and passwords in "gitlab_events_listener.py" in Variables section
12. Deploy "gitlab_events_listener.py" on your server
13. Run with "python3 gitlab_events_listener.py"

To protect your data - install NGNX with LetsEncrypt with free-to-use certificates.
Replace "user" with your account names
Replace /home/events path with a real path to events_listener.py

# NGINX with Let's Encrypt SSL Setup for Event Listener Service

This guide covers setting up an NGINX service with Let's Encrypt SSL certificates to secure the communication channel for a GitLab events listener service.

## Prerequisites

- A Linux server with root or sudo privileges
- Domain name pointing to your server (e.g., `https://events.myserver.com/`)
- Python application "gitlab_events_listener.py" ready to be hosted on `127.0.0.1:5000`

## Setup Instructions

### Step 1: Install NGINX and Certbot

First, update your package list and install NGINX and Certbot using the following commands:

```bash
sudo apt update
sudo apt install nginx
sudo apt install certbot python3-certbot-nginx
```

### Step 2: Configure NGINX

Edit the NGINX default configuration file:

```bash
sudo vim /etc/nginx/sites-available/default
```

Replace its contents with the following configuration:

```nginx
server {
    listen 80;
    server_name events.myserver.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        send_timeout 60s;
    }
}
```

### Step 3: Restart NGINX

Apply the changes by restarting NGINX:

```bash
sudo systemctl restart nginx
```

### Step 4: Obtain and Install SSL Certificate

Use Certbot to obtain an SSL certificate for your domain:

```bash
sudo certbot --nginx -d events.myserver.com
```

Follow the prompts to complete the SSL certificate installation.

### Step 5: Restart NGINX Again

Restart NGINX to ensure all changes are applied:

```bash
sudo systemctl restart nginx
```

### Step 6: Create Systemd Service for the Application

Create a service file for your Python events listener application:

```bash
sudo vim /etc/systemd/system/events-listener.service
```

Enter the following content:

```ini
[Unit]
Description=Python Events Listener Service
After=network.target

[Service]
ExecStart=/home/events/venv/bin/python /home/events/events_listener.py
WorkingDirectory=/home/events
Environment="PATH=/home/events/venv/bin"
StandardOutput=append:/var/log/events_listener.log
StandardError=append:/var/log/events_listener.log
Restart=always
User=user
Group=user

[Install]
WantedBy=multi-user.target
```

### Step 7: Reload Systemd and Start the Service

Reload the systemd daemon and start your service:

```bash
sudo systemctl daemon-reload
sudo systemctl start events-listener.service
```

Enable the service to start on boot:

```bash
sudo systemctl enable events-listener.service
```

### Step 8: Setup Log File and Permissions

Create a log file for the service and set proper permissions:

```bash
sudo touch /var/log/events_listener.log
sudo chown user:user /var/log/events_listener.log
```

### Step 9: Configure Log Rotation

Create a logrotate configuration for the log file:

```bash
sudo vim /etc/logrotate.d/events_listener
```

Add the following rotation configuration:

```plaintext
/var/log/events_listener.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 user user
    postrotate
    sudo systemctl reload events-listener.service > /dev/null 2>&1 || true
    endscript
}
```

Test the log rotation setup:

```bash
logrotate -d /etc/logrotate.d/events_listener
```

### Conclusion

Your NGINX server is now set up with an SSL certificate to secure your events listener service. The application is managed as a systemd service with proper logging and log rotation configurations.

Please ensure you periodically check the service status and logs to maintain the security and performance of your server.
