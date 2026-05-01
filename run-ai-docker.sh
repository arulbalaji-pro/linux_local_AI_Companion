#!/bin/bash

sudo docker build -t linux_ai_companion .

sudo docker run -d \
    --name linux_ai_companion \
    -p 5000:5000 \
    -p 8080:8080 \
    linux_ai_companion