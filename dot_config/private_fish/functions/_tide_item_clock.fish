function _tide_item_clock
    # nf-md-numeric icons: 0-9 (fish arrays are 1-indexed, so index 1 = "0")
    set -l numbers 󰬹 󰬺 󰬻 󰬼 󰬽 󰬾 󰬿 󰭀 󰭁 󰭂
    set -l gauges '░░░░' '▒░░░' '▓░░░' '█░░░' '█▒░░' '█▓░░' '██░░' '██▒░' '██▓░' '███░' '███▒' '███▓' '████'

    set -l hour (date +%H)
    set -l minute (date +%M | string replace -r '^0' '')
    test -z "$minute" && set minute 0

    # Map two-digit hour to number icons (fish arrays are 1-indexed: [1]=0, [2]=1, ...)
    set -l d1 (math (string sub -l 1 $hour) + 1)
    set -l d2 (math (string sub -s 2 $hour) + 1)
    set -l hour_display $numbers[$d1]$numbers[$d2]

    # Map minute to gauge (13 states across 60 minutes)
    set -l gauge_index (math "floor($minute * 13 / 60) + 1")
    test $gauge_index -gt 13 && set gauge_index 13

    _tide_print_item clock $hour_display' '$gauges[$gauge_index]
end
