# Read-only native process isolation

`u.Cli.run_raw`, `run_bytes` and `run_to_file` accept an optional
`m.Cli.ProcessOptions.isolation`. The existing process owner prepares and starts
the isolated child; its deadline, byte streams, signals, cleanup and
`ProcessOutcome` retain the ordinary runtime contract.

`m.Cli.ProcessReadOnlyIsolation` is an immutable request. The caller supplies the
qualified Linux platform and filter architecture, authenticated Bubblewrap
launcher and seccomp policy bytes, captured source/resource/metadata files,
authenticated runtime trees and files, and the complete child environment as
immutable name/value pairs. Tool qualification and the meaning of the native
filter remain the supplying bootstrap owner's responsibility. The filter must
deny socket creation and network operations for its declared architecture.
An arbitrary file receipt alone is not tool or policy qualification.

The runtime reauthenticates the supplied physical identities before spawning.
Source files, runtime files, the launcher and the filter are copied into sealed
anonymous descriptors. Bubblewrap mounts those exact file bytes read-only at
their original absolute paths. Runtime trees use authenticated physical
directory descriptors and read-only mounts; they retain live backing and must
also be reauthenticated by the caller after execution before accepting an import
result. Interpreter links are retained only when their declared targets stay
within the supplied closure. Host root mounts, overlapping runtime roots and
caller-inherited file descriptors are rejected.

Bubblewrap enters explicit user, IPC, PID, network, UTS and cgroup namespaces,
disables further user namespaces, creates a terminal session, drops capabilities
and applies the required native seccomp filter before executing the command.
The child receives no ambient environment or PATH resolution, no writable host
mount, and no host device or socket mount. The executable and working directory
must belong to the declared closure. Standard input and captured output remain
the explicit process protocol.

This implementation selects Linux only. An unsupported platform, changed input,
invalid request, unavailable kernel capability, rejected namespace or invalid
seccomp policy fails without an alternate executor or unenforced import.
Namespace isolation alone does not deny socket creation; the seccomp policy is
required. Positive acceptance must exercise the qualified launcher and policy
through the public runtime and show that filesystem, network, IPC and signal
escape attempts cannot affect the host.

The native option and descriptor contracts come from the
[Bubblewrap upstream source](https://github.com/containers/bubblewrap/blob/main/bubblewrap.c)
and its [security guidance](https://github.com/containers/bubblewrap/blob/main/README.md).
