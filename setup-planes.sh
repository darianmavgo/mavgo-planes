#!/usr/bin/env bash
# setup-planes.sh
# Automates the creation of a GitHub repo, Cloudflare Pages site, and Cloudflare Worker proxy.

set -e # Exit immediately if any command fails

echo "✈️  Starting GetaPlane Deployment Setup..."

# 1. Dependency Checks
for cmd in git gh wrangler; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "❌ Error: $cmd is required but not installed." >&2
    exit 1
  fi
done
echo "✅ All required CLI tools (git, gh, wrangler) are installed."

# Check if logged in to gh
if ! gh auth status >/dev/null 2>&1; then
  echo "❌ Error: You are not logged into GitHub CLI. Run 'gh auth login' first." >&2
  exit 1
fi
echo "✅ Authenticaton checks passed."

# 2. Prepare the Worker Proxy Files
echo "⚙️  Setting up Cloudflare Worker proxy files..."
mkdir -p proxy-worker

cat << 'EOF' > proxy-worker/wrangler.toml
name = "mavgo-planes-proxy"
main = "index.js"
compatibility_date = "2024-03-24"

[[routes]]
pattern = "mavgo.com/planes*"
zone_name = "mavgo.com"
EOF

cat << 'EOF' > proxy-worker/index.js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/planes')) {
      const targetUrl = new URL(request.url);
      targetUrl.hostname = 'mavgo-planes.pages.dev';
      
      if (url.pathname === '/planes' || url.pathname === '/planes/') {
        targetUrl.pathname = '/';
      } else {
        targetUrl.pathname = url.pathname.replace(/^\/planes/, '');
      }
      return fetch(targetUrl, request);
    }
    return fetch(request);
  }
};
EOF
echo "✅ Worker configuration created in proxy-worker/"

# 3. Ignore Worker code in Cloudflare Pages static upload
echo "proxy-worker/" > .cfignore
echo ".git/" >> .cfignore
echo ".gitignore" >> .cfignore
echo "setup-planes.sh" >> .cfignore

# 4. Deploy to Cloudflare Pages (Direct Upload)
echo "🚀 Deploying static HTML/CSS to Cloudflare Pages..."
# Attempt to create the project. We use || true so it doesn't fail if the project already exists.
wrangler pages project create mavgo-planes --production-branch main 2>/dev/null || true

# Deploy the root directory (using .cfignore to exclude the proxy-worker folder)
if ! wrangler pages deploy . --project-name=mavgo-planes --branch=main; then
  echo "❌ Pages Deployment failed." >&2
  exit 1
fi
echo "✅ Cloudflare Pages deployed successfully."

# 5. Deploy Cloudflare Worker Proxy
echo "🚀 Deploying 'mavgo.com/planes' route interceptor Worker..."
cd proxy-worker
if ! wrangler deploy; then
  echo "❌ Worker Deployment failed." >&2
  exit 1
fi
cd ..
echo "✅ Cloudflare Worker deployed successfully to mavgo.com zone."

# 6. GitHub Repository Setup & Push
echo "🐙 Synchronizing with GitHub..."
# Initialize git if not already done
[ ! -d ".git" ] && git init

cat << 'EOF' > .gitignore
proxy-worker/node_modules/
.wrangler/
EOF

git add .
# Commit changes if there are any
if ! git diff --cached --quiet; then
  git commit -m "Automated deployment setup"
else
  echo "ℹ️  No new code changes to commit."
fi

# Check if repository already exists on GitHub
if ! gh repo view "mavgo-planes" >/dev/null 2>&1; then
  echo "Creating new GitHub repository 'mavgo-planes'..."
  gh repo create mavgo-planes --public --source=. --remote=origin --push
else
  echo "GitHub repository exists. Pushing latest changes..."
  git push origin main || git push origin master
fi
echo "✅ GitHub sync complete."

echo "🎉 Setup complete! Your planes page is securely live at https://mavgo.com/planes"
