#!/usr/bin/env python3
import sys, string

def extract_strings(data, min_len=3):
    printable = set(bytes(string.printable, 'ascii'))
    results = []
    i = 0
    while i < len(data):
        # skip nulls and non-printable
        if data[i] in printable and data[i] != 0:
            j = i
            while j < len(data) and data[j] in printable and data[j] != 0:
                j += 1
            if j - i >= min_len:
                results.append((i, data[i:j]))
            i = j
        else:
            i += 1
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: parse_dump.py dumpfile")
        raise SystemExit(1)
    fn = sys.argv[1]
    d = open(fn,'rb').read()
    strs = extract_strings(d, min_len=3)
    if not strs:
        print("No printable strings >=3 found")
    else:
        for off,s in strs:
            print("offset %04x: %r" % (off, s))
