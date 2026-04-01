# System utilities

function updateall --description "Update all packages (brew on macOS, apt on Linux)"
    switch (uname)
        case Linux
            sudo apt update
            and sudo apt upgrade -y
            and sudo apt autoremove -y
        case Darwin
            brew update
            and brew upgrade
            and brew cleanup
    end
end
