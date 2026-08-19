-- =========================================
-- Neovim starter config (Python-focused)
-- Save as: ~/.config/nvim/init.lua
-- =========================================

-- Leader key
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- Basic UI/options
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"
vim.opt.cursorline = true
vim.opt.wrap = true             -- Enable soft wrapping
vim.opt.linebreak = true        -- Wrap at word boundaries
vim.opt.breakindent = true      -- Keep indentation on wrapped lines
vim.opt.showbreak = "↪ "        -- Show a marker on wrapped screen lines (optional)
vim.opt.scrolloff = 8
vim.opt.sidescrolloff = 8
vim.opt.splitright = true
vim.opt.splitbelow = true

-- Editing
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.smartindent = true
vim.opt.clipboard = "unnamedplus"
vim.opt.updatetime = 250
vim.opt.timeoutlen = 400

-- Diagnostic UI
vim.diagnostic.config({
  virtual_text = true,
  float = { border = "rounded" },
  severity_sort = true,
})

-- Keymaps (a few good defaults)
local map = vim.keymap.set
map("n", "<leader>e", vim.diagnostic.open_float, { desc = "Line diagnostics" })
map("n", "[d", vim.diagnostic.goto_prev, { desc = "Prev diagnostic" })
map("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })

-- =========================================
-- Bootstrap lazy.nvim (plugin manager)
-- =========================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- =========================================
-- Plugins
-- =========================================
require("lazy").setup({
  -- Nice defaults + Lua helpers
  { "nvim-lua/plenary.nvim" },

  -- Theme (simple, no fuss)
  { "folke/tokyonight.nvim", priority = 1000, config = function()
      vim.cmd.colorscheme("tokyonight")
    end
  },

  -- Treesitter highlighting
  { "nvim-treesitter/nvim-treesitter", lazy = false, build = ":TSUpdate", config = function()
      local treesitter = require("nvim-treesitter")
      local languages = { "lua", "python", "json", "toml", "yaml", "markdown" }

      treesitter.setup()
      treesitter.install(languages)

      vim.api.nvim_create_autocmd("FileType", {
        pattern = languages,
        callback = function(args)
          vim.treesitter.start(args.buf)
          vim.bo[args.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
        end,
      })
    end
  },

  { "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      local telescope = require("telescope")
      local builtin = require("telescope.builtin")

      telescope.setup({})

      map("n", "<leader>ff", builtin.find_files, { desc = "Find files" })
      map("n", "<leader>fg", builtin.live_grep,  { desc = "Live grep" })
      map("n", "<leader>fb", builtin.buffers,    { desc = "Buffers" })

      -- Grep word under cursor (default behavior)
      map("n", "<leader>fw", builtin.grep_string, { desc = "Grep word under cursor" })

      -- Grep whole word under cursor (rg -w)
      map("n", "<leader>fm", function()
        builtin.grep_string({ word_match = "-w" })
      end, { desc = "Grep whole word under cursor" })
    end
  },

  -- Git signs in gutter
  { "lewis6991/gitsigns.nvim", config = function()
      require("gitsigns").setup()
    end
  },

  -- LSP + Mason installer
  { "williamboman/mason.nvim", config = function() require("mason").setup() end },
  { "williamboman/mason-lspconfig.nvim" },

  -- Neovim LSP config
  { "neovim/nvim-lspconfig" },

  -- Completion
  { "hrsh7th/nvim-cmp" },
  { "hrsh7th/cmp-nvim-lsp" },
  { "hrsh7th/cmp-buffer" },
  { "hrsh7th/cmp-path" },

  -- Snippets
  { "L3MON4D3/LuaSnip" },
  { "saadparwaiz1/cmp_luasnip" },

  -- Formatting (lightweight, fast)
  { "stevearc/conform.nvim" },

}, {
  checker = { enabled = true, notify = false },
  change_detection = { notify = true },
})

-- =========================================
-- LSP setup
-- =========================================
local lspconfig = require("lspconfig")

-- Capabilities for nvim-cmp
local cmp = require("cmp")
local cmp_lsp = require("cmp_nvim_lsp")
local capabilities = cmp_lsp.default_capabilities()

-- Completion setup
cmp.setup({
  snippet = {
    expand = function(args) require("luasnip").lsp_expand(args.body) end,
  },
  mapping = cmp.mapping.preset.insert({
    ["<C-Space>"] = cmp.mapping.complete(),
    ["<CR>"] = cmp.mapping.confirm({ select = true }),
    ["<Tab>"] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_next_item()
      else
        fallback()
      end
    end, { "i", "s" }),
    ["<S-Tab>"] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_prev_item()
      else
        fallback()
      end
    end, { "i", "s" }),
  }),
  sources = cmp.config.sources({
    { name = "nvim_lsp" },
    { name = "luasnip" },
    { name = "path" },
    { name = "buffer" },
  }),
})

