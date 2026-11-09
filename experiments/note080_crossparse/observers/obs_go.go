// note080 Go observer: strconv.ParseFloat and encoding/json on each token (one per line).
// Same output format as obs_python.py. A returned error is recorded as ERR, whatever value came with it.
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"runtime"
	"strconv"
)

func main() {
	f, err := os.Open(os.Args[1])
	if err != nil {
		os.Exit(2)
	}
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1<<20), 1<<22)
	var toks []string
	for sc.Scan() {
		toks = append(toks, sc.Text())
	}
	fmt.Printf("#versions\t{\"go\": %q}\n", runtime.Version())
	for i, t := range toks {
		v, err := strconv.ParseFloat(t, 64)
		if err != nil {
			fmt.Printf("go-strconv\t%d\tERR\t%T\n", i, err)
		} else {
			fmt.Printf("go-strconv\t%d\tOK\t%016x\n", i, math.Float64bits(v))
		}
	}
	for i, t := range toks {
		var v float64
		if err := json.Unmarshal([]byte(t), &v); err != nil {
			fmt.Printf("go-encoding/json\t%d\tERR\t%T\n", i, err)
		} else {
			fmt.Printf("go-encoding/json\t%d\tOK\t%016x\n", i, math.Float64bits(v))
		}
	}
}
