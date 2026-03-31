# Language binary directories
# Env vars (GOPATH, PYTHONSTARTUP, etc.) are set in 2x TOOL-INTEGRATIONS (23__python, 24__go, etc.)
# Those load before 80s, so variables like $GOPATH are available here.
fish_add_path --global --path $GOPATH/bin
fish_add_path --global --path $HOME/.krew/bin
fish_add_path --global --path $ASDF_DATA_DIR/installs/rust/stable/bin
