#!/bin/bash
# update_addons.sh
# Usage: ./scripts/update_addons.sh <modules_to_update>
# Example: ./scripts/update_addons.sh sales,custom_module_a

MODULES=$1

if [ -z "$MODULES" ]; then
    echo "Error: No modules specified."
    echo "Usage: ./scripts/update_addons.sh <comma_separated_modules>"
    exit 1
fi

echo "Updating modules: $MODULES"

# Re-use start_odoo.sh to run the update
./scripts/start_odoo.sh dev -u "$MODULES" --stop-after-init
