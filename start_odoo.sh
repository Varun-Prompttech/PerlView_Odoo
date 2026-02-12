#!/bin/bash

# Port to check
PORT=8070

# Find PID of process listening on port 8070
PID=$(ss -tulnp | grep ":$PORT " | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2)

if [ -n "$PID" ]; then
    echo "Stopping existing process on port $PORT (PID: $PID)..."
    kill -9 $PID
    sleep 1
fi

echo "Starting Odoo 18 on port $PORT..."
nohup python3 odoo18/odoo/odoo-bin -c odoo18/config/odoo.dev.conf > odoo_dev.log 2>&1 &

# Save the new PID
PID=$!
echo $PID > odoo.pid

echo "SUCCESS: Odoo started with PID $PID."
echo "Logs: tail -f odoo_dev.log"
