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
propagate. Run these contracts through the repository-root `make test`.
