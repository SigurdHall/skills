---
name: tableau-rest-api
description: Build, test, debug, or document Tableau REST API and extract workflows. Use when the user mentions Tableau API, Tableau Server, PAT login, .env Tableau config, site/project smoke tests, workbook/report evidence, views, crosstabs, download Tableau workbooks or datasources, .twb, .twbx, .tdsx, .tds, .hyper, Hyper API, Metadata API, Tableau-to-Power-BI/Fabric migration, redirects, or HTTP errors 301, 405, 401, 403, 404, connection refused.
---

# Tableau REST API

Use this for Tableau REST API smoke tests and small automation scripts.

For workbook/report evidence capture, read
`references/workbook-report-extraction.md` before designing extraction scripts or
Tableau-to-Power BI migration evidence.

## Configuration

Read credentials from `.env`; never hardcode or print secrets.

Common variables:

```text
TABLEAU_SERVER_URL=http://tableau-server
TABLEAU_SITE_CONTENT_URL=site-content-url
TABLEAU_KEY_NAME=personal-access-token-name
TABLEAU_API_SECRET=personal-access-token-secret
TABLEAU_API_VERSION=3.23
```

Add `.env`, `.env.*`, `__pycache__/`, and `*.py[cod]` to `.gitignore`. Keep `!.env.example` if examples are useful.

## Minimal Smoke Test

1. Load `.env`.
2. POST to `/api/<version>/auth/signin` with PAT credentials.
3. Read `credentials.token`, `site.id`, and `user.id`.
4. Make one small authenticated GET, for example `/sites/<site_id>/projects?pageSize=1`.
5. POST to `/auth/signout` in `finally`.

Use Python standard library (`urllib.request`) if the repo has no dependency management. Use `requests` only when dependencies already exist or the user asks for it.

## Redirect Handling

Tableau or a gateway may return `301`/`302`. Default Python redirect handling can convert `POST` to `GET`, causing:

```text
HTTP 405 Method Not Allowed: The HTTP method 'GET' is not supported
```

For sign-in, preserve method and body across redirects:

- Disable automatic redirects with a custom `HTTPRedirectHandler`.
- On `301`, `302`, `303`, `307`, or `308`, read `Location`.
- Reissue the same method, headers, and payload to the redirected URL.
- Limit redirects, for example `MAX_REDIRECTS = 5`.

## Diagnostics

When a connection fails, report the actionable reason without leaking tokens:

- `301`: server redirected; show `Location` and suggest updating `TABLEAU_SERVER_URL` if stable.
- `405 GET not supported`: a POST was redirected as GET; preserve method on redirect.
- `401`: token name/secret likely invalid or expired.
- `403`: token is valid but lacks access to site/resource.
- `404`: wrong API version, site, or endpoint path.
- `10061 connection refused`: host reached but port/service refused connection; check protocol, port, VPN, firewall, or Tableau gateway.

## Verification

Run:

```powershell
python -B -c "import ast, pathlib; ast.parse(pathlib.Path('test_tableau_api.py').read_text(encoding='utf-8')); print('Syntax OK')"
python -B test_tableau_api.py
```

Use `-B` if local `__pycache__` writes fail or should be avoided.

## Datasource Downloads And Hyper Extracts

When downloading Tableau data sources, distinguish these files:

- `.tdsx`: packaged data source.
- `.tds`: Tableau definition and field metadata; this is not row data.
- `.hyper`: extract data; this contains rows when the data source includes an extract.

For readable exports, unzip `.tdsx`, parse `.tds` for field metadata, and use
`tableauhyperapi` for `.hyper` rows.

Never assume the Hyper data table lives in schema `Extract` or that the table is
named `Extract`. Before exporting:

1. Open the `.hyper` file with `HyperProcess` and `Connection`.
2. Call `connection.catalog.get_schema_names()`.
3. For each schema, call `connection.catalog.get_table_names(schema)`.
4. For each table, read `catalog.get_table_definition(table)`.
5. Count rows with `SELECT COUNT(*) FROM <table>`.
6. Export rows in chunks with an explicit row limit or `0` for all rows.

Log a small table catalog for each Hyper file with:

```text
hyper_file
schema_name
table_name
column_count
row_count
rows_exported
csv_chunks
```

If a readable output only contains `*_tds_columns.csv`, assume only metadata was
converted. Check whether a `.hyper` file exists and whether Hyper conversion
ran successfully.

For large extracts, default to a sample row limit for inspection and require an
explicit all-rows option before exporting everything:

```text
--hyper-row-limit 10000
--hyper-row-limit 0
--hyper-chunk-size 100000
```

## Workbook And Report Evidence

Use Tableau REST API and existing Tableau metadata to capture workbook/report
evidence before rebuilding reports elsewhere. Prefer small, auditable artifacts:
workbook inventory, view/page list, datasource bindings, field usage, filters,
parameters, calculated fields, permissions, schedules, subscriptions, thumbnails,
and owner/project context.

If table migration contracts exist, join the Tableau field/datasource evidence
to those contracts instead of inferring renamed tables or columns from report
labels. Keep unresolved mappings explicit for human review.

See `references/workbook-report-extraction.md` for a compact artifact checklist
and extraction sequence.
