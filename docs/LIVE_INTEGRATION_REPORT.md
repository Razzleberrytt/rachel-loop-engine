# Live Descript Integration Report

**Test date:** 2026-09-04 (America/New_York)  
**Scope:** synthetic media only — no Rachel/family footage was used.

## Result

The URL-based ChatGPT ↔ Descript production path is **verified end-to-end**.

Verified against a live Descript project:

1. Create a project inside the `Rachel Loop Engine` folder.
2. Import a synthetic video from a fetchable URL.
3. Wait for the asynchronous media-import job and verify `result.status=success`.
4. Preserve the canonical `00 Raw` composition.
5. Run the Descript project agent.
6. Create exact canonical compositions:
   - `A Natural`
   - `B Retention`
   - `C Loop`
7. Inspect the project after the mutation.
8. Resolve actual composition UUIDs from project state rather than guessing IDs.
9. Publish `A Natural` as a 1080p unlisted review render.
10. Wait for the render job and verify a successful share URL was returned.

This validates the repository's core editor-transport design against the real connected Descript surface, not only the mock transport.

## Direct chat-file upload finding

The connected Descript import operation correctly supports a two-stage direct-upload handshake:

1. request an upload slot with MIME type + exact byte size;
2. `PUT` the bytes to the returned signed storage URL.

The first stage was verified: Descript returned a real project and signed upload slot. The current execution container, however, cannot perform arbitrary outbound `PUT` traffic to that external storage host. Therefore **direct chat attachment → Descript bytes is not yet an end-to-end path in this environment**.

This is a transport gap, not an editing-engine failure. Current working intake options are:

- a direct/fetchable media URL;
- Google Drive URL supported by Descript import;
- Dropbox URL supported by Descript import;
- another bridge capable of sending the attachment bytes to Descript's signed upload URL.

## Production consequence

For Rachel's first real end-to-end job, use a private Drive/Dropbox/direct-access URL rather than placing personal footage in a public repository. The temporary synthetic smoke fixture is test-only and must never become a pattern for private family media.

## Validated invariants

- External editor operations are asynchronous and must be awaited.
- `stopped` job state alone does not mean success; inspect `result.status`.
- Canonical composition names are a reliable machine contract.
- Composition IDs must be discovered after agent mutation.
- Rendering can be kept unlisted for review; publishing a Descript render is **not** the same as posting publicly to a social platform.
- A failed later stage should not recreate an already-successful project/edit.

## Next integration gate

Process one real Rachel source from a private supported URL through the full creative prompt, then evaluate the actual A/B/C edits visually and update Rachel-specific rules from observed quality rather than assumptions.
