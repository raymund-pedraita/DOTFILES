# DOTFILES

DOTFILES is a personal collection of small command-line utilities. Despite the name, this repository is not limited to traditional shell dotfiles; the name is retained simply because it is how the collection is known.

## Requirements

- Python 3
- A supported clipboard command for `full_path.py`: `pbcopy`, `wl-copy`, `xclip`, `xsel`, or `clip`

The scripts use only the Python standard library, so no package installation is required.

## Utilities

### Time check

`daily/time_check.py` calculates when a work period ends. The base duration is 8 hours and 47 minutes.

Pass the starting time in zero-padded, 24-hour `HH:MM` format:

```sh
python3 daily/time_check.py 09:30
```

Optionally provide one same-day out-of-office range. Its duration is added to the base work period:

```sh
python3 daily/time_check.py 09:30 13:20-14:30
```

In this example, the 1-hour-10-minute absence moves the expected end time from `18:17` to `19:27`. The range must be increasing and use `HH:MM-HH:MM` format.

### Full path

`daily/full_path.py` resolves a relative or absolute path, prints the result, and copies it to the system clipboard:

```sh
python3 daily/full_path.py ./daily
```

If no path is supplied, the current directory is used. The resolved path is still printed if no supported clipboard utility is available, but the script exits with an error status.

## Neovim Configuration

The repository includes a modern, Python-focused Neovim starter configuration in `daily/.config/nvim/`.

### Installation

To use this configuration, run the following commands from the repository root.

If `~/.config/nvim` does not exist, create the parent configuration directory and
link this repository's Neovim configuration:

```sh
mkdir -p ~/.config
ln -s "$(pwd)/daily/.config/nvim" ~/.config/nvim
```

The `mkdir -p` command is safe whether or not `~/.config` already exists.

If `~/.config/nvim` already exists, preserve it before creating the link:

```sh
mv ~/.config/nvim ~/.config/nvim.backup
ln -s "$(pwd)/daily/.config/nvim" ~/.config/nvim
```

Choose a different backup name if `~/.config/nvim.backup` already exists. This
applies whether the existing `nvim` path is a directory or a symbolic link.

Launch Neovim after installation:

```sh
nvim
```

On the first launch, `lazy.nvim` will automatically bootstrap and install the
configured plugins.

### Features

- **Plugin Manager**: Managed via [lazy.nvim](https://github.com/folke/lazy.nvim).
- **Theme**: [tokyonight.nvim](https://github.com/folke/tokyonight.nvim).
- **Highlighting & Indentation**: [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter) with auto-installed parsers for Python, Lua, JSON, TOML, YAML, and Markdown.
- **Fuzzy Finder**: [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim) for files, buffers, and grep searches.
- **LSP Support**: Automatically configures LSP servers via [mason.nvim](https://github.com/williamboman/mason.nvim) and [mason-lspconfig.nvim](https://github.com/williamboman/mason-lspconfig.nvim). Python support includes `pyright` and `ruff`.
- **Auto-Formatting**: Configured via [conform.nvim](https://github.com/stevearc/conform.nvim) to format Python files using `isort` and `black` on save.
- **Quality of Life**:
  - Automatically trims trailing whitespace on save for supported filetypes.
  - Keeps cursor centered with scroll offsets.
  - Shares system clipboard via `unnamedplus`.

### Custom Commands

- **`:ToCheckBox`**: Converts checklist items (e.g., lines containing `[x]`, `[ ] ` or starting with 4 spaces) into a cleaner format. It replaces `[x]` with `✅`, strips empty `[ ] ` checkbox markers, and removes four leading spaces. This is useful for formatting task lists and clean copy-pasting.

## Development

Run a quick syntax check for all scripts with:

```sh
python3 -m py_compile daily/*.py
```

See [AGENTS.md](AGENTS.md) for repository structure, coding conventions, testing expectations, and contribution guidelines.
~~~~