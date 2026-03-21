# Uses cache_completions from functions/cache_completions.fish
if status is-interactive
    cache_completions asdf "asdf completion fish"
    cache_completions chezmoi "chezmoi completion fish"
end
