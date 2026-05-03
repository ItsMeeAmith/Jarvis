#!/usr/bin/env bash
# setup_server.sh — First-time JARVIS server setup for DigitalOcean Ubuntu 22.04+
set -euo pipefail

echo "============================================================"
echo "  JARVIS Server Setup"
echo "============================================================"

# 1. Update system packages
echo "[1/6] Updating system packages..."
apt-get update -y && apt-get upgrade -y

# 2. Install Docker (official repository)
echo "[2/6] Installing Docker..."
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

# 3. Install git
echo "[3/6] Installing git..."
apt-get install -y git

# 4. Create ~/jarvis directory
echo "[4/6] Creating ~/jarvis directory..."
mkdir -p ~/jarvis

# 5. Copy .env.example to .env (if not already present)
echo "[5/6] Preparing .env file..."
if [ ! -f ~/jarvis/.env ]; then
  cp ~/jarvis/.env.example ~/jarvis/.env 2>/dev/null || \
    echo "Note: .env.example not found yet — run this after git clone."
else
  echo "  .env already exists, skipping copy."
fi

# 6. Print next steps
echo ""
echo "============================================================"
echo "  Setup complete! Next steps:"
echo "============================================================"
echo ""
echo "  1. Clone your repository (if not already done):"
echo "       cd ~ && git clone https://github.com/YOUR_USER/Jarvis.git jarvis"
echo ""
echo "  2. Add your Groq API key:"
echo "       nano ~/jarvis/.env"
echo "     → Set GROQ_API_KEY=<your key from https://console.groq.com>"
echo "     → Set DB_PASSWORD to a strong password"
echo "     → Set DATABASE_URL with the same password"
echo "     → Set NEXT_PUBLIC_API_URL=http://<your-droplet-ip>"
echo ""
echo "  3. Launch JARVIS with one command:"
echo "       cd ~/jarvis && docker compose up -d --build"
echo ""
echo "  4. JARVIS will be available at:"
echo "       http://<your-droplet-ip>"
echo ""
echo "============================================================"
