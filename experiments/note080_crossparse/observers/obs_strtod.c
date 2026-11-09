/* note080 C observer: glibc strtod on each token (one per line). Same output format as obs_python.py.
 * strtod signalling ERANGE is recorded as ERR, because it is the C library's explicit range report. */
#include <errno.h>
#include <gnu/libc-version.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "rb");
  if (!f) return 2;
  printf("#versions\t{\"glibc\": \"%s\"}\n", gnu_get_libc_version());
  char *line = 0; size_t cap = 0; ssize_t n; long i = 0;
  while ((n = getline(&line, &cap, f)) != -1) {
    if (n && line[n - 1] == '\n') line[--n] = 0;
    char *end; errno = 0;
    double d = strtod(line, &end);
    if (*end != 0) printf("glibc-strtod\t%ld\tERR\tpartial-parse\n", i);
    else if (errno == ERANGE) printf("glibc-strtod\t%ld\tERR\tERANGE\n", i);
    else { uint64_t u; memcpy(&u, &d, 8); printf("glibc-strtod\t%ld\tOK\t%016" PRIx64 "\n", i, u); }
    i++;
  }
  return 0;
}
