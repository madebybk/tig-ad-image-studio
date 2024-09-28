#!/bin/bash

# Update packages
sudo apt-get update -y
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y ec2-instance-connect
sudo apt-get install -y git
sudo apt-get install -y python3-pip
sudo apt-get install -y python3.8-venv

# Clone repository
cd /home/ubuntu
git clone https://github.com/madebybk/tig-ad-image-studio.git

# Create and activate virtual environment
python3 -m venv /home/ubuntu/streamlit_env
source /home/ubuntu/streamlit_env/bin/activate

# Install dependencies
cd tig-ad-image-studio/frontend
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/streamlit.service > /dev/null <<EOF
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=ubuntu
Environment="PATH=/home/ubuntu/streamlit_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="AWS_DEFAULT_REGION=us-west-2"
WorkingDirectory=/home/ubuntu/tig-ad-image-studio/frontend
ExecStartPre=/bin/bash -c 'sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501'
ExecStart=/home/ubuntu/streamlit_env/bin/python -m streamlit run app.py --server.port 8501 --server.enableXsrfProtection=false
Restart=always
StandardOutput=append:/var/log/streamlit.log
StandardError=append:/var/log/streamlit.log

[Install]
WantedBy=multi-user.target
EOF

# Create log file and set permissions
sudo touch /var/log/streamlit.log
sudo chown ubuntu:ubuntu /var/log/streamlit.log

# Reload systemd daemon and start the service
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
