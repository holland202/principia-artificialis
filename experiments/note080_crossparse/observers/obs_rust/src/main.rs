// note080 Rust observer: str::parse::<f64> and serde_json (default features) on each token (one per line).
// Same output format as obs_python.py.
use std::io::{BufRead, BufReader};

fn main() {
    let path = std::env::args().nth(1).expect("tokens file");
    let toks: Vec<String> = BufReader::new(std::fs::File::open(path).unwrap()).lines().map(|l| l.unwrap()).collect();
    println!("#versions\t{{\"serde_json\": \"1.0.154\", \"rustc\": \"see build log\"}}");
    for (i, t) in toks.iter().enumerate() {
        match t.parse::<f64>() {
            Ok(v) => println!("rust-str-parse\t{}\tOK\t{:016x}", i, v.to_bits()),
            Err(_) => println!("rust-str-parse\t{}\tERR\tParseFloatError", i),
        }
    }
    for (i, t) in toks.iter().enumerate() {
        match serde_json::from_str::<f64>(t) {
            Ok(v) => println!("rust-serde_json\t{}\tOK\t{:016x}", i, v.to_bits()),
            Err(e) => println!("rust-serde_json\t{}\tERR\t{:?}", i, e.classify()),
        }
    }
}
