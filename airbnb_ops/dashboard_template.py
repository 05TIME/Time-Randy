"""Minimal mobile-friendly HTML for the Airbnb command center."""


def render_command_center(state: dict) -> str:
    def money(value):
        return f"₦{Decimal(str(value)):,.0f}"

    from decimal import Decimal
    cards = [
        ("Occupancy", f"{Decimal(str(state['occupancy_percent'])) * 100:.0f}%"),
        ("Gross Revenue", money(state["gross_revenue"])),
        ("Net Result", money(state["net_operating_result"])),
        ("Outstanding", money(state["outstanding_obligation"])),
        ("Debt Nights", str(state["debt_clearing_nights"])),
        ("Turnovers", str(state["upcoming_turnovers"])),
        ("Ready", str(state["turnovers_ready"])),
        ("Escalated", str(state["turnovers_escalated"])),
        ("Low Stock", str(state["low_inventory_items"])),
        ("Maintenance", str(state["open_maintenance_issues"])),
    ]
    cards_html = "".join(
        f'<section class="card"><small>{label}</small><strong>{value}</strong></section>'
        for label, value in cards
    )
    return f"""<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TIMEŒ Airbnb Command Center</title>
<style>
body{{margin:0;background:#101010;color:#eee;font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:18px}}
h1{{font-size:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px}}
.card{{background:#1b1b1b;border:1px solid #333;border-radius:14px;padding:16px;min-height:70px}}
small{{display:block;color:#aaa;margin-bottom:10px}}strong{{font-size:22px}}
.warn{{border-color:#8b6f00}}.critical{{border-color:#a33}}
</style></head><body><h1>TIMEŒ Airbnb Ops</h1>
<p>Lekki Phase 1 · Business Command Center</p><div class="grid">{cards_html}</div>
</body></html>"""
