#!/bin/bash
# XClamAV Simple Installation Script

echo "🛡️ Installing XClamAV..."

# עדכון המערכת
echo "📦 Updating system packages..."
sudo apt update

# התקנת תלויות
echo "📦 Installing dependencies..."
sudo apt install -y \
    clamav \
    clamav-daemon \
    clamav-freshclam \
    python3 \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-xapp-1.0 \
    policykit-1

# הפסקת שירותים לעדכון
echo "🔄 Configuring ClamAV..."
sudo systemctl stop clamav-freshclam
sudo systemctl stop clamav-daemon

# עדכון בסיס נתונים
echo "📡 Updating virus database..."
sudo freshclam

# הפעלת שירותים
sudo systemctl start clamav-freshclam
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-freshclam
sudo systemctl enable clamav-daemon

# הפעלת XClamAV
echo "🚀 Testing XClamAV..."
python3 xclamav.py &

echo "✅ Installation completed!"
echo "You can run XClamAV with: python3 xclamav.py"
