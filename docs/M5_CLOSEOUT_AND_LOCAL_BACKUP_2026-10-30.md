# M5 technical closeout and local backup

Date: **2026-10-30**.

M5 is the current consolidation/delivery milestone. Its technical deliverables
are complete locally: retrospective trace analysis, family/paired tables, both
efficiency views, qualified uncertainty analysis, report, claim ledger, validated
wheel, installation guide and recorded two-backend Gazebo demonstration. M5 did
not introduce new research trials. The preserved M4 result remains mixed:
Sol20/20 in each condition; Qwen15/20 with primitives and14/20 with macros.

The eight human ratings and the owner's preference for concise explicit tasks
were committed in evaluation9931226. The subsequent GitHub access diagnostic is
committed in b5e94bf. The feedback is outcome-oriented stakeholder review;
independent human adjudication applying the frozen clarification rule was not
obtained. Original ratings and disagreements remain visible. No revised ratings
or new validation success are inferred.

## Verified local committed backup

The backup directory is `backups/m5-committed-2026-10-30/` at the workspace root,
outside both Git repositories. See the
[pinned backup record](../artifacts/macro-m5-20261027/committed-backup-20261030.json).

| Repository | Protected commit | Files at protected HEAD | Available commits | Bundle bytes |
|---|---|---:|---:|---:|
| rosa-research | b13df0f03677754f42383dee95424cded862b117 | 86 | 6 | 618,060 |
| rosa-evaluation | b5e94bf2c107fb4ff57ba5559b084ce2ea2d97a0 | 2,949 | 21 | 123,958,224 |

Both source repos are shallow clones. The backup preserves each branch bundle
**together with its matching `.shallow` marker**. An ordinary bundle clone failed
at a parent beyond the source history boundary; that initial failure is retained
in `RESTORE_ATTEMPT_01.json`. Shallow-aware restoration into newly initialized bare
repositories then passed, with exact HEAD/tree equality and `git fsck --full`.
The active repos and source history boundaries were not modified or fetched.
These are backups of all available branch history, not all upstream history.

`BACKUP_MANIFEST.json`, SHA256 sidecars and `RESTORE.md` are beside the bundles.
Keep the bundle and shallow marker together. The verified restore-check bare
repositories are also retained. The credential-pattern scan passed across8,245
unique contents and15,927 nested archive entries; two exact expired sentinel
files retain their prior explicit noncredential review. No credential values
were printed or copied from credential stores.

Tracked raw results, delivery ZIPs and the previously committed historical
retained-work backups are included. Current uncommitted/untracked work outside
those dated historical archives, Git configuration, installed environments and
credential stores are not included. Later backup-status documentation is not
implicitly included in the pinned base bundles; the manifest is authoritative
for any later supplement.

## Remaining limits and decision

- Evaluation off-machine protection remains deferred under the user's local-only
  instruction. No GitHub push or other upload was performed. Research b13df0f was
  separately verified remotely earlier; this is not a claim that evaluation was.
- Independent human review applying the original clarification criterion was not
  obtained. The owner's alternative judging preference is preserved rather than
  silently substituted into the frozen benchmark.

M5 therefore has completed technical delivery with explicitly unfulfilled
protection/review items. It is not an assertion that every original gate passed.
The recommended next use is the delivered installation guide, report and demo.
No new architecture, model experiment, prompt rewrite or physical robot work is
scheduled by this closeout.
