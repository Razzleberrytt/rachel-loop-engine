# Descript Integration Contract

Rachel Loop Engine treats Descript as an editor **adapter**, not as the source of creative truth. The creative rules remain versioned in this repository.

## Operations the adapter needs

The current ChatGPT-connected Descript surface maps cleanly to five engine operations:

1. **Import media** — create a project, import a URL or direct upload, and create a 1080x1920 raw composition.
2. **Project agent** — apply natural-language editing instructions to a project/composition.
3. **Wait for job** — resolve asynchronous import/edit/publish jobs.
4. **Get project** — discover actual composition IDs, names, and durations after edits.
5. **Publish project** — render a selected composition and return a shareable result.

`src/rachel_loop_engine/adapters/descript.py` depends on the small `EditorTransport` protocol instead of embedding connector-specific code. A bridge running inside ChatGPT can translate these methods to the connected Descript tools. A future direct client can implement the same protocol.

## One-input execution

1. Create `SourceSpec` from the raw video URL/upload metadata.
2. Create a Descript project in the `Rachel Loop Engine` folder.
3. Preserve the imported composition as `00 Raw`.
4. Run the multi-variant production prompt.
5. Inspect the project and resolve exact `A Natural`, `B Retention`, and `C Loop` composition IDs.
6. Run QC; reject/downgrade the loop independently if necessary.
7. Publish accepted variants at 1080p.
8. Persist project/composition/share IDs in the job manifest.
9. Later ingest platform analytics and append evidence to the experiment log.

## Important constraint

Do not invent undocumented network endpoints. The engine coordinates capabilities exposed by a transport. This keeps the repository honest and runnable in mock/dry-run mode even when no live Descript bridge is attached.
