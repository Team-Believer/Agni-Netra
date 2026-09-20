# Agni-Netra: Dashboard & UI Checkpoint

This document summarizes the current state of the frontend UI and Dashboard following the Phase 1 and Phase 2 improvement sprints.

## Dashboard Overview
The primary analyst dashboard (`/dashboard`) integrates several key components:
- **KPI Cards**: Displays total active events, high-priority counts, verification queues, and 24h resolution rates.
- **Action Required Queue**: A prominent banner displaying the *single most urgent event* that requires analyst verification, adhering to the strict "one event at a time" review rule.
- **Live Event Map**: Displays spatial distribution of events. Features centralized filtering that syncs with the rest of the dashboard components.
- **Event Detail Panel**: Includes a newly designed "Multi-Sensor Contribution Summary" chart that visually breaks down evidence supporting vs. conflicting with an event.

## Pages & Navigation
- `/dashboard`: Main operational view.
- `/live-map`: Expanded full-screen map view with heatmap and real-time visualization options.
- `/events`: Comprehensive list of all detected anomalies.
- `/analytics`: High-level data visualization on trends and priorities.
- `/facilities`: Directory of inferred industrial facilities and their thermal event history.
- `/reports`: A dedicated export hub for generating structured JSON reports, CSV data dumps, and comprehensive PDF reports for events.
- `/about`: The core mission, methodology, and philosophy of Agni-Netra (Event-Centric Evidence Intelligence, Conformal ML, No-Fake-Data policy).

## Recent Enhancements (Phase 1 & 2)
1. **Centralized Map Filtering**: Map filters (e.g. "Under Verification", "High Priority") are now hoisted to the Dashboard page state and passed down, accurately filtering the map, recent events table, and verification queue.
2. **Facility 404 Resolution**: URL encoding issues preventing navigation to specific facility detail pages have been resolved.
3. **PDF Generation**: Analysts can now generate and download formatted PDF reports directly from the Reports page.
4. **About Page Integration**: The previously orphaned About page is now accessible via the global sidebar.
