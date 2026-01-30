#!/bin/bash
# start_odoo.sh
# Usage: ./scripts/start_odoo.sh [prod|dev] [extra_args]

MODE=${1:-dev}
SHIFT_ARGS=1

CONF_FILE="config/odoo.dev.conf"

if [ "$MODE" == "prod" ]; then
    CONF_FILE="config/odoo.conf"
    echo "Starting Odoo in PRODUCTION mode..."
else
    echo "Starting Odoo in DEVELOPMENT mode..."
fi

# Shift arguments so we can pass the rest to odoo-bin
shift $SHIFT_ARGS

# Path to python interpreter (system default per requirements)
PYTHON_BIN=python3

# Check if odoo-bin exists
if [ ! -f "odoo/odoo-bin" ]; then
    echo "Error: odoo/odoo-bin not found. Are you in the workspace root?"
    exit 1
fi

# Run Odoo
$PYTHON_BIN odoo/odoo-bin -c $CONF_FILE "$@"
