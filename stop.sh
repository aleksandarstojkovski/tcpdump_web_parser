#!/bin/bash

if [[ -f pid ]]; then
  kill -9 $(cat pid)
  echo "stopped."
else
  echo "already stopped."
fi

