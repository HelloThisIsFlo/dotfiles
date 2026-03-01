# IPython configuration
# Auto-reload modules before executing code (no need to restart REPL after edits)
c = get_config()  # noqa
c.InteractiveShellApp.extensions = ['autoreload']
c.InteractiveShellApp.exec_lines = ['%autoreload 2']
