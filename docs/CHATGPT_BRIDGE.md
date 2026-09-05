# ChatGPT ↔ Descript Bridge

This document maps `EditorTransport` to the connected Descript operations.

| Engine method | Connected operation | Notes |
|---|---|---|
| `import_media(payload)` | Descript import media | Returns a job ID; wait before continuing. |
| `run_agent(payload)` | Descript project agent | Target project or exact composition when known. |
| `wait(job_id)` | Descript wait for job | `stopped` is terminal; inspect nested `result.status`. |
| `get_project(project_id)` | Descript get project | Resolve real composition IDs and durations by name. |
| `publish(payload)` | Descript publish project | Publish accepted composition, normally 1080p/unlisted. |

## Verified live path

A synthetic smoke test verified:

`fetchable URL -> import -> wait -> 00 Raw -> agent -> A/B/C -> inspect -> real IDs -> 1080p unlisted render`

See `docs/LIVE_INTEGRATION_REPORT.md`.

## Bridge invariant

Never guess a composition ID. After variant creation, inspect the project and match exact canonical names (`A Natural`, `B Retention`, `C Loop`).

## Intake modes

### Fetchable URL — verified
Pass the media URL directly to Descript import. Use a private-access mechanism supported by Descript for personal footage.

### Google Drive / Dropbox — supported path for private footage
Descript's import surface accepts these URL forms and they avoid making Rachel's source public.

### Direct chat attachment — handshake verified, byte bridge pending
The Descript tool returns a signed upload URL when given MIME type + exact file size. The current execution container cannot perform the required arbitrary external `PUT`, so another byte-transfer bridge is required before this mode is fully automatic here.

Never work around this by uploading Rachel/family footage to a public Git repository.

## Async jobs

Import, agent editing, and rendering are asynchronous. Persist durable IDs and retry the failed stage rather than duplicating upstream work. The v0.4 workflow runner now reuses an existing Descript project/canonical compositions and existing rendered artifacts when present in the job manifest.
