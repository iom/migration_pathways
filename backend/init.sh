#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

python main.py