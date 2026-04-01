# TADL — torrent auto-downloader

function tadl --description "Send torrent to TADL auto-downloader with categories"
    if test (count $argv) -lt 2
        echo "Usage: tadl CATEGORY... TORRENT_FILE"
        return 1
    end

    set -l TADL_PASS (cat $HOME/.tadl-pass)
    set -l ENDPOINT "https://tadl.floriankempenich.com"

    # All args except last = categories, last = torrent file
    set -l categories $argv[1..-2]
    set -l torrent $argv[-1]
    set -l csv_categories (string join ',' $categories)

    http --body -f POST "$ENDPOINT/auto_dl" X-Tadl-Pass:"$TADL_PASS" torrent_file@$torrent categories=$csv_categories
end
