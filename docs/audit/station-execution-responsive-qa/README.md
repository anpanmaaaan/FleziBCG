# Station Execution Responsive Screenshot QA

## Purpose

This QA harness captures responsive screenshots for the Station Execution page to support visual layout review.

This script is visual QA only.
It does not validate backend truth, execution truth, authorization truth, or API contract behavior.

## Script

From the frontend workspace:

~~~bash
npm run qa:station-execution:screenshots
~~~

## Prerequisite

Start the dev server first and keep it running at:

~~~text
http://localhost:5173
~~~

Example:

~~~bash
cd frontend
npm run dev
~~~

Then run the screenshot script in another terminal.

## QA-Only Mocking Policy

The screenshot script uses Playwright route interception with QA-only mock responses defined inside:

frontend/scripts/station-execution-responsive-screenshots.mjs

No QA mock data is imported into production source code.

## Viewports Captured

- 1440 x 900
- 1180 x 820
- 820 x 1180
- 430 x 932

The script captures two visual states per viewport:
- Mode A (empty queue)
- Mode B (cockpit with selected operation)

## Output Location

Screenshots are saved to:

docs/audit/station-execution-responsive-qa/

Expected files:

- station-execution-mode-a-desktop-1440x900.png
- station-execution-mode-a-tablet-landscape-1180x820.png
- station-execution-mode-a-tablet-portrait-820x1180.png
- station-execution-mode-a-narrow-430x932.png
- station-execution-queue-desktop-1440x900.png
- station-execution-queue-tablet-landscape-1180x820.png
- station-execution-queue-tablet-portrait-820x1180.png
- station-execution-queue-narrow-430x932.png
