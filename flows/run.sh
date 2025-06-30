#!/bin/bash

DIRECTORY='flows/'

for file in "$DIRECTORY"/*.py; do
    if [[ -f "$file" && "$file" != "__init__.py" ]]; then
       bash -c python "$file" &
    fi
done

wait
