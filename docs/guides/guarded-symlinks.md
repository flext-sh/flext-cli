# Guarded symbolic links

<!-- TOC START -->

<!-- TOC END -->

The public `u.Cli` filesystem domain provides three operations:

- `atomic_read_symlink_state(path, required=False)` captures the exact link text,
  physical link identity and physical parent identity. A dangling link is present.
- `atomic_write_symlink_guarded(before, target)` creates at authenticated absence or
  replaces the authenticated symbolic link. An unchanged target is a no-op.
- `atomic_delete_symlink_guarded(before)` removes only that link, never its target.

The parent directory must exist and must not traverse a symbolic link. Regular files and
directories are rejected as leaf inputs. Filesystem `OSError` failures returned through
the result retain their exception object. Exceptions outside each public method's
declared catch boundary escape directly: this includes strict UTF-8 decoding or encoding
failure during snapshot acquisition and causal cleanup groups. Publication returns
`ValueError` failures through its result boundary as well. Link targets remain literal;
no resolution, normalization or rewriting of relative targets occurs. The text API
requires UTF-8-representable target text. Newlines are preserved. Surrogate-containing
targets fail before publication; an existing non-UTF-8 link fails snapshot acquisition
without modifying or deleting it. No encoding fallback or replacement is performed.

Every cooperative writer must hold the same exclusive lease from snapshot through
mutation. These operations authenticate the parent and leaf immediately before
descriptor-bound effects and sync the parent afterward. They are not compare-and-swap
against actors that ignore that lease. Absence publication uses the shared platform
no-replace rename primitive; unsupported platforms fail before publication.

If staging succeeds but its first authenticated snapshot fails, the original exception
is not enriched with notes or otherwise altered. The unverified leaf remains untouched:
another actor may have replaced it. A parent rename can invalidate the original logical
path, so recovery must locate and re-authenticate the physical parent and leaf under the
same lease before cleanup. A failed parent recheck preserves the original exception and
traceback in its causal exception group. Once a staging snapshot exists, cleanup uses
its exact identity; a cleanup failure is grouped with the original exception rather than
replacing it.

`m.Cli.AtomicSymlinkState.target` and `.identity` are both absent or both present. The
nested identity records permissions, device, inode, link count, owner, group,
modification/change timestamps and platform metadata. Access time is excluded because
reading a symbolic link can change it.

Changing a regular file into a link, or a link into a regular file, requires the
appropriate existing guarded deletion followed by a fresh absence snapshot and the
appropriate guarded creation. A higher-level durable transaction owns resumption across
that explicit intermediate absence; this facade never treats an unexpected filesystem
kind as permission to remove it.

Validate the public behavior through root `make gen`, `make check` and `make test`. The
filesystem tests cover dangling links, no-op identity, target preservation, stale inode
and parent rejection, competing files and invalid targets.
