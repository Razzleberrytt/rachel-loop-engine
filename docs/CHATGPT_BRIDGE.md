# ChatGPT ↔ Descript Bridge

This document maps `EditorTransport` to the currently connected Descript operations.

| Engine method | Connected operation | Notes |
|---|---|---|
| `import_media(payload)` | Descript import media | Returns a job ID; wait before continuing. |
| `run_agent(payload)` | Descript project agent | Target project or exact composition when known. |
| `wait(job_id)` | Descript wait for job | Inspect stopped/result status; do not treat stopped+error as success. |
| `get_project(project_id)` | Descript get project | Resolve real composition IDs and durations by name. |
| `publish(payload)` | Descript publish project | Publish accepted composition, normally 1080p/unlisted. |

## Bridge invariant

Never guess a composition ID. After variant creation, call project inspection and match exact canonical names (`A Natural`, `B Retention`, `C Loop`).

## Uploads

The connected import surface supports URL imports and direct file upload flows. For direct uploads, the bridge must declare MIME type and byte size, use the returned upload URL, and only proceed after the import job completes.

## Async jobs

Import, agent editing, and publishing are asynchronous. Persist returned job IDs in job metadata when a production bridge is implemented so an interrupted session can resume rather than duplicate work.
