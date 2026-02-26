
# TODO: Setup Brew with Brewfile

# 1. Mac Preliminary Setup

---

1. Install command line tools
    
    ```
    xcode-select --install
    ```
    
2. Install [`brew`](https://brew.sh/)
    - Run this at the end of instalation *(Temporary - Will be erased when restoring dotfiles symlinks)*
        
        ```bash
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        ```
        

# 2. Install `asdf`

---

<aside>
⚠️ **At the moment I’m also experimenting with the following `asdf` plugins:**

- `kubectl` (official asdf plugin)
    - 1.28.2
- `terraform` (official asdf plugin)
    - 1.6.0
</aside>

1. Make sure ZSH is the default shell
    
    ```bash
    chsh -s $(which zsh)
    ```
    
2. Restart Shell
3. Install requirements
    - **OSX**
        - *Why?*
            - Python
                - `pkg-config` ← Thanks to [comment on PyEnv issue](https://github.com/pyenv/pyenv/issues/1184#issuecomment-433683530)
                - `tcl-tk` ← To make `tinker` work in python
            - PHP
                - `autoconf automake bison freetype gd gettext icu4c krb5 libedit libiconv libjpeg libpng libxml2 libzip openssl pkg-config re2c zlib`
                - `gmp libsodium imagemagick` ← Optional
        
        ```bash
        brew install \
            autoconf \
            automake \
            bison \
            coreutils \
            freetype \
            gd \
            gettext \
            gmp \
            gpg \
            icu4c \
            imagemagick \
            krb5 \
            libedit \
            libiconv \
            libjpeg \
            libpng \
            libsodium \
            libtool \
            libxml2 \
            libxslt \
            libyaml \
            libzip \
            mackup \
            openssl \
            pkg-config \
            re2c \
            readline \
            sqlite3 \
            tcl-tk \
            unixodbc \
            wxmac \
            xz \
            zlib \
            oniguruma
        ```
        
    - **Ubuntu**
        
        ```bash
        sudo apt install -y \
            autoconf \
            automake \
            build-essential \
            curl \
            dirmngr \
            fop \
            gpg \
            libbz2-dev \
            libffi-dev \
            libgl1-mesa-dev \
            libglu1-mesa-dev \
            liblzma-dev \
            libncurses-dev \
            libncurses5-dev \
            libncursesw5-dev \
            libpng-dev \
            libreadline-dev \
            libsqlite3-dev \
            libssh-dev \
            libssl-dev \
            libtool \
            libwxgtk3.0-gtk3-dev \
            libxslt-dev \
            libyaml-dev \
            llvm \
            m4 \
            tk-dev \
            unixodbc-dev \
            unzip \
            wget \
            xsltproc \
            xz-utils \
            zlib1g-dev
        ```
        
4. Install asdf
    
    ```bash
    brew install asdf
    ```
    
5. Configure `asdf` *(Temporary - Will be erased when restoring dotfiles symlinks)*
    
    ```bash
    cat << EOF >> ~/.zprofile
    export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"
    EOF
    ```
    
    - *Bash Version*
        
        ```bash
        cat << EOF >> ~/.bash_profile
        export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"
        EOF
        ```
        
6. Restart Terminal
7. Install plugins
    
    ```bash
    DEPRECATED
    See: Install Languages -> Essential
    ```
    
8. Install Languages
    - Essential (needed for cli tools)
        
        <aside>
        ❗ **Language Specific Install Notes**
        
        - `python`
            
            ```bash
            # On MAC
            # ------
            # Install command is DIFFERENT!!
            #
            # - PATH, LDFLAGS, CPPFLAGS, PKG_CONFIG_PATH, CFLAGS 
            #	    To make sure to use the correct 'tcl-tk' version
            #     This is mentioned in the caveats when installing 'tcl-tk'
            #     with homebrew
            #
            # - PYTHON_CONFIGURE_OPTS
            #     This makes tool work:
            #       - 'tinker': --with-tcltk-includes=... --with-tcltk-libs=...
            #       - 'pyinstaller': --enable-framework
            #
            # Source: https://stackoverflow.com/a/60469203/4490991
            env \
              PATH="$(brew --prefix tcl-tk)/bin:$PATH" \
              LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
              CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
              PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
              CFLAGS="-I$(brew --prefix tcl-tk)/include" \
              PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
              asdf install python 3.X.X
            
            # Multiple global
            # ---------------
            # Install both latest python2 and python3
            # Set both as `global`. First python3, then python2 
            # (ordered by priority)
            # They will be able to be picked up by pipenv
            asdf global python 3.XX 2.XX
            
            ```
            
        </aside>
        
        <aside>
        💡 If getting the error below, just re-login and try again
        
        ```bash
        tail: cannot open '/home/flo/.tool-versions' for reading: No such file or directory
        ```
        
        </aside>
        
        ```bash
        #!/usr/bin/env bash
        # Notes
        #   - Make sure to install and use the same versions as the one on my mac
        #     (because '.tool-versions' is synced)
        #   - For Python, see warning above!
        
        # Define version variables
        export ERLANG=24.3.3
        export ELIXIR=1.13.4-otp-24
        export NODEJS=22.8.0
        # For Python, we install several versions; we’ll set the default to the first one.
        export PYTHON_VERSIONS="3.12.8 3.11.11 3.10.4 3.9.12"
        export DEFAULT_PYTHON=3.12.8
        export GRADLE=7.6
        export JAVA=liberica-18+37
        export RUBY=3.1.2
        export MAVEN=3.8.5
        export GOLANG=1.22.12
        export RUST=1.83.0
        export KUBECTL=1.30.3
        export TERRAFORM=1.6.0
        export CLOJURE=1.11.1.1435
        export BABASHKA=1.3.188
        export ETCD=3.5.15
        export KREW=0.4.4
        export TALOSCTL=1.9.2
        export TALHELPER=3.0.16
        export SOPS=3.9.4
        export HELM=3.16.4
        
        # Add asdf plugins for each tool
        asdf plugin add erlang
        asdf plugin add elixir
        asdf plugin add nodejs
        asdf plugin add python
        asdf plugin add gradle
        asdf plugin add java
        asdf plugin add ruby
        asdf plugin add maven
        asdf plugin add golang
        asdf plugin add rust
        asdf plugin add kubectl
        asdf plugin add terraform
        asdf plugin add clojure
        asdf plugin add babashka
        asdf plugin add etcd
        asdf plugin add krew
        asdf plugin add talosctl
        asdf plugin add talhelper
        asdf plugin add sops
        asdf plugin add helm
        
        # List all available versions for each tool
        asdf list all erlang &&
        asdf list all elixir &&
        asdf list all nodejs &&
        asdf list all python &&
        asdf list all gradle &&
        asdf list all java &&
        asdf list all ruby &&
        asdf list all maven &&
        asdf list all golang &&
        asdf list all rust &&
        asdf list all kubectl &&
        asdf list all terraform &&
        asdf list all clojure &&
        asdf list all babashka &&
        asdf list all etcd &&
        asdf list all krew &&
        asdf list all talosctl &&
        asdf list all talhelper &&
        asdf list all sops &&
        asdf list all helm &&
        
        # Install specified versions
        asdf install erlang $ERLANG &&
        asdf install elixir $ELIXIR &&
        asdf install nodejs $NODEJS &&
        for py in $PYTHON_VERSIONS; do
            asdf install python "$py" || exit 1
        done &&
        asdf install gradle $GRADLE &&
        asdf install java $JAVA &&
        asdf install ruby $RUBY &&
        asdf install maven $MAVEN &&
        asdf install golang $GOLANG &&
        asdf install rust $RUST &&
        asdf install kubectl $KUBECTL &&
        asdf install terraform $TERRAFORM &&
        asdf install clojure $CLOJURE &&
        asdf install babashka $BABASHKA &&
        asdf install etcd $ETCD &&
        asdf install krew $KREW &&
        asdf install talosctl $TALOSCTL &&
        asdf install talhelper $TALHELPER &&
        asdf install sops $SOPS &&
        asdf install helm $HELM &&
        
        # Set global versions
        asdf set --home erlang $ERLANG &&
        asdf set --home elixir $ELIXIR &&
        asdf set --home nodejs $NODEJS &&
        asdf set --home python $DEFAULT_PYTHON &&
        asdf set --home gradle $GRADLE &&
        asdf set --home java $JAVA &&
        asdf set --home ruby $RUBY &&
        asdf set --home maven $MAVEN &&
        asdf set --home golang $GOLANG &&
        asdf set --home rust $RUST &&
        asdf set --home kubectl $KUBECTL &&
        asdf set --home terraform $TERRAFORM &&
        asdf set --home clojure $CLOJURE &&
        asdf set --home babashka $BABASHKA &&
        asdf set --home etcd $ETCD &&
        asdf set --home krew $KREW &&
        asdf set --home talosctl $TALOSCTL &&
        asdf set --home talhelper $TALHELPER &&
        asdf set --home sops $SOPS &&
        asdf set --home helm $HELM
        ```
        
    - Optional
        - `erlang`
            
            ```bash
            export KERL_BUILD_DOCS=yes
            export KERL_CONFIGURE_OPTIONS="--disable-debug --without-javac"
            ```
            
            - ***Important install notes***
        - `elixir`
            
            ```bash
            # Install from REFERENCE!! Not version
            asdf install elixir 1.10.3    # WRONG ❌
            asdf install elixir ref:v1.10 # CORRECT ✅
                                          # (without PATCH version)
            # To know which reference to install, check the latest branch on the repo
            
            ```
            
        - `gradle`
        - `ruby`

# 3. Install Common Tools

---

## Python

```bash
pip install \
    hierarchy \
    mackup \
    glances \
    docker \
    bottle \
    howdoi \
    pre-commit \
    awscli \
    pipenv \
    poetry \
    homeassistant-cli \
		ipython \
    'black[d]'
```

```bash
pip install \
    hierarchy \
    mackup \
    glances \
    docker \
    bottle \
    howdoi \
    pre-commit \
    awscli \
    pipenv \
    poetry \
    homeassistant-cli \
		ipython \
    'black[d]'
```

- `mackup` ⇒ **Important:** Needed by Ansible Magic to restore symlinks
- `docker` ⇒ Not docker-ce, but python tool for docker
- `bottle` ⇒ Required for glances web-daemon mode

## NodeJS

```bash
npm install -g \
    tern \
    js-beautify \
    eslint \
    mocha \
    nativefier \
    pragmatic-motd \
    yarn \
    diffchecker \
		fast-cli
```

## Rust

```bash
cargo install \
    git-delta
```

## Go

```bash
go install \
    github.com/cheat/cheat/cmd/cheat@latest
```

# 4. Restore ChezMoi

---

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply HelloThisIsFlo
```

# 5. Run Ansible Magic

---

- Note: **This will install `*antigen*`, if need to install manually, open toggle
    
    
    ```bash
    git clone https://github.com/zsh-users/antigen.git ~/.antigen
    ```
    

<aside>
⚠️ Make sure

- ASDF was installed
- Python was installed with ASDF
- Python has the **same version** as the one on my mac
*(because `.tool-versions` is synced)*
- Python version was set as global
- `mackup` was installed with python from ASDF
</aside>

1. Log out from the new host machine
2. Go to `ansible` folder
    
    ```bash
    cd ~/config-in-the-cloud/ansible-magic/ansible
    ```
    
3. Edit `inventory/hosts` with the correct ip for the new host (`macbook`, `thehome`, …)
    
    ```bash
    vim inventory/hosts
    ```
    
    - **Note:** `python3` should be available by default, use that instead of the default `python`
4. Create the `playbook.yml`
    
    ```bash
    cp sample-playbook.yml playbook.yml
    ```
    
5. Change `hosts` to `macbook` (instead of `localhost`)
    
    ```bash
    vim playbook.yml
    ```
    
6. Install role dependencies
    
    ```bash
    ansible-galaxy install -r requirements.yml --force
    ```
    
7. Run playbook with `ask-become-pass` option: 
    
    ```bash
    ansible-playbook -K playbook.yml
    ```
    
    - `K` is the `ask-become-pass` option

# 5. Final Touches

---

1. Reload the shell
2. Clone all repos with hierarchy
    
    ```bash
    hierarchy
    ```
    
3. Update antigen
    
    ```bash
    antigen selfupdate
    ```
    
4. Start `vim` once to trigger install of plugins
    
    ```bash
    vim
    ```
    
5. **~~[Mac]** Install Docker via Docker Desktop~~
    
    ⇒ Replace with brew cask!