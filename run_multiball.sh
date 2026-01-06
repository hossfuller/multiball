#!/bin/bash

## Change to the project directory.
cd "$(dirname "$0")"

## Set Python path
export PYTHONPATH="$(pwd)"

## Default to dbpop if no specific flag is provided
target_module="src.multiball.dbpop"

## Parse command line arguments to find module flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --db)
            target_module="src.multiball.dbpop"
            shift
            ;;
        --dl)
            target_module="src.multiball.downloader"
            shift
            ;;
        --pl)
            target_module="src.multiball.plotter"
            shift
            ;;
        --sk)
            target_module="src.multiball.skeeter"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--db|--dl|--pl|--sk] [module_arguments]"
            echo ""
            echo "Flags:"
            echo "  --db    Run database population module (default)"
            echo "  --dl    Run downloader module"
            echo "  --pl    Run plotter module"
            echo "  --sk    Run skeeter module"
            echo ""
            echo "If no flag is provided, --db (dbpop) is used by default."
            echo "All other arguments are passed to the selected module."
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

## Run the selected module with remaining arguments
echo "Running: python3 -m $target_module $@"
python3 -m "$target_module" "$@"

