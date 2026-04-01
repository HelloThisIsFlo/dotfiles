# Docker droplets — TLS client certs for remote Docker hosts

function _activate_droplet -a secret_repo_path --description "Activate Docker droplet TLS credentials"
    test -z "$secret_repo_path"; and echo "Usage: _activate_droplet SECRET_REPO_PATH"; and return 1
    eval ($secret_repo_path/activate.sh)
    echo "Docker droplet activated: "(basename $secret_repo_path)
end

function deactivate-droplet --description "Clear Docker droplet TLS environment"
    set -e DOCKER_TLS_VERIFY
    set -e DOCKER_HOST
    set -e DOCKER_CERT_PATH
    echo "Docker droplet deactivated"
end

function activate-awesometeam
    _activate_droplet "$HOME/config-in-the-cloud/secrets/tlscertificates-awesometeam"
end

function activate-thesandbox
    _activate_droplet "$HOME/config-in-the-cloud/secrets/tlscertificates-thesandbox"
end

function activate-floriankempenich
    _activate_droplet "$HOME/config-in-the-cloud/secrets/tlscertificates-floriankempenich"
end

function activate-thehome
    _activate_droplet "$HOME/config-in-the-cloud/secrets/tlscertificates-thehome"
end

function activate-dadhome
    _activate_droplet "$HOME/config-in-the-cloud/secrets/tlscertificates-dadhome"
end
