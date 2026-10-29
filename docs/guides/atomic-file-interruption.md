# Atomic file interruption

<!-- TOC START -->

<!-- TOC END -->

The public atomic file operations retain a descriptor and its inode identity through
staging and publication. An interruption after authentication removes only the matching
staged inode. The original exception escapes with its original traceback. A real cleanup
failure retains both causes through the existing cleanup error contract.

An authenticated read can fail before its final pathname or parent validation.
That read failure remains the primary exception with its original traceback and
errno even if final validation also fails. Retain later validation failures as
secondary diagnostics; never replace the operation's cause, select another read
path or publish success. If the operation succeeded, a failed final validation is
itself the native failure. The active work item owns acceptance of this correction.

For `flext-2e7wy.1` phase 1, the existing `atomic_file_state` owner also owns
`read_authenticated_state` and the retained `authenticated_entry` context. Its
native capture is the original parent stat, leaf stat and bytes, not a model
reconstructed by reopening the path. Receipt operations in `atomic_file_snapshot`
consume that owner directly, without wrapping its descriptors in callable aliases;
file and process consumers retain their public APIs through `u.Cli`.
Receipt construction likewise uses the original retained native state and stream.

The public byte-state reader returns `p.Result[m.Cli.AtomicFileState]` through
Core's generic `r.ok` and covariant failure factory. It constructs and validates
the state model once from the retained native observation; the result carries
that instance by reference. Specializing the result class at each read solely
to call those already-generic factories adds schema construction without another
payload-validation contract. Removing that specialization does not change the
authenticated read, optional absence, original exception or physical witnesses.
Performance acceptance requires the same real consumer and attributable profile;
the factory change alone proves no completed generation or transaction budget.

File and empty-directory state checks are distinct capabilities, not interchangeable
MRO overrides. A directory check requires a retained parent descriptor, a physical
directory on its parent's device, and a present caller-owned identity. A file check
accepts exact absence, validates a regular file when present, and may acquire its
own parent descriptor. Preserve these contracts when assigning capability-specific
names through the native refactoring route; changing facade base order or widening
the directory inputs does not resolve their semantic collision.

The cold source closure is `atomic_file_state`, `atomic_file_read`,
`atomic_file_descriptor`, `atomic_parent_descriptor`, `atomic_parent_failure` and
`atomic_file_path`. These sources depend at runtime only on stdlib and each other,
with relative imports retaining descriptor-class identity inside each loading
namespace. The native read primitive owns its open flags; the public constants
surface projects them, not the reverse. Ordinary SDK imports retain their normal
package initialization. A cold consumer may load an explicitly source-published
bootstrap namespace containing this complete declared closure without executing or
fabricating `flext_cli` or `_utilities` package initializers. That projection is
maintained by the resource publisher, never a second implementation of atomic IO.

This extraction does not establish supplier election or operation lifetime. The
root's pending lifetime binding must span the actual reaped UV process through the
final save; a serialized receipt or permission flag cannot establish that binding.

`u.Cli.atomic_read_binary_file_receipt` records physical identity, byte length,
SHA-256, and native version without storing the payload. Optional absence retains
the same parent and owner contract as a byte snapshot. The scoped
`u.Cli.atomic_binary_file_reader(receipt)` verifies the complete digest once on
acquisition and serves repeated `read_range(offset, length)` calls through that
descriptor. Each range rejects changed metadata and short reads; completion checks
the path and parent again. The reader becomes unusable when its context closes.
`u.Cli.atomic_read_binary_file_range` provides the same contract for one range.

`u.Cli.atomic_publish_staged_binary_file_receipt_guarded` uses the existing guarded
replacement and durability owners. It verifies the destination and staged receipts,
consumes the staged name, streams the published digest, and returns the published
version. It never constructs a payload-sized `AtomicFileState`.

`u.Cli.atomic_inventory_physical_directory` captures one authenticated directory and
its immediate names, kinds, versions, and literal symlink targets. It does not
descend or read child payloads. Its complete election set can prove an absent name;
file-content and recursive cleanup authority remain separate contracts.

Directory child names and query exclusions are native lexical leaves. Reject
empty names, dot and parent entries, and embedded native path separators before
descriptor lookup. Preserve ordered uniqueness, root identity, versions, literal
symlink targets and query predicates. Leaf validation uses native basename
semantics without constructing a `Path` for every already-lexical name; it never
resolves a name against the working directory or substitutes another entry.
The topology proof remains fresh for every original witness. Reusing a completed
directory inventory does not authorize caching lineage verification or skipping
descriptor, parent-entry, no-follow or anchor rechecks.

An exception can also interrupt the return from the operating system's `open` before
Python stores the descriptor. In that window the operation cannot authenticate the
directory entry, and therefore leaves it untouched. The original interruption still
escapes unchanged; retained staging is not a successful write or authorized cleanup. An
unpredictable temporary name alone never proves ownership. Re-authentication is required
before any subsequent removal.

Blocking timer signals on the acquiring thread narrows this window but cannot promise
process-wide exclusion. POSIX signal masks are per-thread, and a process-directed signal
may arrive on another unblocked thread. Python executes its handler in the main thread
at a later interpreter boundary. These constraints are documented by
[Python's signal contract](https://docs.python.org/3.13/library/signal.html#execution-of-python-signal-handlers)
and [Linux signal delivery](https://man7.org/linux/man-pages/man7/signal.7.html).

The public tests exercise actual timer delivery and deterministic audit boundaries. They
require authenticated staging to be removed, unknown entries to retain their inode and
bytes, the destination to remain unpublished, and the identical original exception to
propagate. Run these contracts through the repository-root `make tests`.
