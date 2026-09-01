# Salesforce Experience Site Playwright Framework

Python + pytest + Playwright smoke automation scaffold for the Salesforce Experience Cloud site:

- Default base URL: `https://tdlrgov--qa2.sandbox.my.site.com/s/`
- Framework style: Page Object Model
- Focus: public / unauthenticated smoke coverage

## Project Structure

```text
.
├── pages/
│   ├── base_page.py
│   ├── home_page.py
│   └── search_license_page.py
├── tests/
│   ├── conftest.py
│   └── test_public_smoke.py
├── utils/
│   ├── config.py
│   └── waits.py
├── artifacts/
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

## What was inspected on the target site

The site was inspected headlessly and appears to behave as follows:

- Visiting `/s/` redirects unauthenticated users to a public login page.
- The login page still exposes public content such as:
  - `Welcome to TDLR CORE`
  - `Log In: TDLR CORE License Management`
  - navigation to `Find a License`
- The `Find a License` page is publicly reachable at:
  - `/s/search-license-permit-holder`
- That page includes a public search form with fields for license type, license number, issue/expiration dates, licensee name, city, county, zip, plus `Search` and `Reset` buttons.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install
```

3. Optionally create a `.env` file from `.env.example`.

## Run tests

Run all smoke tests:

```bash
pytest tests/test_public_smoke.py -m smoke
```

Run headed locally if desired:

```bash
HEADLESS=false pytest tests/test_public_smoke.py -m smoke
```

Override the base URL:

```bash
BASE_URL=https://your-salesforce-site.example.com/s/ pytest -m smoke
```

## Design notes

- `utils/config.py` centralizes environment-based configuration.
- `utils/waits.py` adds Salesforce-friendly waits for LWC/Experience Cloud rendering.
- `pages/` contains reusable page objects.
- `tests/conftest.py` provides Playwright browser/page fixtures and failure screenshots.

## Implemented smoke tests

1. Home route redirects to login and shows expected public content.
2. Public nav from login/home to `Find a License` works.
3. Public `Find a License` search form renders key fields.
4. `Reset` clears user-entered values in the public search form.
5. Footer/legal/contact content is visible on a public page.

## Notes about Salesforce/LWC selectors

Where possible, selectors prefer:

- ARIA labels / roles
- visible button/link text
- stable text blocks

Some Salesforce-generated inputs do not expose durable labels for every field, so the page object uses a small amount of positional mapping for currently visible text inputs. If the org markup changes, update those locators in `pages/search_license_page.py` only.

## Adding authenticated flows later

If login automation is needed later:

1. Add a `LoginPage` object under `pages/`.
2. Store credentials in environment variables, not in source.
3. Prefer a dedicated non-MFA automation user in lower environments.
4. Consider Playwright storage state for session reuse after interactive login.
5. Add separate tests marked with `@pytest.mark.auth` so public smoke remains runnable without credentials.

Suggested env vars already scaffolded:

- `LOGIN_USERNAME`
- `LOGIN_PASSWORD`

## Assumptions / limitations

- The root route currently redirects anonymous users to login by design.
- Public smoke coverage is therefore built around the public login page and the public `Find a License` route.
- No authenticated flow was implemented because credentials were not provided and the request asked to avoid auth unless required.
- The search results behavior was not asserted because realistic public search criteria were not known during inspection.
