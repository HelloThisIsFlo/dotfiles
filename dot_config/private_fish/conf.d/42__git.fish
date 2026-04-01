# Git utilities
# Abbreviations via lewisacidic/fish-git-abbr plugin

function git-copy-push-remote --description "Copy the push remote URL to clipboard"
    git remote -v | tail -n1 | awk '{print $2}' | pbcopy
end

abbr greignore 'git rm -r --cached . && git add . && git commit -m "Re-apply .gitignore rules"'
