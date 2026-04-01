# Git abbreviations and utilities
# Replaces lewisacidic/fish-git-abbr plugin with hand-managed abbrs.
# Organised by category, most-used first. --set-cursor used where helpful.

# ── Helpers (used by abbreviations below) ─────────────────────────────
# These come from the plugin — kept here so abbreviations that reference
# them continue to work.

function git_main_branch -d 'Detect name of main branch of current git repository'
    command git rev-parse --git-dir &>/dev/null || return
    for ref in refs/{heads,remotes/{origin,upstream}}/{main,master,trunk}
        if command git show-ref -q --verify $ref
            echo (string split -r -m1 -f2 / $ref)
            return
        end
    end
    echo main
end

function git_develop_branch -d 'Detect name of develop branch of current git repository'
    command git rev-parse --git-dir &>/dev/null || return
    for branch in dev devel development
        if command git show-ref -q --verify refs/heads/$branch
            echo $branch
            return
        end
    end
    echo develop
end

function git_current_branch -d 'Detect name of current branch of current git repository'
    echo (git branch --show-current)
end

function git_feature_branch_prepend -d 'Detect prepend of feature branches of git repository'
    command git rev-parse --git-dir &>/dev/null || return
    if string match -q '*/feat/*' (git show-ref)
        echo feat
        return
    end
    echo feature
end

function git-copy-push-remote --description "Copy the push remote URL to clipboard"
    git remote -v | tail -n1 | awk '{print $2}' | pbcopy
end

# ── Everyday: status, add, commit, push, pull ─────────────────────────

abbr -a gs   'git status'
abbr -a gss  'git status -s'
abbr -a gsb  'git status -sb'

abbr -a ga   'git add'
abbr -a gaa  'git add --all'
abbr -a gau  'git add --update'
abbr -a gav  'git add --verbose'
abbr -a gapa 'git add --patch'

abbr -a gc   'git commit -v'
abbr -a gc!  'git commit -v --amend'
abbr -a gcn  'git commit -v --no-edit'
abbr -a gcn! 'git commit -v --amend --no-edit'
abbr -a gcm  --set-cursor 'git commit -m "%"'
abbr -a gca  'git commit -a -v'
abbr -a gca! 'git commit -a -v --amend'
abbr -a gcam --set-cursor 'git commit -a -m "%"'
abbr -a gcan!  'git commit -a -v --no-edit --amend'
abbr -a gcans! 'git commit -a -v -s --no-edit --amend'
abbr -a gcas   'git commit -a -s'
abbr -a gcasm  --set-cursor 'git commit -a -s -m "%"'
abbr -a gcsm   --set-cursor 'git commit -s -m "%"'
abbr -a gcs  'git commit -S'
abbr -a gci  "git commit --allow-empty -v -m'chore: initial commit'"

abbr -a gp    'git push'
abbr -a gpd   'git push --dry-run'
abbr -a gpf   'git push --force-with-lease'
abbr -a gpf!  'git push --force'
abbr -a gpsu  'git push --set-upstream origin (git_current_branch)'
abbr -a gpt   'git push --tags'
abbr -a gptf  'git push --tags --force-with-lease'
abbr -a gptf! 'git push --tags --force'
abbr -a gpoat   'git push origin --all && git push origin --tags'
abbr -a gpoatf! 'git push origin --all --force && git push origin --tags --force'
abbr -a gpv   'git push -v'

abbr -a gpl    'git pull'
abbr -a gplo   'git pull origin'
abbr -a gplom  'git pull origin (git_main_branch)'
abbr -a gplu   'git pull upstream'
abbr -a gplum  'git pull upstream (git_main_branch)'

# ── Branching and switching ───────────────────────────────────────────

abbr -a gb    'git branch'
abbr -a gba   'git branch -a'
abbr -a gbd   'git branch -d'
abbr -a gbdf  'git branch -d -f'
abbr -a gbD   'git branch -D'
abbr -a gbDf  'git branch -D -f'
abbr -a gbnm  'git branch --no-merged'
abbr -a gbr   'git branch --remote'

abbr -a gco   'git checkout'
abbr -a gcob  'git checkout -b'
abbr -a gcom  'git checkout (git_main_branch)'
abbr -a gcod  'git checkout (git_develop_branch)'
abbr -a gcof  'git checkout (git_feature_branch_prepend)/'
abbr -a gcoh  'git checkout hotfix/'
abbr -a gcor  'git checkout release/'
abbr -a gcos  'git checkout support/'
abbr -a gcors 'git checkout --recurse-submodules'

abbr -a gsw   'git switch'
abbr -a gswc  'git switch -c'
abbr -a gswm  'git switch (git_main_branch)'
abbr -a gswd  'git switch (git_develop_branch)'

# ── Diff and log ──────────────────────────────────────────────────────

abbr -a gd    'git diff'
abbr -a gdca  'git diff --cached'
abbr -a gdcw  'git diff --cached --word-diff'
abbr -a gdt   'git diff-tree --no-commit-id --name-only -r'
abbr -a gdup  'git diff @{upstream}'

abbr -a gl     'git log'
abbr -a gls    'git log --stat'
abbr -a glsp   'git log --stat -p'
abbr -a glg    'git log --graph'
abbr -a glgda  'git log --graph --decorate --all'
abbr -a glgm   'git log --graph --max-count=10'
abbr -a glo    'git log --oneline --decorate'
abbr -a glog   'git log --oneline --decorate --graph'
abbr -a gloga  'git log --oneline --decorate --graph --all'
abbr -a gshow    'git show'
abbr -a gshowps 'git show --pretty=short --show-signature'

