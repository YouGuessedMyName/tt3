#!/bin/bash
poetry run \
python3 src/adapter/plugin_adapter.py -u wss://course02.axini.com:443/adapters -t eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjU4MDk3NjAsInN1YiI6InJ1X2dyb3VwXzAzQGF4aW5pLmNvbSIsImlzcyI6InZtcHVibGljcHJvZDAxIiwic2NvcGUiOiJhZGFwdGVyIn0.g-Gsx5iDzcQEBV8UYf50voxccGseFtayndFqa9n3MHA -n ivo-laptop
