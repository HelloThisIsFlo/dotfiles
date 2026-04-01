# Docker abbreviations
# Replaces akomuj/fish-docker-abbr plugin with hand-managed abbrs.
# Uses `d` prefix (not `dk`), `docker compose` (not `docker-compose`).

# ── Core ─────────────────────────────────────────────────────────────

abbr -a d      'docker'
abbr -a dr     'docker run'
abbr -a dri    'docker run -it --rm'
abbr -a drie   'docker run -it --rm --entrypoint /bin/bash'
abbr -a de     'docker exec'
abbr -a dei    'docker exec -it'
abbr -a da     'docker attach'
abbr -a dl     'docker logs'
abbr -a dL     'docker logs -f'
abbr -a dps    'docker ps'
abbr -a dpsa   'docker ps -a'
abbr -a dx     'docker stop'
abbr -a dk     'docker kill'
abbr -a dkh    'docker kill -s HUP'
abbr -a ds     'docker start'
abbr -a dS     'docker restart'
abbr -a dp     'docker pause'
abbr -a dP     'docker unpause'
abbr -a dw     'docker wait'
abbr -a dss    'docker stats'
abbr -a dtop   'docker top'

# ── Images ───────────────────────────────────────────────────────────

abbr -a di     'docker images'
abbr -a db     'docker build'
abbr -a dpl    'docker pull'
abbr -a dph    'docker push'
abbr -a dt     'docker tag'
abbr -a dh     'docker history'
abbr -a dim    'docker import'
abbr -a dsv    'docker save'
abbr -a drmi   'docker rmi'

# ── Container lifecycle ──────────────────────────────────────────────

abbr -a drm    'docker rm'
abbr -a drn    'docker rename'
abbr -a dup    'docker update'
abbr -a din    'docker inspect'
abbr -a dd     'docker diff'
abbr -a dv     'docker version'

# ── Auth ─────────────────────────────────────────────────────────────

abbr -a dli    'docker login'
abbr -a dlo    'docker logout'

# ── Compose ──────────────────────────────────────────────────────────

abbr -a dc     'docker compose'
abbr -a dcu    'docker compose up'
abbr -a dcU    'docker compose up -d'
abbr -a dcd    'docker compose down'
abbr -a dcb    'docker compose build'
abbr -a dcB    'docker compose build --no-cache'
abbr -a dce    'docker compose exec'
abbr -a dcr    'docker compose run'
abbr -a dcR    'docker compose run --rm'
abbr -a dcl    'docker compose logs'
abbr -a dcL    'docker compose logs -f'
abbr -a dcps   'docker compose ps'
abbr -a dcs    'docker compose start'
abbr -a dcx    'docker compose stop'
abbr -a dcS    'docker compose restart'
abbr -a dck    'docker compose kill'
abbr -a dcp    'docker compose pause'
abbr -a dcP    'docker compose unpause'
abbr -a dcpl   'docker compose pull'
abbr -a dcph   'docker compose push'
abbr -a dcrm   'docker compose rm'
abbr -a dcsc   'docker compose scale'
abbr -a dcv    'docker compose version'

# ── Container subcommand ─────────────────────────────────────────────

abbr -a dC     'docker container'
abbr -a dCa    'docker container attach'
abbr -a dCcp   'docker container cp'
abbr -a dCd    'docker container diff'
abbr -a dCe    'docker container exec'
abbr -a dCei   'docker container exec -it'
abbr -a dCin   'docker container inspect'
abbr -a dCk    'docker container kill'
abbr -a dCl    'docker container logs'
abbr -a dCL    'docker container logs -f'
abbr -a dCls   'docker container ls'
abbr -a dCp    'docker container pause'
abbr -a dCpr   'docker container prune'
abbr -a dCrn   'docker container rename'
abbr -a dCS    'docker container restart'
abbr -a dCrm   'docker container rm'
abbr -a dCr    'docker container run'
abbr -a dCri   'docker container run -it --rm'
abbr -a dCrie  'docker container run -it --rm --entrypoint /bin/bash'
abbr -a dCs    'docker container start'
abbr -a dCss   'docker container stats'
abbr -a dCx    'docker container stop'
abbr -a dCtop  'docker container top'
abbr -a dCP    'docker container unpause'
abbr -a dCup   'docker container update'
abbr -a dCw    'docker container wait'

# ── Image subcommand ─────────────────────────────────────────────────

abbr -a dI     'docker image'
abbr -a dIb    'docker image build'
abbr -a dIh    'docker image history'
abbr -a dIim   'docker image import'
abbr -a dIin   'docker image inspect'
abbr -a dIls   'docker image ls'
abbr -a dIpr   'docker image prune'
abbr -a dIpl   'docker image pull'
abbr -a dIph   'docker image push'
abbr -a dIrm   'docker image rm'
abbr -a dIsv   'docker image save'
abbr -a dIt    'docker image tag'

# ── Volume subcommand ────────────────────────────────────────────────

abbr -a dV     'docker volume'
abbr -a dVin   'docker volume inspect'
abbr -a dVls   'docker volume ls'
abbr -a dVpr   'docker volume prune'
abbr -a dVrm   'docker volume rm'

# ── Network subcommand ───────────────────────────────────────────────

abbr -a dN     'docker network'
abbr -a dNs    'docker network connect'
abbr -a dNx    'docker network disconnect'
abbr -a dNin   'docker network inspect'
abbr -a dNls   'docker network ls'
abbr -a dNpr   'docker network prune'
abbr -a dNrm   'docker network rm'

# ── System ───────────────────────────────────────────────────────────

abbr -a dY     'docker system'
abbr -a dYdf   'docker system df'
abbr -a ddf    'docker system df'
abbr -a dYpr   'docker system prune'
abbr -a dRM    'docker system prune'

# ── Stack ────────────────────────────────────────────────────────────

abbr -a dK     'docker stack'
abbr -a dKls   'docker stack ls'
abbr -a dKps   'docker stack ps'
abbr -a dKrm   'docker stack rm'

# ── Swarm ────────────────────────────────────────────────────────────

abbr -a dW     'docker swarm'

# ── Cleanup helpers ──────────────────────────────────────────────────

abbr -a drmC   'docker rm (docker ps -qaf status=exited)'
abbr -a drmI   'docker rmi (docker images -qf dangling=true)'
abbr -a drmV   'docker volume rm (docker volume ls -qf dangling=true)'
abbr -a dplI   'docker images --format "{{ .Repository }}" | grep -v "^<none>$" | xargs -L1 docker pull'
