# Mock WMS Database — Boxleo-Style Operations Queries

A SQLite database modeling a simplified pan-African e-commerce fulfillment operation (inspired by Boxleo Courier's real multi-country structure), with 10 SQL queries answering the kinds of questions a warehouse or operations manager actually asks day to day.

## Why this exists

Most people learning supply chain understand the *concepts* — inventory, fulfillment, delivery performance — but can't query the data those concepts actually live in. This project is the missing link: a realistic (if simplified) relational schema, populated with mock data that mirrors real operational patterns, queried with SQL a working analyst would actually write.

## Schema

- **merchants** — the businesses being served, their country, and their region manager
- **inventory** — SKUs per merchant, which warehouse holds them, current quantity, and reorder point
- **orders** — 120 mock orders across 4 countries (Kenya, Uganda, Tanzania, South Africa) and 4 statuses (delivered, delayed, pending, cancelled)
- **shipments** — delivery tracking per order, including promised vs. actual delivery dates

The data is deliberately modeled with hub countries (Kenya, South Africa) getting faster base transit times than spoke countries (Uganda, Tanzania) — reflecting the real hub-and-spoke delivery pattern found in earlier analysis of Boxleo's actual operations.

## The 10 queries (`ops_queries.sql`)

1. Stockout risk — SKUs at or below reorder point
2. Delayed orders by country
3. Overall on-time delivery rate
4. On-time delivery rate by country (tests whether the hub-vs-spoke delivery gap shows up in the data)
5. Revenue by merchant
6. Order volume by region manager
7. Unshipped order backlog by warehouse
8. Average order value by country
9. Fully out-of-stock SKUs
10. Cancellation rate by merchant

## An honest note on the data

Query 4 didn't cleanly reproduce the "hub countries deliver faster" pattern in every run — with only 13-24 delivered orders per country, random variance can outweigh the underlying signal. That's a real, common issue with small datasets, not a flaw to hide: a real analyst reports what the data actually shows, including when sample size limits how much you can conclude, rather than forcing the result to match the expected story.

## How to use it

Open `boxleo_mock_wms.db` with any SQLite client (e.g., DB Browser for SQLite, or `sqlite3` on the command line / `python3 -m sqlite3`), and run the queries in `ops_queries.sql` against it. Modify the mock data generation logic to test different scenarios if you want to extend it.

## Status

v1 — Python-generated mock data + hand-written SQL queries. A natural next step would be visualizing query 4's output (on-time rate by country) as a chart, or connecting this schema to the driver scorecard project for a combined analysis.
