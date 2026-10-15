/*
 * Native libseccomp policy compiler for the CLI process owner.
 *
 * Build and qualification belong to the declared bootstrap toolchain.
 * The process owner supplies its validated symbolic syscall obligations.
 * Copyright (c) 2026 FLEXT Team. All rights reserved.
 * SPDX-License-Identifier: MIT
 */

#include <errno.h>
#include <inttypes.h>
#include <seccomp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int report_failure(const char *operation, int status)
{
    fprintf(stderr, "%s: native_status=%d\n", operation, status);
    return EXIT_FAILURE;
}

int main(int argc, char **argv)
{
    if (argc == 1) {
        uint32_t architecture = seccomp_arch_native();
        if (architecture == SCMP_ARCH_NATIVE) {
            fprintf(stderr, "seccomp_arch_native: unresolved token=%" PRIu32 "\n",
                    architecture);
            return EXIT_FAILURE;
        }
        if (printf("%" PRIu32 "\n", architecture) < 0 ||
            fflush(stdout) == EOF) {
            return report_failure("native architecture output", -errno);
        }
        return EXIT_SUCCESS;
    }

    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
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

    scmp_filter_ctx context = seccomp_init(SCMP_ACT_ALLOW);
    if (context == NULL) {
        fputs("seccomp_init returned NULL\n", stderr);
        return EXIT_FAILURE;
    }

    int status = seccomp_attr_set(context, SCMP_FLTATR_ACT_BADARCH,
                                 SCMP_ACT_KILL_PROCESS);
    if (status < 0) {
        seccomp_release(context);
        return report_failure("seccomp_attr_set", status);
    }

    for (int index = 1; index < argc; ++index) {
        int syscall_number = seccomp_syscall_resolve_name(argv[index]);
        if (syscall_number == __NR_SCMP_ERROR) {
            fprintf(stderr, "unresolved syscall: %s\n", argv[index]);
            seccomp_release(context);
            return report_failure("seccomp_syscall_resolve_name",
                                  syscall_number);
        }
        status = seccomp_rule_add_array(context, SCMP_ACT_ERRNO(EACCES),
                                       syscall_number, 0, NULL);
        if (status < 0) {
            seccomp_release(context);
            return report_failure("seccomp_rule_add_array", status);
        }
    }

    status = seccomp_export_bpf(context, STDOUT_FILENO);
    seccomp_release(context);
    if (status < 0) {
        return report_failure("seccomp_export_bpf", status);
    }
    return EXIT_SUCCESS;
}
