#!/bin/bash

DEVICE_USER="arul"
DEVICE_IP="192.168.29.151"
TARGET_DIR="/home/arul/test-ai-git2/linux_local_AI_Companion/voice-server"

echo "Connecting to $DEVICE_USER@$DEVICE_IP ..."
echo ""

read -p "Choose delete option (1=wav, 2=log, 3=both): " choice

ssh "$DEVICE_USER@$DEVICE_IP" bash << EOF

TARGET_DIR="$TARGET_DIR"

echo "Calculating before size..."
BEFORE=\$(du -sb "\$TARGET_DIR" | awk '{print \$1}')
BEFORE_HUMAN=\$(du -sh "\$TARGET_DIR" | awk '{print \$1}')

echo "Before: \$BEFORE_HUMAN"

case $choice in
  1)
    echo "Deleting wav files..."
    rm -f "\$TARGET_DIR"/*.wav
    ;;
  2)
    echo "Deleting chat_log.txt..."
    rm -f "\$TARGET_DIR/chat_log.txt"
    ;;
  3)
    echo "Deleting both..."
    rm -f "\$TARGET_DIR"/*.wav "\$TARGET_DIR/chat_log.txt"
    ;;
  *)
    echo "Invalid option"
    exit 1
    ;;
esac

AFTER=\$(du -sb "\$TARGET_DIR" | awk '{print \$1}')
AFTER_HUMAN=\$(du -sh "\$TARGET_DIR" | awk '{print \$1}')

FREED=\$((BEFORE - AFTER))

echo ""
echo "========================"
echo "Before : \$BEFORE_HUMAN"
echo "After  : \$AFTER_HUMAN"
echo "Freed  : \$(numfmt --to=iec \$FREED)"
echo "========================"

EOF