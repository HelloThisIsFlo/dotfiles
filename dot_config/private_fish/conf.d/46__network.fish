# Network utilities

function local-ip --description "Print local 192.168.x.x IP address"
    ifconfig | awk '/192\.168\..*/ {print $2}'
end

function find-devices-on-local-network --description "Scan local network for devices (requires nmap)"
    if not command -q nmap
        echo "nmap is not installed. Install with: brew install nmap"
        return 1
    end
    set -l ip (local-ip)
    set -l class_c_network (string replace -r '\.[^.]+$' '.0/24' $ip)

    echo "Local IP: $ip"
    echo "Class C Network: $class_c_network"
    echo
    nmap -sP $class_c_network
end

alias show-all-ports-in-use 'sudo lsof -PiTCP -sTCP:LISTEN'

# termbin — pastebin from terminal
# Usage: echo "something" | tb    → returns URL
#        curl TERMBIN_URL          → view content
#        tbrun TERMBIN_URL         → download and execute
alias tb 'nc termbin.com 9999'
function tbrun -a url --description "Download and execute a termbin paste"
    curl -s $url | bash
end
