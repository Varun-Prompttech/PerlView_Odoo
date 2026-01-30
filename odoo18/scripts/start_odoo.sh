#!/bin/bash
# start_odoo.sh
# Usage: ./scripts/start_odoo.sh [prod|dev] [extra_args]

MODE=${1:-dev}
SHIFT_ARGS=1

CONF_FILE="odoo18/config/odoo.dev.conf"

if [ "$MODE" == "prod" ]; then
    CONF_FILE="odoo18/config/odoo.conf"
    echo "Starting Odoo in PRODUCTION mode..."
else
    echo "Starting Odoo in DEVELOPMENT mode..."
fi

# Shift arguments so we can pass the rest to odoo-bin
shift $SHIFT_ARGS

# Path to python interpreter (system default per requirements)
PYTHON_BIN=odoo18/.venv/bin/python3
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Virtualenv python not found, trying system python..."
    PYTHON_BIN=python3
fi

# Check if odoo-bin exists
if [ ! -f "odoo18/odoo/odoo-bin" ]; then
    echo "Error: odoo18/odoo/odoo-bin not found. Are you in the workspace root?"
    exit 1
fi

echo "DEBUG: Using Python: $PYTHON_BIN"
$PYTHON_BIN --version
$PYTHON_BIN -c "import sys; print(sys.path)" || echo "Failed to print sys.path"
$PYTHON_BIN -c "import babel; print(babel.__file__)" || echo "Failed to import babel"

# Run Odoo
$PYTHON_BIN odoo18/odoo/odoo-bin -c $CONF_FILE "$@"
