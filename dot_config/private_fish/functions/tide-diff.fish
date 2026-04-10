function tide-diff -d "Compare your Tide prompt items against Tide's defaults"
    if not set -q _tide_known_defaults_right; or not set -q _tide_known_defaults_left
        echo "No stored defaults found. Run 'chezmoi apply' first to capture them."
        return 1
    end

    _experiment_diff_side "Left" $_tide_known_defaults_left -- $tide_left_prompt_items
    echo
    _experiment_diff_side "Right" $_tide_known_defaults_right -- $tide_right_prompt_items
end

function _experiment_diff_side -d "Diff one side of the prompt"
    set -l label $argv[1]
    set -l defaults
    set -l custom
    set -l phase defaults
    for arg in $argv[2..]
        if test "$arg" = --
            set phase custom
            continue
        end
        if test "$phase" = defaults
            set -a defaults $arg
        else
            set -a custom $arg
        end
    end

    set_color --bold
    echo "── $label prompt ──"
    set_color normal

    # Side-by-side table with color on added/removed items
    set -l col 20
    set -l rows (math "max($(count $defaults), $(count $custom))")

    printf "  %-"$col"s  %s\n" "Defaults" "Custom"
    printf "  %-"$col"s  %s\n" (string repeat -n $col ─) (string repeat -n $col ─)

    for i in (seq $rows)
        set -l d_item (test $i -le (count $defaults); and echo $defaults[$i]; or echo "")
        set -l c_item (test $i -le (count $custom); and echo $custom[$i]; or echo "")

        # Left column (defaults): red if removed (not in custom)
        if test -n "$d_item"; and not contains $d_item $custom
            set_color red
            printf "  %-"$col"s" $d_item
            set_color normal
        else
            printf "  %-"$col"s" $d_item
        end

        printf "  "

        # Right column (custom): green if added (not in defaults)
        if test -n "$c_item"; and not contains $c_item $defaults
            set_color green
            echo $c_item
            set_color normal
        else
            echo $c_item
        end
    end
end
