# Docker utilities

# Docker Compose shortcuts
abbr dcreload 'docker compose up --build --timeout 0 -d'
abbr dcdown   'docker compose kill && docker compose down'
abbr dcpsa    'watch -n0.5 docker ps -a'


function docker-kill-and-remove-all-containers --description "Kill and remove all Docker containers"
    docker kill (docker ps -a -q)
    docker rm (docker ps -a -q)
end

# Docker-based utilities
function docker-hello-world -a port --description "Run nginx hello-world container on PORT"
    test -z "$port"; and echo "Usage: hello-world PORT"; and return 1
    docker run --rm --name=hello-world -eWORLD=Debug -p"$port:80" -d floriankempenich/hello-world
end

function docker-raspberry-pi --description "Start a Raspberry Pi build environment in cwd"
    docker run --rm -it -v"(pwd):/workdir" floriankempenich/raspberry-pi sh
end
