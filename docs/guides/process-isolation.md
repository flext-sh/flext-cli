# Read-only native process isolation

`u.Cli.run_raw`, `run_bytes` and `run_to_file` accept an optional
`m.Cli.ProcessOptions.isolation`. The existing process owner prepares and starts
the isolated child; its deadline, byte streams, signals, cleanup and
`ProcessOutcome` retain the ordinary runtime contract.

`m.Cli.ProcessReadOnlyIsolation` is an immutable request. The caller supplies the
qualified Linux platform and filter architecture, the bootstrap-qualified static
Bubblewrap launcher and policy compiler, captured source/resource/metadata files,
authenticated runtime trees and files, and the complete child environment as
immutable name/value pairs. `ProcessNativeToolEvidence` is serialized inside the
existing bootstrap `WorkspaceOperationReceipt.native_tool_qualifications`; it
does not create an installation ledger. Its wrapper adds the current issuer
report snapshot and captured compiler bytes. The process owner requires exactly
one matching original evidence row, its independently elected compiler
declaration, unchanged source/installation/artifact receipts, successful native
build and ABI outcomes, and complete original syscall-denial observations.
Every required syscall must have been attempted once and returned `EACCES`.
Missing observations, a changed policy hash or an absent native provider is red.
An arbitrary file receipt or successful process exit alone is not qualification.

Both tools must be native ELF with no interpreter and no `DT_NEEDED` libraries,
matching the declared interpreter ABI. The execution owner invokes its sealed
bytes through the same public `run_bytes` port with the original absolute deadline
and an empty replacement environment. Each source-owned symbolic syscall is one
argv item; stdout is native SDK-generated BPF, which the owner seals and passes
directly to Bubblewrap. With no arguments the static compiler emits the decimal
`seccomp_arch_native()` token and a newline for its SDK ABI probe. That probe is
distinct from the native denial observations. The policy identity hashes the
NUL-terminated ASCII argv vector; bootstrap and execution use
`u.Cli.native_process_policy_identity()` and
`u.Cli.native_process_policy_arguments()`. Compiler failure
retains the original process outcome and output. Caller-supplied raw BPF has no
request field or admission route.

`src/flext_cli/config/process.yaml` owns the required symbolic network and `io_uring` syscall
denials. The typed schema preserves those immutable external syscall obligations;
they cannot be removed by configuration. The native compiler uses libseccomp's
architecture-aware symbolic rule API, including multiplexed syscall rewriting,
and never relies on a handwritten numeric syscall table.

The runtime reauthenticates the supplied physical identities before spawning.
Source files, runtime files, the launcher and the compiled filter use sealed
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

This implementation selects Linux only. The managed native compiler provider
and its real host-escape acceptance remain required before positive isolation
can be accepted. An unsupported platform, changed input, invalid request,
unavailable kernel capability, rejected namespace or invalid seccomp policy
fails without an alternate executor or unenforced import.
Namespace isolation alone does not deny socket creation; the seccomp policy is
required. Positive acceptance must exercise the qualified launcher and policy
through the public runtime and show that filesystem, network, IPC and signal
escape attempts cannot affect the host.

The native option and descriptor contracts come from the
[Bubblewrap upstream source](https://github.com/containers/bubblewrap/blob/main/bubblewrap.c)
and its [security guidance](https://github.com/containers/bubblewrap/blob/main/README.md).
The compiler follows the
[libseccomp rule API](https://github.com/seccomp/libseccomp/blob/main/doc/man/man3/seccomp_rule_add.3)
and [native BPF export contract](https://github.com/seccomp/libseccomp/blob/main/doc/man/man3/seccomp_export_bpf.3).
