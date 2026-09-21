"""
Connects Project 4 (mock WMS database) to Project 6 (inventory optimizer).

Pulls real per-SKU order history from the database, calculates actual
average daily demand and its variability, feeds that into the EOQ /
safety stock / reorder point formulas, and compares the CALCULATED
reorder point against the STORED reorder point in the inventory table
(which was assigned arbitrarily when the mock data was first generated
on Day 18 — before any real demand data existed for it to be based on).

This mirrors a real, common analyst task: auditing whether a system's
stored reorder points still make sense given actual observed demand.
"""

import sqlite3
import statistics
from datetime import datetime
from inventory_optimizer import economic_order_quantity, safety_stock, reorder_point

import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boxleo_mock_wms.db")

# Assumed cost inputs — the mock schema has no supplier/warehousing cost data,
# so these are illustrative placeholders, clearly flagged as assumptions, not
# real sourced costs (same discipline as flagging estimates vs. verified facts
# throughout this project).
ASSUMED_ORDER_COST = 15       # $ per replenishment order placed
ASSUMED_HOLDING_COST = 2.5    # $ per unit per year
TARGET_SERVICE_LEVEL = 0.95

# Observation window used to build demand history (matches the mock order dates)
WINDOW_START = datetime(2026, 8, 1)
WINDOW_END = datetime(2026, 9, 14)
WINDOW_DAYS = (WINDOW_END - WINDOW_START).days

# Hub vs spoke lead times, consistent with the Day 3/12 hub-and-spoke finding
HUB_COUNTRIES = {"Kenya", "South Africa"}
LEAD_TIME_HUB = 3
LEAD_TIME_SPOKE = 6


def get_sku_demand_history(cur):
    """Returns {sku_id: {day: total_qty_sold}} across the observation window."""
    query = """
    SELECT oi.sku_id, o.order_date, SUM(oi.quantity)
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != 'cancelled'
    GROUP BY oi.sku_id, o.order_date
    """
    history = {}
    for sku_id, order_date, qty in cur.execute(query):
        history.setdefault(sku_id, {})[order_date] = qty
    return history


def daily_series(day_totals):
    """Fills in zero-demand days so std dev reflects true variability, not just active days."""
    series = []
    d = WINDOW_START
    while d <= WINDOW_END:
        key = d.strftime("%Y-%m-%d")
        series.append(day_totals.get(key, 0))
        d = d.replace(day=d.day)  # placeholder, incremented below
        d = datetime.fromordinal(d.toordinal() + 1)
    return series


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    demand_history = get_sku_demand_history(cur)
    skus = cur.execute(
        "SELECT sku_id, product_name, warehouse_location, quantity, reorder_point FROM inventory"
    ).fetchall()

    results = []
    for sku_id, name, warehouse, current_qty, stored_rop in skus:
        day_totals = demand_history.get(sku_id, {})
        series = daily_series(day_totals)
        total_sold = sum(series)

        if total_sold == 0:
            # No sales recorded in this window — not enough data to calculate demand stats
            results.append((name, warehouse, stored_rop, None, "no sales data in window"))
            continue

        avg_daily = statistics.mean(series)
        std_daily = statistics.pstdev(series) if len(series) > 1 else 0
        annual_demand = avg_daily * 365

        # hub vs spoke lead time, based on the warehouse location's country
        is_hub = any(h in warehouse for h in ["Nairobi", "Johannesburg"])
        lead_time = LEAD_TIME_HUB if is_hub else LEAD_TIME_SPOKE

        eoq = economic_order_quantity(max(annual_demand, 1), ASSUMED_ORDER_COST, ASSUMED_HOLDING_COST)
        ss = safety_stock(TARGET_SERVICE_LEVEL, std_daily, lead_time)
        calc_rop = reorder_point(avg_daily, lead_time, ss)

        flag = "OK" if abs(calc_rop - stored_rop) <= 5 else "MISMATCH"
        results.append((name, warehouse, stored_rop, round(calc_rop, 1), flag))

    conn.close()
    return results


if __name__ == "__main__":
    results = main()
    print(f"{'Product':<15}{'Warehouse':<22}{'Stored ROP':<12}{'Calculated ROP':<16}{'Flag'}")
    print("-" * 80)
    for name, warehouse, stored, calc, flag in results:
        calc_display = calc if calc is not None else "N/A"
        print(f"{name:<15}{warehouse:<22}{stored:<12}{str(calc_display):<16}{flag}")
