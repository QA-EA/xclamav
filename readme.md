# XClamAV

<div align="center">

![XClamAV Logo](screenshots/logo.png)

**🛡️ Modern Cross-Desktop GUI for ClamAV Antivirus 🛡️**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Linux-brightgreen.svg)](https://www.linux.org/)
[![Desktop](https://img.shields.io/badge/Desktop-XApp-orange.svg)](https://github.com/linuxmint/xapp)
[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)
[![ClamAV](https://img.shields.io/badge/ClamAV-Compatible-red.svg)](https://www.clamav.net/)

*Finally, a user-friendly antivirus interface for Linux!*

[Screenshots](#screenshots) • [Installation](#installation) • [Features](#features) • [Contributing](#contributing)

</div>

---

## 🌟 About

**XClamAV** is a modern, intuitive graphical interface for the ClamAV antivirus engine, built specifically as a Linux Mint **XApp**. It provides a consistent, beautiful experience across all major Linux desktop environments.

### 🎯 Why XClamAV?

- **🔥 ClamTk is discontinued** (April 2024) - XClamAV is the modern replacement
- **🎨 Beautiful, modern interface** that feels native on every desktop
- **⚡ Lightning fast** with real-time scanning capabilities  
- **🌍 Multi-language support** - English, Hebrew, Spanish, French, German
- **🛠️ Built by a computer technician** who understands what users actually need

---

## 📸 Screenshots

### Main Interface
![Main Window](screenshots/main-window.png)
*Clean, intuitive main interface*

### Advanced Settings
![Settings Dialog](screenshots/settings.png)
*Comprehensive settings with 8 categories*

### Real-time Scanning
![Scanning Progress](screenshots/scanning.png)
*Live progress monitoring with detailed output*

---

## ✨ Features

### 🛡️ **Core Protection**
- **Quick Scan** - Scan home directory in seconds
- **Full System Scan** - Comprehensive malware detection
- **Custom Scan** - Choose any directory or file
- **Real-time Protection** - Monitor file system changes
- **Auto-Quarantine** - Safely isolate threats

### 🎨 **Modern Interface**
- **Cross-Desktop Compatible** - Works on Cinnamon, MATE, XFCE, GNOME
- **Dark Mode Support** - Automatic theme switching
- **System Tray Integration** - Minimize to tray with status notifications
- **Progress Monitoring** - Real-time scan progress with detailed logs

### ⚙️ **Advanced Features**
- **Automatic Updates** - Keep virus definitions current
- **Scheduled Scans** - Set up recurring scans
- **Exclusion Lists** - Skip files/folders you trust
- **Performance Tuning** - Multi-threaded scanning
- **Quarantine Management** - Review and restore quarantined files

### 🌍 **Internationalization**
- English, Hebrew (עברית), Spanish (Español)
- French (Français), German (Deutsch)
- RTL support for Hebrew and Arabic

---

## 🚀 Installation

### 📋 Prerequisites

- **OS:** Ubuntu 18.04+, Linux Mint 19+, or Debian 10+
- **Desktop:** Any GTK-based environment
- **Python:** 3.6+

### 🛠️ Quick Install

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y clamav clamav-daemon python3-gi gir1.2-gtk-3.0 gir1.2-xapp-1.0 meson git

# 2. Clone repository
git clone https://github.com/YOUR-USERNAME/xclamav.git
cd xclamav

# 3. Install XClamAV
chmod +x setup.sh
./setup.sh create
./setup.sh install

# 4. Update virus database
sudo freshclam

# 5. Launch XClamAV
xclamav.py
```

### 📦 Alternative: Download .deb Package

1. Go to [Releases](https://github.com/YOUR-USERNAME/xclamav/releases)
2. Download `xclamav_1.0.0_all.deb`
3. Install: `sudo dpkg -i xclamav_1.0.0_all.deb`

---

## 🎯 Usage

### Basic Operations

1. **Launch XClamAV** from Applications menu (Security category)
2. **Quick Scan** - Click to scan your home directory
3. **Settings** - Configure advanced options
4. **Update Database** - Keep protection current

### Advanced Usage

- **Real-time Protection:** Enable in Settings → Real-time
- **Scheduled Scans:** Set up in Settings → Updates  
- **Quarantine Management:** Review threats in quarantine folder
- **Custom Exclusions:** Add trusted files/folders to skip

---

## 🛠️ Development

### Project Structure

```
xclamav/
├── src/
│   ├── xclamav.py          # Main application
│   └── settings.py         # Settings management
├── data/
│   ├── xclamav.desktop     # Desktop entry
│   ├── xclamav.svg         # Application icon
│   └── *.policy            # PolicyKit rules
├── po/                     # Translations
├── debian/                 # Packaging
├── screenshots/            # Screenshots for README
└── docs/                   # Documentation
```

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/YOUR-USERNAME/xclamav.git
cd xclamav
./setup.sh dev-setup

# Test in development mode
./setup.sh test
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 **Bug Reports**
Found a bug? [Open an issue](https://github.com/YOUR-USERNAME/xclamav/issues/new)

### 💡 **Feature Requests**  
Have an idea? [Start a discussion](https://github.com/YOUR-USERNAME/xclamav/discussions)

### 🌍 **Translations**
Help translate XClamAV to your language!

### 💻 **Code Contributions**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### 📝 **Areas We Need Help With:**
- [ ] Testing on different distributions
- [ ] UI/UX improvements
- [ ] Documentation
- [ ] Translations
- [ ] Performance optimizations

---

## 🗺️ Roadmap

### 📅 **Version 1.1** (Next Release)
- [ ] Scheduled scan management
- [ ] Email scanning integration  
- [ ] Enhanced threat detection
- [ ] Better error handling
- [ ] Performance improvements

### 📅 **Version 1.2** (Future)
- [ ] Cloud scanning integration
- [ ] Network drive scanning
- [ ] Advanced reporting
- [ ] Plugin system

### 📅 **Version 2.0** (Long-term)
- [ ] GTK 4 migration
- [ ] Container scanning
- [ ] Machine learning integration
- [ ] Enterprise management console

---

## 📊 Compatibility

### Desktop Environments

| Environment | Status | Notes |
|-------------|--------|-------|
| Cinnamon | ✅ Perfect | Native XApp support |
| MATE | ✅ Perfect | Native XApp support |  
| XFCE | ✅ Perfect | Native XApp support |
| GNOME | ✅ Excellent | Minor theming differences |
| KDE | ⚠️ Good | GTK theming may vary |

### Linux Distributions

| Distribution | Tested | Status | Package Format |
|--------------|--------|--------|----------------|
| Linux Mint 21+ | ✅ | Perfect | .deb |
| Ubuntu 20.04+ | ✅ | Excellent | .deb |
| Debian 11+ | ✅ | Good | .deb |
| Fedora 35+ | ⚠️ | Partial | Manual install |
| openSUSE 15+ | ⚠️ | Partial | Manual install |

---

## 🆘 Support

### 📖 **Documentation**
- [Installation Guide](docs/installation.md)
- [User Manual](docs/user-guide.md)
- [Troubleshooting](docs/troubleshooting.md)

### 💬 **Community**
- [GitHub Discussions](https://github.com/YOUR-USERNAME/xclamav/discussions) - Ask questions
- [Issues](https://github.com/YOUR-USERNAME/xclamav/issues) - Report bugs

### 🚨 **Common Issues**
- **ClamAV not found:** `sudo apt install clamav clamav-daemon`
- **Permission errors:** Check [troubleshooting guide](docs/troubleshooting.md)
- **GUI not starting:** Verify GTK dependencies

---

## 📄 License

XClamAV is free software licensed under the **GNU General Public License v3.0**.

This means you can:
- ✅ Use it for any purpose
- ✅ Study and modify the source code  
- ✅ Distribute copies
- ✅ Distribute modified versions

See [LICENSE](LICENSE) for full details.

---

## 🙏 Credits

### 👨‍💻 **Development Team**
- **Lead Developer:** [Your Name] - Computer Technician & Linux Enthusiast
- **Contributors:** [See contributors](https://github.com/YOUR-USERNAME/xclamav/contributors)

### 🎯 **Inspiration & Thanks**
- **ClamAV Team** - For the excellent antivirus engine
- **Linux Mint Team** - For XApp framework and inspiration  
- **ClamTk Team** - For years of service to the Linux community
- **Linux Community** - For feedback and support

### 🔧 **Built With**
- [ClamAV](https://www.clamav.net/) - Antivirus engine
- [GTK 3](https://www.gtk.org/) - GUI toolkit
- [XApp](https://github.com/linuxmint/xapp) - Cross-desktop libraries
- [Python](https://www.python.org/) - Programming language

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR-USERNAME/xclamav&type=Date)](https://star-history.com/#YOUR-USERNAME/xclamav&Date)

---

<div align="center">

**Made with ❤️ for the Linux community**

**Help keep Linux secure - Star ⭐ this repository!**

[⬆ Back to Top](#xclamav)

</div>