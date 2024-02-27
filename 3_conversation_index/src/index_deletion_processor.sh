#!/bin/bash

while true; do
    python -u deletion_task.py
    if [ $? -eq 0 ]; then
        echo "Command executed successfully"
    else
        echo "Command failed. Restarting..."
    fi
done
