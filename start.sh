#!/bin/bash
echo "Installing Playwright dependencies..."
playwright install --with-deps
python main.py