#!/bin/bash

while true; do
    python -u process_attachment_status.py
    if [ $? -eq 0 ]; then
        echo "Command executed successfully"
    else
        echo "Command failed. Restarting..."
    fi
done
