#!/bin/bash

if [[ ! -f pid ]]; then
  nohup python3 main.py "$@" > /dev/null 2>&1 &
  echo $! > pid
else
  echo "process already started, pid: $(cat pid)"
fi
