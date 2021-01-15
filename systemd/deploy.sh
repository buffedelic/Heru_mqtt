#!/usr/bin/env bash
echo "Removing existing service service"
sudo systemctl disable heru-link.service
sudo rm /etc/systemd/system/heru-link.service
echo "Done"
echo "Creating service"
sudo cp ./heru-link.service /etc/systemd/system/heru-link.service
sudo systemctl enable heru-link.service
sudo systemctl start heru-link.service
echo "Check status with 'sudo service heru-link status'"