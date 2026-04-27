#!/bin/bash
set -e

# Start Hugo server in the background
hugo server -D --source site &
SERVER_PID=$!

# Wait for server to start and open in browser
sleep 2
open http://localhost:1313

# Keep the server running
wait $SERVER_PID
