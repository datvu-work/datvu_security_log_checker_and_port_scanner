#!/usr/bin/env bash

# ==============================================================================
# SecTool - Automated Setup & Permission Management Script
# ==============================================================================

# ANSI Colors for formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Starting SecTool Environment Setup...${NC}"

# 1. Verify Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] Error: Python 3 could not be found. Please install Python 3.${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Python 3 detected.${NC}"

# 2. Create the Directory Structure
echo -e "${YELLOW}[*] Validating project structure...${NC}"
mkdir -p data/blacklist
mkdir -p data/samples

# Create default blacklist if it doesn't exist
DEFAULT_BLACKLIST="data/blacklist/main_blacklist.txt"
# FIXED: Added space after 'if'
if [ ! -f "$DEFAULT_BLACKLIST" ]; then
    echo "# SecTool Default Threat Intel Blacklist" > "$DEFAULT_BLACKLIST"
    echo "# Add one IP address per line" >> "$DEFAULT_BLACKLIST"
    echo "185.156.74.65" >> "$DEFAULT_BLACKLIST"
    echo -e "${GREEN}[+] Created default blacklist at $DEFAULT_BLACKLIST${NC}"
fi

# 3. Apply Strict Permissions (Least Privilege)
echo -e "${YELLOW}[*] Applying strict file permissions...${NC}"

# Ensure src directory exists before chmod
if [ -d "src" ]; then
    chmod -R 755 src/
    chmod +x src/main.py
    echo -e "${GREEN}[+] Source code locked down (Executable/Readable by all).${NC}"
else
    echo -e "${RED}[-] Error: 'src' directory not found. Please run setup from the project root.${NC}"
    exit 1
fi

# Lock down the data directory
chmod 755 data/ data/blacklist/ data/samples/
find data/ -type f -exec chmod 644 {} \;
echo -e "${GREEN}[+] Threat Intelligence files secured (Read-only for users).${NC}"

# 4. Create a Global Wrapper Command
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BIN_DIR="/usr/local/bin"
WRAPPER_NAME="sectool"

echo -e "${YELLOW}[*] Attempting to create global 'sectool' command...${NC}"

# FIXED: Added space after 'if'
if [ -w "$BIN_DIR" ]; then
    ln -sf "${SCRIPT_DIR}/src/main.py" "${BIN_DIR}/${WRAPPER_NAME}"
    echo -e "${GREEN}[+] Successfully created global command '${WRAPPER_NAME}'.${NC}"
else
    echo -e "${YELLOW}[!] Root privileges required to add 'sectool' to system PATH.${NC}"
    sudo ln -sf "${SCRIPT_DIR}/src/main.py" "${BIN_DIR}/${WRAPPER_NAME}"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[+] Successfully created global command '${WRAPPER_NAME}'.${NC}"
    else
        echo -e "${RED}[-] Failed to create global command. Use './src/main.py' instead.${NC}"
    fi
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN} Setup Complete! SecTool is ready for your SOC team.  ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "You can now run the tool from anywhere by typing:"
echo -e "  ${YELLOW}sectool -h${NC}"