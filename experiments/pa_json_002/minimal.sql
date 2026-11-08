-- Post-hoc convenience reproducer of registered cases 12 and 28, plus baseline.
-- Each v below denotes exactly 1 as a rational number. No persistent database.
.mode list
.headers on
SELECT sqlite_version() AS sqlite_version, sqlite_source_id() AS source_id;
WITH input(label,v) AS (
  VALUES ('baseline','1e0'),
         ('integer_padding','1'||hex(zeroblob(50000))||'e-100000'),
         ('fraction_padding','0.'||hex(zeroblob(50000))||'1e100001')
)
SELECT label, length(v) AS bytes, json_valid(v) AS valid_json,
       typeof(json_extract(v,'$')) AS sql_type,
       json_extract(v,'$') AS parsed_value
FROM input;
