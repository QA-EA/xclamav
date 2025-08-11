#!/bin/bash
# XClamAV Installation Script

# Project structure creation script
create_project_structure() {
    echo "Creating XClamAV project structure..."
    
    # Create directories
    mkdir -p xclamav/{src,data,debian,po}
    mkdir -p xclamav/src/{gui,core}
    
    # Create meson.build (main)
    cat > xclamav/meson.build << 'EOF'
project('xclamav', 'c',
    version: '1.0.0',
    meson_version: '>= 0.50.0'
)

# Dependencies
gtk3_dep = dependency('gtk+-3.0', version: '>= 3.20')
xapp_dep = dependency('xapp', version: '>= 1.0')
python3_dep = dependency('python3', version: '>= 3.6')

# Install main application
install_data('src/xclamav.py',
    install_dir: get_option('bindir'),
    install_mode: 'rwxr-xr-x'
)

# Install desktop file
install_data('data/xclamav.desktop',
    install_dir: join_paths(get_option('datadir'), 'applications')
)

# Install icon
install_data('data/xclamav.svg',
    install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
)

# Install policy file for pkexec
install_data('data/org.x-apps.xclamav.policy',
    install_dir: join_paths(get_option('datadir'), 'polkit-1', 'actions')
)

subdir('po')
EOF

    # Create desktop file
    cat > xclamav/data/xclamav.desktop << 'EOF'
[Desktop Entry]
Name=XClamAV
Comment=Cross-desktop GUI for ClamAV antivirus
Comment[he]=ממשק גרפי חוצה-פלטפורמות עבור ClamAV
Exec=xclamav.py
Icon=xclamav
Terminal=false
Type=Application
Categories=System;Security;
Keywords=antivirus;security;scan;malware;virus;
StartupNotify=true
EOF

    # Create polkit policy file
    cat > xclamav/data/org.x-apps.xclamav.policy << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
"http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
    <action id="org.x-apps.xclamav.update-database">
        <description>Update ClamAV virus database</description>
        <description xml:lang="he">עדכון בסיס נתוני הוירוסים של ClamAV</description>
        <message>Authentication is required to update the virus database</message>
        <message xml:lang="he">נדרש אימות כדי לעדכן את בסיס נתוני הוירוסים</message>
        <defaults>
            <allow_any>auth_admin</allow_any>
            <allow_inactive>auth_admin</allow_inactive>
            <allow_active>auth_admin_keep</allow_active>
        </defaults>
    </action>
    
    <action id="org.x-apps.xclamav.scan-system">
        <description>Scan system files with ClamAV</description>
        <description xml:lang="he">סריקת קבצי מערכת עם ClamAV</description>
        <message>Authentication is required to scan system files</message>
        <message xml:lang="he">נדרש אימות כדי לסרוק קבצי מערכת</message>
        <defaults>
            <allow_any>auth_admin</allow_any>
            <allow_inactive>auth_admin</allow_inactive>
            <allow_active>auth_admin_keep</allow_active>
        </defaults>
    </action>
</policyconfig>
EOF

    # Create basic SVG icon
    cat > xclamav/data/xclamav.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <!-- Shield background -->
    <path d="M32 4 L12 12 L12 32 Q12 52 32 60 Q52 52 52 32 L52 12 Z" 
          fill="#4a90e2" stroke="#2c5aa0" stroke-width="2"/>
    
    <!-- Checkmark -->
    <path d="M20 32 L28 40 L44 24" 
          fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    
    <!-- X for virus -->
    <g opacity="0.3">
        <circle cx="32" cy="32" r="16" fill="none" stroke="red" stroke-width="2" stroke-dasharray="4,4"/>
        <path d="M24 24 L40 40 M40 24 L24 40" stroke="red" stroke-width="3" stroke-linecap="round"/>
    </g>
</svg>
EOF

    # Create debian packaging directory structure
    mkdir -p xclamav/debian

    # Create debian/control file
    cat > xclamav/debian/control << 'EOF'
Source: xclamav
Section: utils
Priority: optional
Maintainer: XClamAV Team <team@xclamav.org>
Build-Depends: debhelper (>= 10),
               meson (>= 0.50.0),
               python3-dev,
               libgtk-3-dev,
               libxapp-dev,
               gir1.2-xapp-1.0
Standards-Version: 4.1.3
Homepage: https://github.com/xclamav/xclamav

Package: xclamav
Architecture: all
Depends: ${misc:Depends},
         python3,
         python3-gi,
         gir1.2-gtk-3.0,
         gir1.2-xapp-1.0,
         clamav,
         clamav-daemon,
         policykit-1
Recommends: clamav-freshclam
Description: Cross-desktop GUI for ClamAV antivirus
 XClamAV provides a modern, user-friendly graphical interface for the
 ClamAV antivirus engine. It is designed as an XApp to work consistently
 across different desktop environments including Cinnamon, MATE, XFCE,
 and GNOME.
 .
 Features include:
  - Quick, full, and custom scans
  - Real-time scan progress monitoring
  - Virus database updates
  - System tray integration
  - Dark mode support
EOF

    # Create debian/rules file
    cat > xclamav/debian/rules << 'EOF'
#!/usr/bin/make -f

%:
	dh $@ --buildsystem=meson

override_dh_auto_configure:
	dh_auto_configure -- \
		-Dprefix=/usr

override_dh_auto_install:
	dh_auto_install
	# Make the main script executable
	chmod +x debian/xclamav/usr/bin/xclamav.py
EOF

    # Create debian/compat
    echo "10" > xclamav/debian/compat

    # Create debian/copyright
    cat > xclamav/debian/copyright << 'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: xclamav
Upstream-Contact: XClamAV Team <team@xclamav.org>
Source: https://github.com/xclamav/xclamav

Files: *
Copyright: 2025 XClamAV Development Team
License: GPL-3+

License: GPL-3+
 This package is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
EOF

    # Create po/meson.build for translations
    cat > xclamav/po/meson.build << 'EOF'
i18n = import('i18n')

i18n.gettext('xclamav',
    languages: ['he', 'es', 'fr', 'de'],
    preset: 'glib'
)
EOF

    # Create basic Hebrew translation template
    cat > xclamav/po/he.po << 'EOF'
# Hebrew translation for XClamAV
# Copyright (C) 2025 XClamAV Team
msgid ""
msgstr ""
"Project-Id-Version: xclamav 1.0.0\n"
"Report-Msgid-Bugs-To: team@xclamav.org\n"
"Language: he\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "Quick Scan"
msgstr "סריקה מהירה"

msgid "Full System Scan"
msgstr "סריקת מערכת מלאה"

msgid "Custom Scan"
msgstr "סריקה מותאמת אישית"

msgid "Stop Scan"
msgstr "עצירת סריקה"

msgid "Update Database"
msgstr "עדכון בסיס נתונים"

msgid "Settings"
msgstr "הגדרות"

msgid "About"
msgstr "אודות"

msgid "System Status: Protected"
msgstr "סטטוס מערכת: מוגן"

msgid "System Status: ClamAV Not Installed"
msgstr "סטטוס מערכת: ClamAV לא מותקן"

msgid "Last scan"
msgstr "סריקה אחרונה"

msgid "Never"
msgstr "אף פעם"

msgid "Scan Options"
msgstr "אפשרויות סריקה"

msgid "Scan Progress"
msgstr "התקדמות סריקה"

msgid "Ready"
msgstr "מוכן"

msgid "Scanning"
msgstr "סורק"

msgid "Completed"
msgstr "הושלם"

msgid "Failed"
msgstr "נכשל"

msgid "Stopped"
msgstr "נעצר"
EOF

    echo "Project structure created successfully!"
}