# ── Merge and rebase ─────────────────────────────────────────────────

abbr -a gm     'git merge'
abbr -a gmom   'git merge origin/(git_main_branch)'
abbr -a gmum   'git merge upstream/(git_main_branch)'
abbr -a gma    'git merge --abort'
abbr -a gmtl   'git mergetool --no-prompt'
abbr -a gmtlvim 'git mergetool --no-prompt --tool=vimdiff'

abbr -a grb    'git rebase'
abbr -a grba   'git rebase --abort'
abbr -a grbc   'git rebase --continue'
abbr -a grbd   'git rebase (git_develop_branch)'
abbr -a grbi   'git rebase -i'
abbr -a grbom  'git rebase origin/(git_main_branch)'
abbr -a grbo   'git rebase --onto'
abbr -a grbs   'git rebase --skip'

# ── Stash ─────────────────────────────────────────────────────────────

abbr -a gst     'git stash'
abbr -a gsta    'git stash apply'
abbr -a gstc    'git stash clear'
abbr -a gstd    'git stash drop'
abbr -a gstl    'git stash list'
abbr -a gstp    'git stash pop'
abbr -a gstshow 'git stash show --text'
abbr -a gstall  'git stash --all'
abbr -a gsts    --set-cursor 'git stash save "%"'

# ── Reset, restore, revert ───────────────────────────────────────────

abbr -a grs     'git reset'
abbr -a grs!    'git reset --hard'
abbr -a grsh    'git reset HEAD'
abbr -a grsh!   'git reset HEAD --hard'
abbr -a grsoh   'git reset origin/(git_current_branch)'
abbr -a grsoh!  'git reset origin/(git_current_branch) --hard'
abbr -a grs-    'git reset --'
abbr -a gpristine 'git reset --hard && git clean -dffx'

abbr -a grst    'git restore'
abbr -a grsts   'git restore --source'
abbr -a grstst  'git restore --staged'

abbr -a grev    'git revert'

# ── Remote ────────────────────────────────────────────────────────────

abbr -a gr     'git remote -v'
abbr -a gra    'git remote add'
abbr -a grau   'git remote add upstream'
abbr -a grrm   'git remote remove'
abbr -a grmv   'git remote rename'
abbr -a grset  'git remote set-url'
abbr -a gru    'git remote update'
abbr -a grv    'git remote -v'
abbr -a grvv   'git remote -vvv'

# ── Fetch ─────────────────────────────────────────────────────────────

abbr -a gf    'git fetch'
abbr -a gfa   'git fetch --all --prune'
abbr -a gfo   'git fetch origin'

# ── Cherry-pick ───────────────────────────────────────────────────────

abbr -a gcp   'git cherry-pick'
abbr -a gcpa  'git cherry-pick --abort'
abbr -a gcpc  'git cherry-pick --continue'

# ── Tags ──────────────────────────────────────────────────────────────

abbr -a gt    'git tag'
abbr -a gts   'git tag -s'
abbr -a gta   --set-cursor 'git tag -a "%"'
abbr -a gtas  --set-cursor 'git tag -a -s "%"'

# ── Worktree ──────────────────────────────────────────────────────────

abbr -a gwt    'git worktree'
abbr -a gwta   'git worktree add'
abbr -a gwtls  'git worktree list'
abbr -a gwtmv  'git worktree move'
abbr -a gwtrm  'git worktree remove'

# ── Bisect ────────────────────────────────────────────────────────────

abbr -a gbs   'git bisect'
abbr -a gbsb  'git bisect bad'
abbr -a gbsg  'git bisect good'
abbr -a gbsr  'git bisect reset'
abbr -a gbss  'git bisect start'

# ── Misc ──────────────────────────────────────────────────────────────

abbr -a g       git
abbr -a gbl     'git blame -b -w'
abbr -a gcf     'git config --list'
abbr -a gcl     'git clone --recurse-submodules'
abbr -a gclean  'git clean -id'
abbr -a gcount  'git shortlog -sn'
abbr -a gdct    'git describe --tags (git rev-list --tags --max-count=1)'
abbr -a gfg     'git ls-files | grep'
abbr -a ghh     'git help'
abbr -a gi      'git init'
abbr -a gignore  'git update-index --assume-unchanged'
abbr -a gignored 'git ls-files -v | grep "^[[:lower:]]"'
abbr -a gk      'gitk --all --branches &!'
abbr -a gke     'gitk --all (git log -g --pretty=%h) &!'
abbr -a grm     'git rm'
abbr -a grmc    'git rm --cached'
abbr -a grt     'cd (git rev-parse --show-toplevel || echo .)'
abbr -a gwch    'git whatchanged -p --abbrev-commit --pretty=medium'
abbr -a greignore 'git rm -r --cached . && git add . && git commit -m "Re-apply .gitignore rules"'

# ── Apply / am (patches) ─────────────────────────────────────────────

abbr -a gap    'git apply'
abbr -a gapt   'git apply --3way'
abbr -a gam    'git am'
abbr -a gamc   'git am --continue'
abbr -a gams   'git am --skip'
abbr -a gama   'git am --abort'
abbr -a gamscp 'git am --show-current-patch'
