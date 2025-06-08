#!/bin/bash

# Usage: ./append_arc.sh /path/to/folder output.txt

INPUT_DIR="$1"
OUTPUT_FILE="$2"

# Ensure both arguments are provided
if [[ -z "$INPUT_DIR" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 /path/to/folder output.txt"
    exit 1
fi

# Clear output file
> "$OUTPUT_FILE"

# Find all .arc files recursively
find "$INPUT_DIR" -type f -name "*.arc" | while IFS= read -r FILE; do
    if [[ -f "$FILE" ]]; then
        echo "=== $FILE ===" >> "$OUTPUT_FILE"
        cat "$FILE" >> "$OUTPUT_FILE"
        echo -e "\n" >> "$OUTPUT_FILE"
    fi
done
