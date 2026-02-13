
import logging
_logger = logging.getLogger(__name__)

def run_debug():
    print("\n--- DEBUGGING KDS CONFIGURATION ---\n")
    
    # 1. Check if module is installed
    module = env['ir.module.module'].search([('name', '=', 'pos_preparation_display'), ('state', '=', 'installed')])
    if not module:
        print("ERROR: pos_preparation_display module is NOT installed!")
        return
    print("SUCCESS: pos_preparation_display module is installed.")

    # 2. Check Preparation Displays
    displays = env['pos_preparation_display.display'].search([])
    print(f"Found {len(displays)} Preparation Displays.")
    
    kiosk_configs = env['pos.config'].search([('name', 'ilike', 'Kiosk')])
    if not kiosk_configs:
         # Fallback to checking all configs
         kiosk_configs = env['pos.config'].search([])
         print(f"Warning: No explicit 'Kiosk' config found. checking all {len(kiosk_configs)} configs.")

    for display in displays:
        print(f"\nDisplay: {display.name} (ID: {display.id})")
        print(f"  Linked POS Configs: {display.pos_config_ids.mapped('name')}")
        print(f"  Categories: {display.category_ids.mapped('name')}")
        
    # 3. Check Last Order
    last_order = env['pos.order'].search([], order='id desc', limit=1)
    if not last_order:
        print("\nNo POS Orders found.")
        return
        
    print(f"\nLast Order: {last_order.name} (ID: {last_order.id})")
    print(f"  Config: {last_order.config_id.name}")
    print(f"  Date: {last_order.date_order}")
    print(f"  State: {last_order.state}")
    print(f"  Lines: {len(last_order.lines)}")
    
    # Check if this order's config is in any display
    linked_displays = env['pos_preparation_display.display'].search([('pos_config_ids', 'in', last_order.config_id.id)])
    print(f"  Displays explicitly linked to this order's POS ({last_order.config_id.name}): {linked_displays.mapped('name')}")
    
    # Check if any display has NO config (implies ALL)
    global_displays = env['pos_preparation_display.display'].search([('pos_config_ids', '=', False)])
    print(f"  Displays linked to ALL POS: {global_displays.mapped('name')}")
    
    if not linked_displays and not global_displays:
        print("FAIL: The POS Config for the last order is NOT linked to any Preparation Display!")
    
    # 4. Check if KDS Order exists
    kds_order = env['pos_preparation_display.order'].search([('pos_order_id', '=', last_order.id)])
    print(f"\nKDS Order Entry Found: {bool(kds_order)}")
    if kds_order:
        print(f"  KDS Order ID: {kds_order.id}")
        print(f"  Displayed: {kds_order.displayed}")
        print(f"  Order Lines: {len(kds_order.preparation_display_order_line_ids)}")
        for line in kds_order.preparation_display_order_line_ids:
            print(f"    - {line.product_id.name}: {line.product_quantity} (Topic: {line.internal_note})")
            
    # 5. Try triggering manually
    print("\nAttempting to trigger process_order manually...")
    try:
        env['pos_preparation_display.order'].process_order(last_order.id)
        print("Manual process_order call finished without error.")
        
        # Re-check
        kds_order = env['pos_preparation_display.order'].search([('pos_order_id', '=', last_order.id)])
        print(f"Post-trigger KDS Order Entry Found: {bool(kds_order)}")
        if kds_order:
             print(f"  Order Lines: {len(kds_order.preparation_display_order_line_ids)}")
    except Exception as e:
        print(f"ERROR calling process_order: {e}")

run_debug()
