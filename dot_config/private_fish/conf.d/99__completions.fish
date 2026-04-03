# Uses cache_completions from functions/cache_completions.fish
if status is-interactive
    cache_completions chezmoi "chezmoi completion fish"
    cache_completions mise "mise completion fish"
end
