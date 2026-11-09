#!/usr/bin/env bash
# note080 PHP, Ruby and Perl observers on each token (one per line). Same output format as obs_python.py.
set -euo pipefail
T="$1"
php -r '
$t = file($argv[1], FILE_IGNORE_NEW_LINES);
echo "#versions\t" . json_encode(["php" => PHP_VERSION]) . "\n";
foreach ($t as $i => $s) {
  $v = json_decode($s);
  if (json_last_error() !== JSON_ERROR_NONE) { echo "php-json_decode\t$i\tERR\t" . json_last_error_msg() . "\n"; }
  elseif (is_float($v)) { echo "php-json_decode\t$i\tOK\t" . bin2hex(pack("E", $v)) . "\n"; }
  elseif (is_int($v)) { echo "php-json_decode\t$i\tEXACT\t$v\n"; }
  else { echo "php-json_decode\t$i\tOTHER\t" . gettype($v) . "\n"; }
}' "$T"
ruby -rjson -e '
toks = File.read(ARGV[0]).split("\n")
puts "#versions\t" + {"ruby" => RUBY_VERSION, "json" => JSON::VERSION}.to_json
[["ruby-JSON.parse", ->(s) { JSON.parse(s) }], ["ruby-Float", ->(s) { Float(s) }]].each do |name, fn|
  toks.each_with_index do |s, i|
    begin
      v = fn.call(s)
      if v.is_a?(Float) then puts "#{name}\t#{i}\tOK\t#{[v].pack("G").unpack1("H*")}"
      elsif v.is_a?(Integer) then puts "#{name}\t#{i}\tEXACT\t#{v}"
      else puts "#{name}\t#{i}\tOTHER\t#{v.class}" end
    rescue => e
      puts "#{name}\t#{i}\tERR\t#{e.class}"
    end
  end
end' "$T"
perl -MJSON::PP -e '
open(my $f, "<", $ARGV[0]) or die; my @t = <$f>; chomp @t;
print "#versions\t{\"perl\": \"$^V\", \"JSON::PP\": \"$JSON::PP::VERSION\"}\n";
my $j = JSON::PP->new->allow_nonref;
for my $i (0..$#t) {
  my $v = eval { $j->decode($t[$i]) };
  if ($@) { print "perl-JSON::PP\t$i\tERR\tdecode\n"; next; }
  print "perl-JSON::PP\t$i\tOK\t", unpack("H*", pack("d>", $v + 0)), "\n";
}' "$T"
