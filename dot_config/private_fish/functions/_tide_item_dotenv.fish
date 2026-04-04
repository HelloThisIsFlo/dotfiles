function _tide_item_dotenv
    test -f .env || return
    _tide_print_item dotenv $tide_dotenv_icon'.env'
end
