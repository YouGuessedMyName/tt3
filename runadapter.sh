#!/bin/bash
poetry run \
python3 src/adapter/plugin_adapter.py -u wss://course02.axini.com:443/adapters -t eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjU4MDY0NjIsInN1YiI6InJ1X2dyb3VwXzAzQGF4aW5pLmNvbSIsImlzcyI6InZtcHVibGljcHJvZDAxIiwic2NvcGUiOiJhZGFwdGVyIn0.cD04UoUooDiLK_Y4q_ifAn73B9B-bCIT4FmwtMb98z8 -n ivo-laptop
