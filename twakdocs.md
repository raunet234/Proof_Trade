
Trust Developers
Search…
⌘
k

Get Started
Trust Wallet Agent SDK
Quickstart
CLI Reference
Authentication
Key Management
TrustConnect SDK
MCP Servers
Agent Skills
Developing for Trust Wallet platform
Listing new dApps
Listing new assets
Wallet Core
Barz - Smart Wallet

Powered by GitBook
On this page
Step 1 — Install the CLI
Step 2 — Configure credentials
Step 3 — Make your first request
Step 4 — Explore more commands
Next steps
Was this helpful?








Ask

Trust Wallet Agent SDK
Quickstart
Get from zero to your first API call in under 5 minutes using the twak CLI.

Step 1 — Install the CLI
Run directly without installing (recommended):


Ask

Copy
npx @trustwallet/cli --version
Or install globally:


Ask

Copy
npm install -g @trustwallet/cli
twak --version
Permission denied? If you get EACCES on macOS/Linux, either use npx @trustwallet/cli (no install needed), install Node via nvm (avoids /usr/local permissions), or run sudo npm install -g @trustwallet/cli.

Step 2 — Configure credentials
Get your API key and HMAC secret from the developer portal, then run:


Ask

Copy
twak init --api-key your_access_id \
          --api-secret your_hmac_secret
Credentials are stored in ~/.twak/credentials.json (file permissions 0600). This is the recommended approach for local development.

For CI/CD pipelines, use environment variables instead:


Ask

Copy
export TWAK_ACCESS_ID=your_access_id
export TWAK_HMAC_SECRET=your_hmac_secret
Do not add these exports to ~/.zshrc or ~/.bashrc. Use twak init for persistent local credentials — it stores them in a dedicated file with restricted permissions. Env vars are intended for ephemeral CI/CD environments.

Confirm the setup:


Ask

Copy
twak auth status
Never commit your HMAC secret to version control. If using a .env file, add it to .gitignore.

Step 3 — Make your first request
Fetch the current ETH price — no wallet required:


Ask

Copy
twak price ETH
Add --json for machine-readable output:


Ask

Copy
twak price ETH --json
List all supported chains:


Ask

Copy
twak chains
Step 4 — Explore more commands

Ask

Copy
# ETH balance for any address (coin 60 = Ethereum)
twak balance --address <addr> --coin 60

# All token holdings for an address
twak holdings --address <addr> --coin 60

# Trending tokens (with optional category and sort)
twak trending --limit 5
twak trending --category ai
twak trending --category memes --sort volume

# Browse DApps and protocols
twak dapps
twak dapps --category defi

# Search for tokens by name or symbol
twak search uniswap

# Transaction history for an address
twak history --address <addr> --chain ethereum

# Security / rug-risk check for a token
twak risk c60_t0x1f9840a85d5af5bf1d1762f925bdaddc4201f984

# Create an embedded agent wallet
twak wallet create --password <pw>

# Portfolio with USD values across all chains
twak wallet portfolio

# Get a swap quote first, then execute
twak swap 0.1 ETH USDC --chain ethereum --quote-only
twak swap 0.1 ETH USDC --chain ethereum

# Start an MCP server for AI agent integrations
twak serve
Run any command with --help to see all options.

Next steps
CLI Reference — full command reference

Authentication — how HMAC signing works

Previous
Trust Wallet Agent SDK
Next
CLI Reference
Last updated 2 months ago

