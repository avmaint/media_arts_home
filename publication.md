# Publication Procedures for Manuals and Documents

## Machines

- **Development machine — `vanadium-mbp`**: where this repo (`media_arts_home`) and the `uactechdoc` repo are edited, and where the publish scripts are run from.
- **Production machine — `cumu-g001`**: runs the Flask app (`app.py`) that serves the home page, `/manuals/`, and `/docs/`. Reachable over VPN from `vanadium-mbp` under the alias `uacts-g001`. The app lives at `/Users/avuser/media_arts_home/` on this machine (whether run directly via `run.sh` or containerized per the separate `runbook` repo's `docker-compose.yml`, which bind-mounts `docs/`, `manuals/`, `config.json`, and `messages.json` from that same path).

Production is actually a small fleet of containers defined in the `runbook` repo's `docker-compose.yml`: `media-arts-home`, `avl-assistant-api`/`avl-assistant-web` (AVL Tech Assistant), `crud-api`/`crud-web` (`avl_data`), and `postgres`. They talk to each other over the Compose network by service name, not `localhost` — see the env var note below.

Both `manuals/assets_manuals_index.json` and the served PDFs are read from disk on every request (`app.py`'s `load_manual_index()` and `serve_manual()` do not cache) — **rsyncing new files to production is enough to make them live immediately, no app restart needed.**

## Important: PDFs are not committed to git

`manuals/*.pdf` is covered by `.gitignore`'s `*.pdf` rule. Only the mapping/index JSON files (and any non-PDF assets, e.g. reference HTML pages) are tracked in git. PDFs travel from `vanadium-mbp` to `cumu-g001` **only** via `./publish_manuals.sh` (rsync), never via git. Keep local PDFs backed up separately — they exist only on your working copy and on production.

---

## A. Publishing a new manual

Run on **vanadium-mbp**:

1. Copy the new PDF(s) into the appropriate subfolder under `manuals/` (e.g. `manuals/lighting/`, `manuals/audio/`).
2. Edit `manuals/asset_manual_map.json` and add/update the entry mapping the asset tag(s) to the relative PDF path(s) (path is relative to `manuals/`, e.g. `"lighting/New_Fixture_Manual.pdf"`). An asset tag can map to one path (string) or several (array).
3. Run the audit script to sanity-check the mapping before rebuilding the index:
   ```
   python3 scripts/audit_manuals.py
   ```
   Review `unmapped_pdfs` (PDFs on disk with no map entry) and `missing_from_filesystem` (map entries pointing at files that don't exist) in the output.
4. Rebuild the served index (requires `assets.xlsx` at `/Users/donert/Documents/UACTech/uacdata/assets.xlsx`, dev-machine only):
   ```
   python3 scripts/build_manuals_index.py
   ```
   This regenerates `manuals/assets_manuals_index.json`.
5. Commit the map and index changes (not the PDFs — those are gitignored):
   ```
   git add manuals/asset_manual_map.json manuals/assets_manuals_index.json
   git commit -m "Add manual for <asset tag / equipment>"
   git push
   ```
6. Publish the manuals folder (PDFs + map + index) to production:
   ```
   ./publish_manuals.sh
   ```
   This rsyncs `manuals/` to `avuser@uacts-g001:/Users/avuser/media_arts_home/manuals/` with `--delete`, so anything removed locally is also removed on production.

Run on **cumu-g001**: nothing. The new manual is live as soon as the rsync in step 6 completes.

---

## B. Refreshing documentation (uactechdoc)

Run on **vanadium-mbp**:

1. In the `uactechdoc` repo, render/update the Quarto docs so `uactechdoc/_output/` is current (e.g. `quarto render`), then commit and push changes in that repo as normal.
2. From `media_arts_home`, publish the rendered output to production:
   ```
   ./publish_docs.sh
   ```
   This rsyncs `uactechdoc/_output/` (excluding `_work`) to `avuser@uacts-g001:/Users/avuser/media_arts_home/docs/` with `--delete`.

Run on **cumu-g001**: nothing. `/docs/` is served straight from that synced folder and picked up on the next request.

---

## C. Verifying a publish actually took

The server never needs a restart, but two things routinely make a fresh publish *look* like it didn't work:

- **Browser cache on `/manuals/`.** The route sets no `Cache-Control` header, and an already-open tab (or a plain reload in some browsers) can keep showing the pre-publish page/row data even though the underlying file changed. Always **hard-refresh** (Cmd+Shift+R) or check in a private/incognito window before concluding a publish didn't take.
- **The manuals-page search box only matches asset metadata** — `asset_tag`, `category`, `manufacturer`, `model`, `type`, `description`, `room`, `location`, `in_service` (see `data-search` in `templates/manuals_index.html`). It does **not** match manual/PDF filenames. Searching for a term that only appears in the PDF's name (not in the asset's `assets.xlsx` fields) will correctly find nothing — that's not a stale-data bug.

To check the data itself rather than the rendered page, hit the API directly, which reads the same index file with no caching:
```
curl http://uacts-g001/api/manuals/<asset-tag>
```
If this returns the expected manuals but the `/manuals/` page still doesn't show them, it's a browser-cache issue, not a publish issue.

### AVL Tech Assistant's "linked manuals" depends on a cross-container env var

AVL Tech Assistant (`avltechassistant` repo) doesn't read `manuals/` itself — its backend (`avl-assistant-api`, see `backend/main.py`) proxies `GET /manuals/{asset_tag}` to media-arts-home's `GET /api/manuals/{asset_tag}` and rewrites the returned URLs. This proxy target is controlled by the `MANUALS_BASE_URL` env var, set in `runbook/docker-compose.yml` on the `avl-assistant-api` service:
```yaml
avl-assistant-api:
  environment:
    - MANUALS_BASE_URL=http://media-arts-home:5000
```
It must be the Compose **service name** and the container's **internal** port (`5000`, what gunicorn binds to per the `media_arts_home` Dockerfile) — not `localhost` and not the host-mapped port `80`. If this var is missing or wrong, `avl-assistant-api` can't reach `media-arts-home` from inside its own container, the proxy call fails, and the AVL Tech Assistant UI silently shows "No manuals available" for every asset even though `media_arts_home`'s own data and API are completely correct. Republishing manuals on `media_arts_home` doesn't touch this — it's a one-time `runbook` deployment config, not something either publish script or app "reload" step affects.

---

## D. Deploying app/code changes (for reference)

Changes to `app.py`, `templates/`, `static/`, `config.json`, or the `scripts/` — as opposed to manuals or docs content — need an actual deploy on production, separate from the above:

- Commit and push the change from `vanadium-mbp` as usual.
- On **cumu-g001**, pull and restart:
  ```
  ./run.sh deploy   # git pull + pip install
  ./run.sh stop
  ./run.sh start
  ```
  (or the equivalent `docker-compose pull && docker-compose up -d` if running containerized per the `runbook` repo).
