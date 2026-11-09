-- Post-hoc forum reproducer: registered cases 12 and 28, plus the baseline.
-- Every token denotes exactly 1 as a rational number. No database file is used.
.mode list
.headers on
SELECT sqlite_version() AS sqlite_version, sqlite_source_id() AS source_id;
WITH input(label,v) AS (
  VALUES ('baseline','1e0'),
         ('integer_padding','1'||hex(zeroblob(50000))||'e-100000'),
         ('fraction_padding','0.'||hex(zeroblob(50000))||'1e100001')
)
SELECT label, length(v) AS bytes, json_valid(v) AS valid_json,
       json_extract(v,'$') AS json_value, CAST(v AS REAL) AS cast_value
FROM input;
