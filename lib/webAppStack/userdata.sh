#!/bin/bash

# Update packages
apt-get update -y

# Install required packages
apt-get install -y ec2-instance-connect git python3-pip python3.8-venv

# Clone repository
cd /home/ubuntu
git clone https://github.com/madebybk/tig-ad-image-studio.git

# Create virtual environment
python3 -m venv --copies /home/ubuntu/my_env
sudo chown -R ubuntu:ubuntu /home/ubuntu/my_env
source /home/ubuntu/my_env/bin/activate

# Install dependencies
cd tig-ad-image-studio/frontend
pip3 install -r requirements.txt

# Create systemd service
sudo sh -c "cat <<EOF > /etc/systemd/system/streamlit.service
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=ubuntu
Environment='AWS_DEFAULT_REGION=us-west-2'
WorkingDirectory=/home/ubuntu/tig-ad-image-studio/frontend
ExecStartPre=/bin/bash -c 'sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501'
ExecStart=/bin/bash -c 'source /home/ubuntu/my_env/bin/activate && streamlit run app.py --server.port 8501 --server.enableXsrfProtection=false'
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd daemon and start the service
systemctl daemon-reload
systemctl enable streamlit
systemctl start streamlit