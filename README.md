# Task Overview

This financial trading application handles millions of trades, portfolio aggregations, and regulatory audit logs. While the FastAPI APIs are operational, the app struggles with severe database bottlenecks—portfolio queries are slow, audit retrievals time out, and nightly risk calculations overwhelm the system. All endpoints and business logic are in place; the main challenge is to optimize the Postgres schema and async DB logic for high throughput, real-time compliance, and minimal event-loop blocking.

# Guidance
- Multiple tables (trades, portfolios, market_data, audit_logs) have millions of rows and complex relations, but normalization and indexing are suboptimal, harming reporting and logging.
- Some endpoints block the event loop due to sync DB operations or inefficient bulk-processing patterns. Audit/event writes in background tasks may not be truly async-safe or transactional.
- Identify and fix: table/index design for analytic and OLTP workloads; async-safe background auditing; concurrency and isolation in batch reporting; missing keys or poor foreign key structure affecting data consistency and performance.
- If there are any obvious bugs, fix them! 

# Database Access
- Host: <DROPLET_IP>
- Port: 5432
- Database: tradingdb
- Username: traderadmin
- Password: tradepass2024

You may use any SQL/Postgres client (psql, pgAdmin, DBeaver, etc.) for query tuning and schema inspection. 

# Objectives
- See if you can implement normalization of all the schemas for all core models, ensuring keys and relationships are efficient for querying and batch processing.
- Refactor all database access (including background tasks) to async-safe patterns using SQLAlchemy’s async ORM or suitable drivers, eliminating event loop blocking.
- Optimize slow endpoints and batch routines by improving queries, appropriate indexing (including on audit and composite keys), and tuning bulk operations for high throughput.
- Implement or improve audit logging to guarantee compliance—no missed data, transactional integrity for all audit events.
- Validate improvements by benchmarking critical endpoints and demonstrating proper concurrency/safety with read/write workloads.

# How to Verify
- Confirm API endpoints for reporting and audit retrieval return within 2s on large datasets, demonstrating async DB operations (no blocking detected).
- Use EXPLAIN ANALYZE to show efficient execution plans on all major joins and aggregates; indexes are used, no sequential scans on large tables.
- Demonstrate that audit/event logs are correctly persisted and linked for all trades/portfolio updates even during heavy batch processing.
