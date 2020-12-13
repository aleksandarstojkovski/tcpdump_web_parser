#!/bin/bash

if [[ -f pid ]]; then
  kill -9 $(cat pid)
  rm -f pid
  echo "stopped."
else
  echo "already stopped."
fi

