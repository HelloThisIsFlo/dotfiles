#!/usr/bin/env fish

# Bootstrap Fisher if not present
if not functions -q fisher
  curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
end

# Plugins
fisher install IlanCosman/tide@v6

echo "Fisher plugins installed successfully."
