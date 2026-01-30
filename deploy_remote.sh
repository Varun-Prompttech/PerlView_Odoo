#!/bin/bash

# Remote Credentials
HOST="147.93.30.185"
USER="root"
PASS="PTAdmin@151298"
DIR="/opt/odoo"
PROJECT="PerlView_Test"
REPO="https://github.com/Varun-Prompttech/PerlView_Odoo.git"

echo "Deploying to $USER@$HOST..."

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST "bash -s" << EOF
    set -e
    
    # 1. Kill Existing Processes
    echo "Stopping existing processes for $PROJECT..."
    pkill -f "$DIR/$PROJECT" || echo "No processes running."
    sleep 2

    # 2. Setup Directory
    echo "Creating directory structure..."
    mkdir -p $DIR
    cd $DIR

    # 2. Git Operations
    if [ -d "$PROJECT" ]; then
        echo "Updating existing repository..."
        cd $PROJECT
        git pull
    else
        echo "Cloning repository..."
        git clone $REPO $PROJECT
        cd $PROJECT
    fi

    # 3. Find Safe Port (Starting 8070)
    # checking PORT and PORT+1 (for gevent)
    PORT=8070
    while netstat -atn | grep -q ":\$PORT " || netstat -atn | grep -q ":\$((PORT+1)) "; do
        echo "Port \$PORT or \$((PORT+1)) is busy, trying next..."
        ((PORT+=2))
    done
    echo "Selected Port: \$PORT (HTTP) and \$((PORT+1)) (Gevent)"

    # 4. Setup Python Environment (Optional but recommended)
    # Checking if python3-venv is available or if we should use system python
    # For speed/robustness in this specific request, we will try to use a venv, 
    # but fall back to system python if venv creation fails.
    
    if python3 -m venv .venv; then
        echo "Using virtual environment..."
        source .venv/bin/activate
        # Attempt to install requirements if pip is available
        if [ -f "odoo18/odoo/requirements.txt" ]; then
             echo "Installing requirements from odoo18/odoo/requirements.txt..."
             pip install -r odoo18/odoo/requirements.txt || echo "Warning: Pip install failed"
        fi
    else
        echo "Virtualenv creation failed, using system python..."
    fi

    # 5. Start Odoo
    # We use nohup to keep it running.
    # We point to the odoo-bin. Based on repo structure: odoo18/odoo/odoo-bin
    
    BIN_PATH="odoo18/odoo/odoo-bin"
    CONF_PATH="odoo18/config/odoo.conf"
    
    # If conf file doesn't exist, we might need to rely on CLI args entirely or touch it.
    if [ ! -f "\$CONF_PATH" ]; then
        CONF_PATH="/dev/null" 
    fi
    
    EXTRA_ARGS=""
    if [ "$1" == "init" ]; then
        echo "Initializing database with base modules..."
        EXTRA_ARGS="-i base"
    fi

    echo "Starting Odoo..."
    nohup python3 \$BIN_PATH -c \$CONF_PATH --http-port=\$PORT --gevent-port=\$((PORT+1)) --db_host=localhost --db_user=odoo --db_password=odoo \$EXTRA_ARGS > odoo_\$PORT.log 2>&1 &
    
    PID=\$!
    echo "Odoo started on port \$PORT with PID \$PID"
    echo "Log file: \$(pwd)/odoo_\$PORT.log"
    
    # Verify immediate crash
    sleep 3
    if ps -p \$PID > /dev/null; then
        echo "SUCCESS: Process is running."
    else
        echo "ERROR: Process died immediately. Checking last 10 lines of log:"
        tail -n 10 odoo_\$PORT.log
        exit 1
    fi
EOF
