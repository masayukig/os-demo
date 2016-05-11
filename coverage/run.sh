#!/bin/bash

while [ : ]
do
    python coverageindex.py
    cp links.json /var/www/html/cover
    scp links.json ronaldbradford.com:/var/www/ronaldbradford/demo/www/cover
    sleep 60
done
