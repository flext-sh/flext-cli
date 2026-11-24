/*
 * Native libseccomp policy compiler for the CLI process owner.
 *
 * Build and qualification belong to the declared bootstrap toolchain.
 * The process owner supplies its validated symbolic syscall obligations.
 * Copyright (c) 2026 FLEXT Team. All rights reserved.
 * SPDX-License-Identifier: MIT
 */

#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <linux/landlock.h>
#include <seccomp.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <unistd.h>

static int report_failure(const char *operation, int status)
{
    fprintf(stderr, "%s: native_status=%d\n", operation, status);
    return EXIT_FAILURE;
}

static int print_architecture(void)
{
    uint32_t architecture = seccomp_arch_native();
    if (architecture == SCMP_ARCH_NATIVE) {
        fprintf(stderr, "seccomp_arch_native: unresolved token=%" PRIu32 "\n",
                architecture);
        return EXIT_FAILURE;
    }
    if (printf("%" PRIu32 "\n", architecture) < 0 || fflush(stdout) == EOF) {
        return report_failure("native architecture output", -errno);
    }
    return EXIT_SUCCESS;
}

static int print_version(void)
{
    const struct scmp_version *version = seccomp_version();
    if (version == NULL) {
        fputs("seccomp_version returned NULL\n", stderr);
        return EXIT_FAILURE;
    }
    if (printf("%u.%u.%u\n", version->major, version->minor,
               version->micro) < 0 || fflush(stdout) == EOF) {
        return report_failure("native version output", -errno);
    }
    return EXIT_SUCCESS;
}

static bool fixture_socket_operation(const char *name)
{
    static const char *const operations[] = {
        "connect", "bind", "listen", "accept", "accept4", "sendto", "recvfrom",
        "sendmsg", "recvmsg", "sendmmsg", "recvmmsg",
    };
    for (size_t index = 0; index < sizeof(operations) / sizeof(*operations);
         ++index) {
        if (strcmp(name, operations[index]) == 0) {
            return true;
        }
    }
    return false;
}

static int deny_syscalls(scmp_filter_ctx context, int count, char **names,
                         bool fixture)
{
    for (int index = 0; index < count; ++index) {
        if (fixture && fixture_socket_operation(names[index])) {
            continue;
        }
        int syscall_number = seccomp_syscall_resolve_name(names[index]);
        if (syscall_number == __NR_SCMP_ERROR) {
            fprintf(stderr, "unresolved syscall: %s\n", names[index]);
            return report_failure("seccomp_syscall_resolve_name",
                                  syscall_number);
        }
        bool family = fixture && (strcmp(names[index], "socket") == 0 ||
                                  strcmp(names[index], "socketpair") == 0);
        const struct scmp_arg_cmp other_family = SCMP_A0(SCMP_CMP_NE, AF_UNIX, 0);
        int status = seccomp_rule_add_array(
            context, SCMP_ACT_ERRNO(EACCES), syscall_number,
            family ? 1 : 0, family ? &other_family : NULL);
        if (status < 0) {
            return report_failure("seccomp_rule_add_array", status);
        }
    }
    return EXIT_SUCCESS;
}

static int compile_policy(int count, char **names, bool fixture)
{
    scmp_filter_ctx context = seccomp_init(SCMP_ACT_ALLOW);
    if (context == NULL) {
        fputs("seccomp_init returned NULL\n", stderr);
        return EXIT_FAILURE;
    }
    int status = seccomp_attr_set(context, SCMP_FLTATR_ACT_BADARCH,
                                 SCMP_ACT_KILL_PROCESS);
    int outcome = status < 0 ? report_failure("seccomp_attr_set", status)
                             : deny_syscalls(context, count, names, fixture);
    if (outcome == EXIT_SUCCESS) {
        status = seccomp_export_bpf(context, STDOUT_FILENO);
        if (status < 0) {
            outcome = report_failure("seccomp_export_bpf", status);
        }
    }
    seccomp_release(context);
    return outcome;
}

static int execute_fixture(char **command)
{
#ifdef LANDLOCK_ACCESS_FS_RESOLVE_UNIX
    long abi = syscall(SYS_landlock_create_ruleset, NULL, 0,
                       LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 0) {
        return report_failure("landlock ABI query", -errno);
    }
    if (abi < 9) {
        fprintf(stderr, "fixture requires Landlock ABI 9, found %ld\n", abi);
        return EXIT_FAILURE;
    }
    const struct landlock_ruleset_attr rules = {
        .handled_access_fs = LANDLOCK_ACCESS_FS_RESOLVE_UNIX,
        .scoped = LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET,
    };
    int descriptor = syscall(SYS_landlock_create_ruleset, &rules,
                             sizeof(rules), 0);
    if (descriptor < 0) {
        return report_failure("landlock_create_ruleset", -errno);
    }
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0 ||
        syscall(SYS_landlock_restrict_self, descriptor, 0) < 0) {
        int error = errno;
        close(descriptor);
        return report_failure("landlock fixture enforcement", -error);
    }
    if (close(descriptor) < 0) {
        return report_failure("landlock ruleset close", -errno);
    }
    execv(command[0], command);
    return report_failure("fixture execv", -errno);
#else
    (void)command;
    fputs("fixture requires Linux headers with Landlock ABI 9\n", stderr);
    return EXIT_FAILURE;
#endif
}

int main(int argc, char **argv)
{
    if (argc == 1) {
        return print_architecture();
    }
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        return print_version();
    }
    if (argc > 2 && strcmp(argv[1], "--fixture-policy") == 0) {
        return compile_policy(argc - 2, argv + 2, true);
    }
    if (argc > 2 && strcmp(argv[1], "--fixture-exec") == 0) {
        return execute_fixture(argv + 2);
    }
    return compile_policy(argc - 1, argv + 1, false);
}