# Installation script
install_xclamav() {
    echo "Installing XClamAV..."
    
    # Check if running on Ubuntu/Mint
    if ! command -v apt &> /dev/null; then
        echo "Error: This installer is designed for Ubuntu/Linux Mint systems"
        exit 1
    fi
    
    # Check for required dependencies
    echo "Checking dependencies..."
    
    # Install ClamAV if not present
    if ! command -v clamscan &> /dev/null; then
        echo "Installing ClamAV..."
        sudo apt update
        sudo apt install -y clamav clamav-daemon clamav-freshclam
    fi
    
    # Install development dependencies
    echo "Installing development dependencies..."
    sudo apt install -y \
        python3 \
        python3-gi \
        gir1.2-gtk-3.0 \
        gir1.2-xapp-1.0 \
        meson \
        build-essential \
        libgtk-3-dev \
        libxapp-dev \
        policykit-1
    
    # Build and install XClamAV
    if [ -d "xclamav" ]; then
        cd xclamav
        
        # Setup build directory
        meson setup builddir
        
        # Compile
        meson compile -C builddir
        
        # Install
        sudo meson install -C builddir
        
        echo "XClamAV installed successfully!"
        echo "You can find it in your applications menu under 'Security' or run 'xclamav.py' from terminal"
        
        # Update virus database
        echo "Updating virus database..."
        sudo freshclam
        
    else
        echo "Error: xclamav directory not found. Please run create_project_structure first."
        exit 1
    fi
}

