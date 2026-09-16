# UI Test Suite Notes

## Execution Syntax
```bash
playwright install chromium
pytest tests/ui -v --browser chromium
```
*Note: Requires the cluster infrastructure to be up via `docker compose up -d`.*

## Quality Strategy Lookups
Every interface element is located exclusively using `data-testid` tags. This layout completely isolates testing verification scripts from changes to styling selectors, structural paths, or XPath attributes, ensuring long-term script reliability.

## Scenario Profiles Matrix
1. Core frame loading operations (Health status loop evaluation).
2. UI Search capabilities mapping existing records.
3. Form ledger updates tracked via API verification endpoints.
4. Error handling routines for absent or false parameter references.
5. Bad credential handling boundaries (401 access locks).
6. Missing account references tracking logic (404 status updates).
