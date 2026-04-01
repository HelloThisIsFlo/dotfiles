# Misc utilities

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
