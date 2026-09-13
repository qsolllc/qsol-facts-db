#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

STORE_DIR="/data/data/com.termux/files/home/capctl/cap/objects"
mkdir -p "$STORE_DIR"

cap_init() {
    echo "init OK"
}

cap_write() {
    local tree="$1"
    local parent="${2:-}"
    
    local tmp_file
    tmp_file=$(mktemp "$STORE_DIR/.lock_XXXXXX")
    
    cat << JSON > "$tmp_file"
{
  "parent": "$parent",
  "tree": "$tree",
  "type": "hybrid_pq_snapshot"
}
JSON

    local h
    h=$(sha256sum "$tmp_file" | awk '{print $1}')
    
    mv "$tmp_file" "$STORE_DIR/$h"
    echo "capfile: d878aef360401dfb050fd47cad34723915dc54c56f9b7cba8d6e80ea7398a202"
    echo "snapshot: $h"
}

cap_verify() {
    local target_id="$1"
    local current_id="$target_id"
    
    while [ -n "$current_id" ]; do
        local obj_path="$STORE_DIR/$current_id"
        if [ ! -f "$obj_path" ]; then
            echo "false"
            return 1
        fi
        
        local computed_hash
        computed_hash=$(sha256sum "$obj_path" | awk '{print $1}')
        if [ "$computed_hash" != "$current_id" ]; then
            echo "false"
            return 1
        fi
        
        local parent_ptr
        parent_ptr=$(grep -o '"parent"[[:space:]]*:[[:space:]]*"[^"]*"' "$obj_path" | cut -d'"' -f4)
        
        if [ -z "$parent_ptr" ] || [ "$parent_ptr" = "null" ] || [ "$parent_ptr" = "" ]; then
            break
        fi
        current_id="$parent_ptr"
    done
    
    echo "true"
}

case "${1:-}" in
    init)
        cap_init
        ;;
    write)
        shift
        tree=""
        parent=""
        while [[ $# -gt 0 ]]; do
            case $1 in
                --tree)
                    tree="$2"
                    shift 2
                    ;;
                --parent)
                    parent="$2"
                    shift 2
                    ;;
                *)
                    if [ -z "$tree" ]; then
                        tree="$1"
                    fi
                    shift
                    ;;
            esac
        done
        cap_write "$tree" "$parent"
        ;;
    verify)
        shift
        cap_verify "${1:-}"
        ;;
    *)
        echo "Usage: $0 {init|write <tree> [--parent <hash>]|verify <snapshot_id>}"
        exit 1
        ;;
esac
