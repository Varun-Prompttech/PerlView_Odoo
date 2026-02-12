#!/bin/bash

# Remote Credentials
HOST="147.93.30.185"
USER="root"
PASS="PTAdmin@151298"
DIR="/opt/odoo/PerlView_Test"
PORT=8070

echo "Connecting to remote server $HOST..."

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST "bash -s" << EOF
    cd $DIR
    
    # Kill all processes related to this Odoo instance/directory
    echo "Cleaning up all existing Odoo processes for $DIR..."
    pkill -9 -f "$DIR" || echo "No processes found."
    
    # Also specifically free the port if anything remains
    PORT_PID=\$(ss -tulnp | grep ":$PORT " | awk '{print \$7}' | cut -d',' -f2 | cut -d'=' -f2)
    if [ -n "\$PORT_PID" ]; then
        echo "Forcing kill on port $PORT (PID: \$PORT_PID)..."
        kill -9 \$PORT_PID
    fi
    sleep 2

    echo "Starting Odoo on remote port $PORT..."
    # Using python3 from venv if exists, else system python
    PYTHON_CMD="python3"
    if [ -f ".venv/bin/python3" ]; then
        PYTHON_CMD=".venv/bin/python3"
    fi

    nohup \$PYTHON_CMD odoo18/odoo/odoo-bin -c odoo18/config/odoo.conf --db_host=localhost --db_password=prompttech --http-port=$PORT > odoo_remote.log 2>&1 &
    
    NEW_PID=\$!
    echo "SUCCESS: Odoo started on remote with PID \$NEW_PID"
    echo "Remote Log: $DIR/odoo_remote.log"
EOF
