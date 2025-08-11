#!/usr/bin/env python3
"""
XClamAV - Cross-desktop GUI for ClamAV
A Linux Mint XApp for ClamAV antivirus management
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, Gio, GLib, XApp
import os
import sys
import subprocess
import threading
import time
from datetime import datetime

# Import settings module
try:
    from settings import XClamAVSettings, SettingsDialog
except ImportError:
    print("Warning: Settings module not found. Settings functionality will be limited.")
    XClamAVSettings = None
    SettingsDialog = None

class ClamAVWrapper:
    """Wrapper class for ClamAV commands"""
    
    def __init__(self):
        self.scanning = False
        self.scan_process = None
        self.scan_options = {}
        
    def set_scan_options(self, options):
        """Set scan options from settings"""
        self.scan_options = options
        
    def is_clamav_installed(self):
        """Check if ClamAV is installed"""
        try:
            subprocess.run(['clamscan', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def build_scan_command(self, path):
        """Build clamscan command with current options"""
        cmd = ['clamscan']
        
        # Apply scan options
        if self.scan_options.get('scan_archives', True):
            cmd.append('--scan-archive=yes')
        else:
            cmd.append('--scan-archive=no')
            
        if self.scan_options.get('scan_pdf', True):
            cmd.append('--scan-pdf=yes')
        else:
            cmd.append('--scan-pdf=no')
            
        if self.scan_options.get('scan_ole2', True):
            cmd.append('--scan-ole2=yes')
        else:
            cmd.append('--scan-ole2=no')
            
        if self.scan_options.get('scan_html', True):
            cmd.append('--scan-html=yes')
        else:
            cmd.append('--scan-html=no')
            
        if self.scan_options.get('scan_pe', True):
            cmd.append('--scan-pe=yes')
        else:
            cmd.append('--scan-pe=no')
            
        if self.scan_options.get('scan_elf', True):
            cmd.append('--scan-elf=yes')
        else:
            cmd.append('--scan-elf=no')
            
        if self.scan_options.get('detect_pua', False):
            cmd.append('--detect-pua=yes')
        else:
            cmd.append('--detect-pua=no')
            
        if not self.scan_options.get('scan_hidden', False):
            cmd.append('--exclude-dir=^\\.')
        
        # Add file size limit
        max_size = self.scan_options.get('max_file_size', 20)
        cmd.append(f'--max-filesize={max_size}M')
        
        # Add recursion limit
        max_recursion = self.scan_options.get('max_recursion', 15)
        cmd.append(f'--max-dir-recursion={max_recursion}')
        
        # Standard options
        cmd.extend(['--recursive', '--infected', '--bell', path])
        
        return cmd
    
    def update_database(self, callback=None):
        """Update ClamAV virus database"""
        def run_update():
            try:
                process = subprocess.Popen(['sudo', 'freshclam'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
                stdout, stderr = process.communicate()
                if callback:
                    GLib.idle_add(callback, process.returncode == 0, stdout, stderr)
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False, "", str(e))
        
        thread = threading.Thread(target=run_update)
        thread.daemon = True
        thread.start()
    
    def scan_path(self, path, callback=None, progress_callback=None):
        """Scan a specific path"""
        if self.scanning:
            return False
            
        self.scanning = True
        
        def run_scan():
            try:
                cmd = self.build_scan_command(path)
                self.scan_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                output_lines = []
                while True:
                    output = self.scan_process.stdout.readline()
                    if output == '' and self.scan_process.poll() is not None:
                        break
                    if output:
                        output_lines.append(output.strip())
                        if progress_callback:
                            GLib.idle_add(progress_callback, output.strip())
                
                stderr = self.scan_process.stderr.read()
                returncode = self.scan_process.returncode
                
                self.scanning = False
                self.scan_process = None
                
                if callback:
                    GLib.idle_add(callback, returncode == 0, '\n'.join(output_lines), stderr)
                    
            except Exception as e:
                self.scanning = False
                self.scan_process = None
                if callback:
                    GLib.idle_add(callback, False, "", str(e))
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        return True
    
    def stop_scan(self):
        """Stop current scan"""
        if self.scan_process:
            self.scan_process.terminate()
            self.scanning = False
            self.scan_process = None

class XClamAVWindow(Gtk.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, app):
        super().__init__(application=app)
        
        self.clamav = ClamAVWrapper()
        self.scan_results = []
        
        # Initialize settings
        if XClamAVSettings:
            self.settings = XClamAVSettings()
        else:
            self.settings = None
        
        self.set_title("XClamAV - Antivirus Scanner")
        self.set_default_size(800, 600)
        self.set_icon_name("security-high")
        
        # Status icon for system tray
        self.status_icon = XApp.StatusIcon()
        self.status_icon.set_icon_name("security-high")
        self.status_icon.set_tooltip_text("XClamAV - System Protected")
        self.status_icon.set_visible(True)
        
        self.setup_ui()
        self.check_clamav_status()
        self.apply_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.set_margin_left(12)
        main_box.set_margin_right(12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        
        # Header section
        header_frame = Gtk.Frame()
        header_frame.set_shadow_type(Gtk.ShadowType.IN)
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_left(16)
        header_box.set_margin_right(16)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(16)
        
        # Status section
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.status_label = Gtk.Label()
        self.status_label.set_markup("<span size='large' weight='bold'>System Status: Checking...</span>")
        self.status_label.set_halign(Gtk.Align.START)
        
        self.last_scan_label = Gtk.Label("Last scan: Never")
        self.last_scan_label.set_halign(Gtk.Align.START)
        
        status_box.pack_start(self.status_label, False, False, 0)
        status_box.pack_start(self.last_scan_label, False, False, 0)
        
        # Shield icon
        shield_icon = Gtk.Image.new_from_icon_name("security-high", Gtk.IconSize.DIALOG)
        
        header_box.pack_start(shield_icon, False, False, 0)
        header_box.pack_start(status_box, True, True, 0)
        header_frame.add(header_box)
        
        # Scan buttons section
        scan_frame = Gtk.Frame(label="Scan Options")
        scan_grid = Gtk.Grid()
        scan_grid.set_margin_left(12)
        scan_grid.set_margin_right(12)
        scan_grid.set_margin_top(12)
        scan_grid.set_margin_bottom(12)
        scan_grid.set_row_spacing(6)
        scan_grid.set_column_spacing(12)
        
        # Quick scan button
        self.quick_scan_btn = Gtk.Button.new_with_label("Quick Scan")
        self.quick_scan_btn.set_size_request(150, 50)
        self.quick_scan_btn.connect("clicked", self.on_quick_scan)
        
        # Full scan button
        self.full_scan_btn = Gtk.Button.new_with_label("Full System Scan")
        self.full_scan_btn.set_size_request(150, 50)
        self.full_scan_btn.connect("clicked", self.on_full_scan)
        
        # Custom scan button
        self.custom_scan_btn = Gtk.Button.new_with_label("Custom Scan")
        self.custom_scan_btn.set_size_request(150, 50)
        self.custom_scan_btn.connect("clicked", self.on_custom_scan)
        
        # Stop scan button
        self.stop_scan_btn = Gtk.Button.new_with_label("Stop Scan")
        self.stop_scan_btn.set_size_request(150, 50)
        self.stop_scan_btn.connect("clicked", self.on_stop_scan)
        self.stop_scan_btn.set_sensitive(False)
        
        scan_grid.attach(self.quick_scan_btn, 0, 0, 1, 1)
        scan_grid.attach(self.full_scan_btn, 1, 0, 1, 1)
        scan_grid.attach(self.custom_scan_btn, 0, 1, 1, 1)
        scan_grid.attach(self.stop_scan_btn, 1, 1, 1, 1)
        
        scan_frame.add(scan_grid)
        
        # Progress section
        progress_frame = Gtk.Frame(label="Scan Progress")
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        progress_box.set_margin_left(12)
        progress_box.set_margin_right(12)
        progress_box.set_margin_top(12)
        progress_box.set_margin_bottom(12)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Ready")
        
        # Scrolled window for scan output
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 200)
        
        self.output_textview = Gtk.TextView()
        self.output_textview.set_editable(False)
        self.output_textview.set_cursor_visible(False)
        self.output_buffer = self.output_textview.get_buffer()
        
        scrolled.add(self.output_textview)
        
        progress_box.pack_start(self.progress_bar, False, False, 0)
        progress_box.pack_start(scrolled, True, True, 0)
        progress_frame.add(progress_box)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_halign(Gtk.Align.END)
        
        self.update_btn = Gtk.Button.new_with_label("Update Database")
        self.update_btn.connect("clicked", self.on_update_database)
        
        settings_btn = Gtk.Button.new_with_label("Settings")
        settings_btn.connect("clicked", self.on_settings)
        
        about_btn = Gtk.Button.new_with_label("About")
        about_btn.connect("clicked", self.on_about)
        
        button_box.pack_start(self.update_btn, False, False, 0)
        button_box.pack_start(settings_btn, False, False, 0)
        button_box.pack_start(about_btn, False, False, 0)
        
        # Pack everything
        main_box.pack_start(header_frame, False, False, 0)
        main_box.pack_start(scan_frame, False, False, 0)
        main_box.pack_start(progress_frame, True, True, 0)
        main_box.pack_start(button_box, False, False, 0)
        
        self.add(main_box)
        
    def check_clamav_status(self):
        """Check ClamAV installation status"""
        if self.clamav.is_clamav_installed():
            self.status_label.set_markup("<span size='large' weight='bold' color='green'>System Status: Protected</span>")
            self.status_icon.set_tooltip_text("XClamAV - System Protected")
            self.enable_scan_buttons(True)
        else:
            self.status_label.set_markup("<span size='large' weight='bold' color='red'>System Status: ClamAV Not Installed</span>")
            self.status_icon.set_tooltip_text("XClamAV - ClamAV Not Installed")
            self.enable_scan_buttons(False)
            self.show_install_dialog()
    
    def enable_scan_buttons(self, enabled):
        """Enable or disable scan buttons"""
        self.quick_scan_btn.set_sensitive(enabled)
        self.full_scan_btn.set_sensitive(enabled)
        self.custom_scan_btn.set_sensitive(enabled)
        self.update_btn.set_sensitive(enabled)
    
    def show_install_dialog(self):
        """Show ClamAV installation dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="ClamAV Not Installed"
        )
        dialog.format_secondary_text(
            "ClamAV antivirus engine is not installed on your system.\n\n"
            "To install ClamAV, run:\n"
            "sudo apt install clamav clamav-daemon"
        )
        dialog.run()
        dialog.destroy()
    
    def append_output(self, text):
        """Append text to output buffer"""
        end_iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end_iter, text + "\n")
        
        # Auto-scroll to bottom
        mark = self.output_buffer.get_insert()
        self.output_textview.scroll_mark_onscreen(mark)
    
    def on_quick_scan(self, button):
        """Quick scan (home directory)"""
        home_dir = os.path.expanduser("~")
        self.start_scan("Quick Scan", home_dir)
    
    def on_full_scan(self, button):
        """Full system scan"""
        self.start_scan("Full System Scan", "/")
    
    def on_custom_scan(self, button):
        """Custom directory scan"""
        dialog = Gtk.FileChooserDialog(
            title="Choose Directory to Scan",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.start_scan("Custom Scan", path)
        
        dialog.destroy()
    
    def start_scan(self, scan_type, path):
        """Start a scan operation"""
        self.output_buffer.set_text("")
        self.append_output(f"Starting {scan_type} of: {path}")
        self.append_output(f"Scan started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.append_output("-" * 50)
        
        self.progress_bar.set_text(f"Scanning: {scan_type}")
        self.progress_bar.pulse()
        
        # Disable scan buttons, enable stop
        self.enable_scan_buttons(False)
        self.stop_scan_btn.set_sensitive(True)
        
        # Start pulse animation
        self.pulse_timer = GLib.timeout_add(100, self.pulse_progress)
        
        # Start scan
        self.clamav.scan_path(
            path,
            callback=self.on_scan_complete,
            progress_callback=self.on_scan_progress
        )
    
    def pulse_progress(self):
        """Pulse progress bar"""
        if self.clamav.scanning:
            self.progress_bar.pulse()
            return True
        return False
    
    def on_scan_progress(self, line):
        """Handle scan progress updates"""
        self.append_output(line)
    
    def on_scan_complete(self, success, output, error):
        """Handle scan completion"""
        # Stop pulse timer
        if hasattr(self, 'pulse_timer'):
            GLib.source_remove(self.pulse_timer)
        
        self.append_output("-" * 50)
        if success:
            self.append_output("Scan completed successfully!")
            self.progress_bar.set_text("Scan Complete")
            self.progress_bar.set_fraction(1.0)
        else:
            self.append_output(f"Scan failed: {error}")
            self.progress_bar.set_text("Scan Failed")
            self.progress_bar.set_fraction(0.0)
        
        self.append_output(f"Scan finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update last scan time
        self.last_scan_label.set_text(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Re-enable buttons
        self.enable_scan_buttons(True)
        self.stop_scan_btn.set_sensitive(False)
    
    def on_stop_scan(self, button):
        """Stop current scan"""
        self.clamav.stop_scan()
        self.append_output("Scan stopped by user")
        self.progress_bar.set_text("Scan Stopped")
        self.progress_bar.set_fraction(0.0)
        
        # Stop pulse timer
        if hasattr(self, 'pulse_timer'):
            GLib.source_remove(self.pulse_timer)
        
        # Re-enable buttons
        self.enable_scan_buttons(True)
        self.stop_scan_btn.set_sensitive(False)
    
    def on_update_database(self, button):
        """Update virus database"""
        self.append_output("Updating virus database...")
        self.update_btn.set_sensitive(False)
        self.clamav.update_database(callback=self.on_update_complete)
    
    def on_update_complete(self, success, output, error):
        """Handle database update completion"""
        if success:
            self.append_output("Database updated successfully!")
        else:
            self.append_output(f"Database update failed: {error}")
        
        self.update_btn.set_sensitive(True)
    
    def on_settings(self, button):
        """Open settings dialog"""
        if not SettingsDialog or not self.settings:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Settings"
            )
            dialog.format_secondary_text("Settings module not available. Please ensure settings.py is in the same directory.")
            dialog.run()
            dialog.destroy()
            return
        
        dialog = SettingsDialog(self, self.settings)
        response = dialog.run()
        if response in (Gtk.ResponseType.OK, Gtk.ResponseType.APPLY):
            dialog.save_current_settings()
            # Apply new settings to ClamAV wrapper
            self.apply_settings()
        dialog.destroy()
    
    def apply_settings(self):
        """Apply current settings to ClamAV operations"""
        if not self.settings:
            return
        
        # Apply system tray visibility
        notifications = self.settings.get("notifications")
        if notifications:
            show_tray = notifications.get("system_tray", True)
            self.status_icon.set_visible(show_tray)
        
        # Apply interface settings
        interface = self.settings.get("interface")
        if interface:
            # Handle dark mode if supported
            dark_mode = interface.get("dark_mode", "auto")
            if hasattr(self, 'dark_mode_manager'):
                if dark_mode == "dark":
                    # Force dark mode
                    pass
                elif dark_mode == "light":
                    # Force light mode
                    pass
                # "auto" uses system default
        
        # Apply scan options to ClamAV wrapper
        scan_options = self.settings.get("scan_options")
        if scan_options and hasattr(self.clamav, 'set_scan_options'):
            self.clamav.set_scan_options(scan_options)
    
    def on_about(self, button):
        """Show about dialog"""
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_program_name("XClamAV")
        about.set_version("1.0.0")
        about.set_comments("Cross-desktop GUI for ClamAV antivirus")
        about.set_copyright("© 2025 XClamAV Project")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_authors(["XClamAV Development Team"])
        about.set_website("https://github.com/xclamav/xclamav")
        about.set_logo_icon_name("security-high")
        about.run()
        about.destroy()

class XClamAVApplication(Gtk.Application):
    """Main application class"""
    
    def __init__(self):
        super().__init__(application_id="org.x-apps.xclamav",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        # Use XApp dark mode manager
        self.dark_mode_manager = XApp.DarkModeManager()
        
    def do_activate(self):
        """Application activation"""
        window = XClamAVWindow(self)
        window.show_all()
    
    def do_startup(self):
        """Application startup"""
        Gtk.Application.do_startup(self)

def main():
    """Main entry point"""
    app = XClamAVApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()