# File utilities

function mkcd -a dir_name --description "Create directory and cd into it"
    test -z "$dir_name"; and echo "Usage: mkcd DIRNAME"; and return 1
    mkdir -p $dir_name; and cd $dir_name
end

# Create a new executable bash script with boilerplate and open in nvim
function vix -a filename --description "Create executable bash script and open in nvim"
    test -z "$filename"; and echo "Usage: vix FILENAME"; and return 1
    printf '#!/bin/bash\nset -euo pipefail\nDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"\n\ncd "$DIR"\n\n\n\ncd - >/dev/null\n' > $filename
    chmod u+x $filename
    nvim -c 'startinsert' +7 $filename
end

# Make executable the most recently created file in cwd
function x --description "chmod +x the most recently created file in cwd"
    chmod u+x (command ls -tr | tail -1)
end

# Serve current directory via nginx in Docker
function serve-current-dir -a port --description "Serve cwd via nginx Docker container on PORT"
    test -z "$port"; and echo "Usage: serve-current-dir PORT"; and return 1
    echo "Serving current dir on port '$port'"
    echo "Press 'CTRL-C' to exit"
    docker run --rm -it -p "$port:80" -v "(pwd):/usr/share/nginx/html:ro" jorgeandrada/nginx-autoindex
end

# Convert PDF to blue tint (forces color ink when black is empty)
function pdf2blue -a input_pdf --description "Convert PDF to blue tint (force color ink)"
    test -z "$input_pdf"; and echo "Usage: pdf2blue INPUT.pdf"; and return 1
    set -l output_pdf "COLOR_$input_pdf"
    # Don't go too low with the color, or the printer will use black ink anyway
    magick -density 300 "$input_pdf" +level-colors "rgb(30,30,60)",white "$output_pdf"
end