-- LSP keymaps when server attaches
local on_attach = function(_, bufnr)
  local opts = { buffer = bufnr }
  map("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "Go to definition" }))
  map("n", "gr", vim.lsp.buf.references, vim.tbl_extend("force", opts, { desc = "References" }))
  map("n", "K", vim.lsp.buf.hover, vim.tbl_extend("force", opts, { desc = "Hover" }))
  map("n", "<leader>rn", vim.lsp.buf.rename, vim.tbl_extend("force", opts, { desc = "Rename" }))
  map("n", "<leader>ca", vim.lsp.buf.code_action, vim.tbl_extend("force", opts, { desc = "Code action" }))
  map("n", "<leader>f", function() require("conform").format({ lsp_fallback = true }) end,
    vim.tbl_extend("force", opts, { desc = "Format" }))
end

-- Mason: install LSP servers automatically
require("mason-lspconfig").setup({
  ensure_installed = {
    "pyright", -- type checking + intellisense
    "ruff",    -- ruff lsp (fast linting/format suggestions)
  },
})

-- Mason: install LSP servers automatically
require("mason-lspconfig").setup({
  ensure_installed = {
    "pyright",
    "ruff",
  },

  -- v2: handlers live HERE (setup_handlers() was removed)
  handlers = {
    function(server_name)
      require("lspconfig")[server_name].setup({
        on_attach = on_attach,
        capabilities = capabilities,
      })
    end,

    -- Optional: Ruff special-case (totally fine to keep default too)
    ["ruff"] = function()
      require("lspconfig").ruff.setup({
        on_attach = on_attach,
        capabilities = capabilities,
      })
    end,
  },
})

-- =========================================
-- Formatting with conform.nvim
-- =========================================
require("conform").setup({
  formatters_by_ft = {
    python = { "isort", "black" },
  },
  format_on_save = function(bufnr)
    -- Only autoformat normal files
    if vim.bo[bufnr].buftype ~= "" then return end
    return { timeout_ms = 2000, lsp_fallback = true }
  end,
})

-- Optional: set Python host (usually not needed unless you use python-based plugins)
-- vim.g.python3_host_prog = vim.fn.exepath("python3")
-- Trim trailing whitespace on save (only for selected filetypes)
local trim_group = vim.api.nvim_create_augroup("TrimTrailingWhitespace", { clear = true })

local trim_fts = {
  python = true,
  yaml = true,
  -- (YAML files are still filetype "yaml"; *.yml is also "yaml")
  typescript = true,
  typescriptreact = true, -- tsx
  javascript = true,
  javascriptreact = true, -- jsx
  ruby = true,
  lua = true,
  json = true,
  toml = true,
  sh = true,
  go = true,
  rust = true,
  c = true,
  cpp = true,
  java = true,
  md = true,
}

vim.api.nvim_create_autocmd("BufWritePre", {
  group = trim_group,
  callback = function(args)
    local buf = args.buf

    -- Skip special buffers
    if vim.bo[buf].buftype ~= "" then return end
    if not vim.bo[buf].modifiable then return end

    local ft = vim.bo[buf].filetype
    if not trim_fts[ft] then return end

    -- Preserve cursor/view + search register
    local view = vim.fn.winsaveview()
    local old_search = vim.fn.getreg("/")

    -- Remove trailing whitespace
    vim.cmd([[silent! %s/\s\+$//e]])

    vim.fn.setreg("/", old_search)
    vim.fn.winrestview(view)
  end,
})
-- Optional
vim.opt.fixendofline = true

-- =========================================
-- Custom commands
-- =========================================
vim.api.nvim_create_user_command("ToCheckBox", function()
  local script_dir = debug.getinfo(1, "S").source:sub(2):match("(.*[/\\])")
  dofile(script_dir .. "checkbox_to_emoji.lua")
end, { desc = "Replace [x] with ✅ in current buffer" })
