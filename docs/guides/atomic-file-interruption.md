# Atomic file interruption

The public atomic file operations retain a descriptor and its inode identity through
staging and publication. An interruption after authentication removes only the matching
staged inode. The original exception escapes with its original traceback. A real cleanup
failure retains both causes through the existing cleanup error contract.

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