# Development setup
setup_development() {
    echo "Setting up development environment..."
    
    # Install additional development tools
    sudo apt install -y \
        git \
        python3-pip \
        python3-venv \
        glade \
        devhelp \
        gtk-3-examples
    
    # Create virtual environment for development
    python3 -m venv xclamav-dev
    source xclamav-dev/bin/activate
    
    # Install Python development dependencies
    pip install \
        pygobject \
        pycairo
    
    echo "Development environment setup complete!"
    echo "To activate: source xclamav-dev/bin/activate"
}

# Create .deb package
create_deb_package() {
    echo "Creating .deb package..."
    
    if [ ! -d "xclamav" ]; then
        echo "Error: xclamav directory not found"
        exit 1
    fi
    
    cd xclamav
    
    # Install packaging dependencies
    sudo apt install -y devscripts debhelper
    
    # Build package
    debuild -us -uc -b
    
    echo "Package created! Check the parent directory for .deb files"
}

# Uninstall XClamAV
uninstall_xclamav() {
    echo "Uninstalling XClamAV..."
    
    # Remove installed files
    sudo rm -f /usr/bin/xclamav.py
    sudo rm -f /usr/share/applications/xclamav.desktop
    sudo rm -f /usr/share/icons/hicolor/scalable/apps/xclamav.svg
    sudo rm -f /usr/share/polkit-1/actions/org.x-apps.xclamav.policy
    
    # Update icon cache
    sudo gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
    
    echo "XClamAV uninstalled successfully!"
}

# Development testing
test_xclamav() {
    echo "Testing XClamAV..."
    
    if [ ! -f "xclamav/src/xclamav.py" ]; then
        echo "Error: xclamav.py not found"
        exit 1
    fi
    
    # Make executable
    chmod +x xclamav/src/xclamav.py
    
    # Run in development mode
    cd xclamav/src
    python3 xclamav.py
}

# Print usage information
print_usage() {
    cat << EOF
XClamAV Setup Script
===================

Usage: $0 [COMMAND]

Commands:
    create      Create project structure
    install     Install XClamAV system-wide
    dev-setup   Setup development environment
    test        Test XClamAV in development mode
    package     Create .deb package
    uninstall   Remove XClamAV from system
    help        Show this help message

Examples:
    $0 create              # Create project structure
    $0 install             # Install XClamAV
    $0 test               # Test in development mode

Prerequisites:
    - Ubuntu 18.04+ or Linux Mint 19+
    - ClamAV installed (will be installed automatically)
    - XApp libraries (for Linux Mint compatibility)

For more information, visit: https://github.com/xclamav/xclamav
EOF
}

# Main script logic
case "${1:-help}" in
    "create")
        create_project_structure
        ;;
    "install")
        install_xclamav
        ;;
    "dev-setup")
        setup_development
        ;;
    "test")
        test_xclamav
        ;;
    "package")
        create_deb_package
        ;;
    "uninstall")
        uninstall_xclamav
        ;;
    "help"|*)
        print_usage
        ;;
esac