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
    
    # Identify existing process
    PID=\$(ss -tulnp | grep ":$PORT " | awk '{print \$7}' | cut -d',' -f2 | cut -d'=' -f2)
    
    if [ -n "\$PID" ]; then
        echo "Stopping existing process on port $PORT (PID: \$PID)..."
        kill -9 \$PID
        sleep 1
    fi

    echo "Starting Odoo on remote port $PORT..."
    # Using python3 from venv if exists, else system python
    PYTHON_CMD="python3"
    if [ -f ".venv/bin/python3" ]; then
        PYTHON_CMD=".venv/bin/python3"
    fi

    nohup \$PYTHON_CMD odoo18/odoo/odoo-bin -c odoo18/config/odoo.conf --http-port=$PORT > odoo_remote.log 2>&1 &
    
    NEW_PID=\$!
    echo "SUCCESS: Odoo started on remote with PID \$NEW_PID"
    echo "Remote Log: $DIR/odoo_remote.log"
EOF
