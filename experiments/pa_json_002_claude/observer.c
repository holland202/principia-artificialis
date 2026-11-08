/* observer.c - Claude's own SQLite observer for the PA-JSON-002 check.
 *
 * Written from the PA-JSON-002 protocol and the public SQLite C API only; ChatGPT's run.py was not read.
 * Compiled together with the official sqlite3.c, so no other SQLite library can be loaded.
 *
 * Input: a file with one token per line (no token contains a newline).
 * Output, one line per token, tab-separated:
 *   index  json_valid  json_rc  json_type  json_bits  cast_rc  cast_type  cast_bits
 * rc is the sqlite3_step() result (100 = SQLITE_ROW). bits are the binary64 bits of sqlite3_column_double(),
 * copied with memcpy and printed as 16 hex digits. A route that was not run prints "-" for type and bits.
 * The first line is "#" + sqlite3_libversion() + "\t" + sqlite3_sourceid().
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sqlite3.h"

static sqlite3_stmt *prep(sqlite3 *db, const char *sql) {
  sqlite3_stmt *s = 0;
  if (sqlite3_prepare_v2(db, sql, -1, &s, 0) != SQLITE_OK) {
    fprintf(stderr, "prepare failed: %s: %s\n", sql, sqlite3_errmsg(db));
    exit(3);
  }
  return s;
}

static uint64_t bits_of(double d) {
  uint64_t u;
  memcpy(&u, &d, sizeof u);
  return u;
}

/* Runs a two-column (type, value) statement on tok; prints rc, type and bits. */
static void route(sqlite3 *db, sqlite3_stmt *s, const char *tok, size_t n) {
  sqlite3_reset(s);
  sqlite3_clear_bindings(s);
  if (sqlite3_bind_text(s, 1, tok, (int)n, SQLITE_TRANSIENT) != SQLITE_OK) {
    fprintf(stderr, "bind failed: %s\n", sqlite3_errmsg(db));
    exit(3);
  }
  int rc = sqlite3_step(s);
  if (rc == SQLITE_ROW) {
    const unsigned char *t = sqlite3_column_text(s, 0);
    int is_real = sqlite3_column_type(s, 1) == SQLITE_FLOAT;
    double d = sqlite3_column_double(s, 1);
    printf("\t%d\t%s\t%016" PRIx64, rc, t ? (const char *)t : "NULL", is_real ? bits_of(d) : (uint64_t)0);
    if (!is_real) printf("!notfloat");
  } else {
    printf("\t%d\t-\t-", rc);
  }
}

int main(int argc, char **argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: observer TOKENS_FILE\n");
    return 2;
  }
  FILE *f = fopen(argv[1], "rb");
  if (!f) {
    perror("open");
    return 2;
  }
  sqlite3 *db = 0;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 3;
  printf("#%s\t%s\n", sqlite3_libversion(), sqlite3_sourceid());
  sqlite3_stmt *valid = prep(db, "SELECT json_valid(?1)");
  sqlite3_stmt *js = prep(db, "SELECT typeof(json_extract(?1,'$')), json_extract(?1,'$')");
  sqlite3_stmt *cast = prep(db, "SELECT typeof(CAST(?1 AS REAL)), CAST(?1 AS REAL)");
  char *line = 0;
  size_t cap = 0;
  ssize_t len;
  long idx = 0;
  while ((len = getline(&line, &cap, f)) != -1) {
    if (len > 0 && line[len - 1] == '\n') line[--len] = 0;
    sqlite3_reset(valid);
    sqlite3_clear_bindings(valid);
    sqlite3_bind_text(valid, 1, line, (int)len, SQLITE_TRANSIENT);
    int vrc = sqlite3_step(valid);
    int v = vrc == SQLITE_ROW ? sqlite3_column_int(valid, 0) : -1;
    printf("%ld\t%d", idx, v);
    if (v == 1) route(db, js, line, (size_t)len);
    else printf("\t-\t-\t-");
    route(db, cast, line, (size_t)len);
    printf("\n");
    idx++;
  }
  free(line);
  sqlite3_finalize(valid);
  sqlite3_finalize(js);
  sqlite3_finalize(cast);
  sqlite3_close(db);
  return 0;
}
