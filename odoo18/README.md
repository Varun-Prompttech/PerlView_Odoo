# Odoo 18 Enterprise Workspace

This repository contains the source code and configuration for the Odoo 18 Enterprise project.

## Directory Structure

- **odoo/**: Odoo Community Edition source code (upstream).
- **enterprise/**: Odoo Enterprise Edition source code (upstream).
- **addons/custom/**: Company-specific custom modules.
    - `base_extensions`: Core mixins and utilities.
    - `sales`, `accounting`, `hr`: Business-vertical extensions.
- **addons/third_party/**: External community modules (OCA, etc.).
- **config/**: Configuration files (`odoo.conf` for prod, `odoo.dev.conf` for dev).
- **scripts/**: Helper scripts for running and updating Odoo.
- **logs/**: Log storage.

## Development

### Prerequisites
- Python 3.10+
- PostgreSQL
- System dependencies for Odoo (libxml2, libxslt, etc.)

### Getting Started

1.  **Start Odoo in Developer Mode**
    Runs with `dev_mode=all`, no workers, and helpful logging.
    ```bash
    ./scripts/start_odoo.sh
    ```

    Access at: `http://localhost:8069`

2.  **Start Odoo in Production Mode**
    Runs with workers and production resource limits.
    ```bash
    ./scripts/start_odoo.sh prod
    ```

### Managing Custom Addons

New modules should be created in `addons/custom/`.

**Naming Convention:**
- Use `snake_case` for module names.
- Prefix with company tag if applicable (e.g., `cm_sales`).

**Updating Addons:**
To update specific modules (e.g., after editing XML or Python constraints):
```bash
./scripts/update_addons.sh sales,accounting
```

## Configuration

The main configuration is at `config/odoo.conf`.
Development overrides are in `config/odoo.dev.conf`.

**Addons Path Order:**
1. `odoo/addons` (Community)
2. `enterprise` (Enterprise)
3. `addons/third_party`
4. `addons/custom`

This ensures custom modules can properly override or extend base and enterprise functionality.
