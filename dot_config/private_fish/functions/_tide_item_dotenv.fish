# Tide item: displays a ".env" indicator if the current shell environment
# matches the contents of the local .env file.
#
# Behavior:
# - Reads each line of the .env file and extracts KEY=value pairs.
# - For each variable:
#     - If the variable is not set in the shell → stop (do not show item).
#     - If the value differs from the .env file → stop.
# - If all variables match, the ".env" indicator is shown.
#
# This effectively answers: "Is my .env fully loaded into the environment?"
function _tide_item_dotenv
    # Regex for parsing simple .env lines:
    #   KEY=value
    #   KEY="value"
    #   KEY='value'
    set -l DOTENV_ASSIGNMENT_REGEX '^([A-Za-z_]\w*)=["\x27]?(.*?)["\x27]?$'

    test -f .env || return

    while read -l line
        set -l parsed_line (
            string match -rg $DOTENV_ASSIGNMENT_REGEX -- $line
        )

        test -n "$parsed_line[1]" || continue

        set -l variable_name $parsed_line[1]
        set -l dotenv_value  $parsed_line[2]

        set -q $variable_name || return
        test "$$variable_name" = "$dotenv_value" || return
    end < .env

    _tide_print_item dotenv $tide_dotenv_icon'.env'
end
