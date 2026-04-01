# transfer.sh — self-hosted file sharing
set -g TRANSFER_SH_URL "https://transfersh.floriankempenich.com/"

function transfer -a file --description "Upload file/stdin to self-hosted transfer.sh"
    if test (count $argv) -eq 0
        echo "Usage:"
        echo "  transfer /tmp/test.md"
        echo "  cat /tmp/test.md | transfer test.md"
        return 1
    end

    set -l tmpfile (mktemp -t transferXXX)

    if isatty stdin
        set -l basefile (basename "$file" | sed -e 's/[^a-zA-Z0-9._-]/-/g')
        if not test -e $file
            echo "File $file doesn't exist."
            return 1
        end
        if test -d $file
            set -l zipfile (mktemp -t transferXXX.zip)
            cd (dirname $file); and zip -r -q - (basename $file) >> $zipfile
            curl --progress-bar --upload-file "$zipfile" "$TRANSFER_SH_URL$basefile.zip" >> $tmpfile
            rm -f $zipfile
        else
            curl --progress-bar --upload-file "$file" "$TRANSFER_SH_URL$basefile" >> $tmpfile
        end
    else
        curl --progress-bar --upload-file "-" "$TRANSFER_SH_URL$file" >> $tmpfile
    end

    cat $tmpfile
    echo
    rm -f $tmpfile
end
