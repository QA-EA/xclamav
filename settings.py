#!/usr/bin/env python3
"""
XClamAV Settings Module
Advanced configuration and settings management
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, Gio, GLib, XApp
import json
import os
import configparser
from pathlib import Path
from datetime import datetime, timedelta

class XClamAVSettings:
    """Settings management class"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "xclamav"
        self.config_file = self.config_dir / "settings.json"
        self.ensure_config_dir()
        self.load_settings()
    
    def ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self):
        """Load settings from file"""
        self.default_settings = {
            "scan_options": {
                "scan_archives": True,
                "scan_pdf": True,
                "scan_ole2": True,
                "scan_html": True,
                "scan_pe": True,
                "scan_elf": True,
                "detect_pua": False,
                "scan_hidden": False,
                "max_file_size": 20,  # MB
                "max_recursion": 15
            },
            "real_time": {
                "enabled": False,
                "watch_downloads": True,
                "watch_home": False,
                "watch_removable": True,
                "prevention_mode": False
            },
            "updates": {
                "auto_update": True,
                "update_frequency": "daily",  # daily, weekly, manual
                "check_on_startup": True
            },
            "notifications": {
                "show_scan_complete": True,
                "show_threats_found": True,
                "show_update_complete": False,
                "system_tray": True
            },
            "quarantine": {
                "auto_quarantine": True,
                "quarantine_path": str(Path.home() / ".local" / "share" / "xclamav" / "quarantine"),
                "retention_days": 30
            },
            "interface": {
                "start_minimized": False,
                "close_to_tray": True,
                "dark_mode": "auto",  # auto, light, dark
                "language": "auto"
            },
            "exclusions": {
                "paths": [],
                "extensions": [".tmp", ".log"],
                "processes": []
            },
            "advanced": {
                "scan_threads": 4,
                "memory_limit": 512,  # MB
                "database_mirror": "auto",
                "log_level": "info"  # debug, info, warning, error
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    self.settings = self._merge_settings(self.default_settings, loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.default_settings.copy()
        else:
            self.settings = self.default_settings.copy()
    
    def _merge_settings(self, default, loaded):
        """Recursively merge loaded settings with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, category, key=None):
        """Get setting value"""
        if key is None:
            return self.settings.get(category, {})
        return self.settings.get(category, {}).get(key)
    
    def set(self, category, key, value):
        """Set setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()

class SettingsDialog(Gtk.Dialog):
    """Settings dialog window"""
    
    def __init__(self, parent, settings):
        super().__init__(title="XClamAV Settings", transient_for=parent, modal=True)
        
        self.settings = settings
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        
        self.set_default_size(600, 500)
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the settings UI"""
        content_area = self.get_content_area()
        content_area.set_margin_left(12)
        content_area.set_margin_right(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        
        # Create notebook for different setting categories
        self.notebook = Gtk.Notebook()
        content_area.pack_start(self.notebook, True, True, 0)
        
        # Scan Options Tab
        self.create_scan_options_tab()
        
        # Real-time Protection Tab
        self.create_realtime_tab()
        
        # Updates Tab
        self.create_updates_tab()
        
        # Notifications Tab
        self.create_notifications_tab()
        
        # Quarantine Tab
        self.create_quarantine_tab()
        
        # Interface Tab
        self.create_interface_tab()
        
        # Exclusions Tab
        self.create_exclusions_tab()
        
        # Advanced Tab
        self.create_advanced_tab()
    
    def create_scan_options_tab(self):
        """Create scan options tab"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # File types frame
        file_types_frame = Gtk.Frame(label="File Types to Scan")
        file_types_grid = Gtk.Grid()
        file_types_grid.set_margin_left(12)
        file_types_grid.set_margin_right(12)
        file_types_grid.set_margin_top(12)
        file_types_grid.set_margin_bottom(12)
        file_types_grid.set_row_spacing(6)
        file_types_grid.set_column_spacing(12)
        
        self.scan_archives_check = Gtk.CheckButton.new_with_label("Scan archive files (ZIP, RAR, etc.)")
        self.scan_pdf_check = Gtk.CheckButton.new_with_label("Scan PDF documents")
        self.scan_ole2_check = Gtk.CheckButton.new_with_label("Scan Office documents")
        self.scan_html_check = Gtk.CheckButton.new_with_label("Scan HTML files")
        self.scan_pe_check = Gtk.CheckButton.new_with_label("Scan Windows executables")
        self.scan_elf_check = Gtk.CheckButton.new_with_label("Scan Linux executables")
        
        file_types_grid.attach(self.scan_archives_check, 0, 0, 2, 1)
        file_types_grid.attach(self.scan_pdf_check, 0, 1, 2, 1)
        file_types_grid.attach(self.scan_ole2_check, 0, 2, 2, 1)
        file_types_grid.attach(self.scan_html_check, 0, 3, 2, 1)
        file_types_grid.attach(self.scan_pe_check, 0, 4, 2, 1)
        file_types_grid.attach(self.scan_elf_check, 0, 5, 2, 1)
        
        file_types_frame.add(file_types_grid)
        
        # Detection options frame
        detection_frame = Gtk.Frame(label="Detection Options")
        detection_grid = Gtk.Grid()
        detection_grid.set_margin_left(12)
        detection_grid.set_margin_right(12)
        detection_grid.set_margin_top(12)
        detection_grid.set_margin_bottom(12)
        detection_grid.set_row_spacing(6)
        detection_grid.set_column_spacing(12)
        
        self.detect_pua_check = Gtk.CheckButton.new_with_label("Detect potentially unwanted applications (PUA)")
        self.scan_hidden_check = Gtk.CheckButton.new_with_label("Scan hidden files and directories")
        
        detection_grid.attach(self.detect_pua_check, 0, 0, 2, 1)
        detection_grid.attach(self.scan_hidden_check, 0, 1, 2, 1)
        
        detection_frame.add(detection_grid)
        
        # Limits frame
        limits_frame = Gtk.Frame(label="Scan Limits")
        limits_grid = Gtk.Grid()
        limits_grid.set_margin_left(12)
        limits_grid.set_margin_right(12)
        limits_grid.set_margin_top(12)
        limits_grid.set_margin_bottom(12)
        limits_grid.set_row_spacing(6)
        limits_grid.set_column_spacing(12)
        
        max_file_label = Gtk.Label("Maximum file size to scan (MB):")
        max_file_label.set_halign(Gtk.Align.START)
        self.max_file_spin = Gtk.SpinButton.new_with_range(1, 1000, 1)
        
        max_recursion_label = Gtk.Label("Maximum directory recursion depth:")
        max_recursion_label.set_halign(Gtk.Align.START)
        self.max_recursion_spin = Gtk.SpinButton.new_with_range(1, 50, 1)
        
        limits_grid.attach(max_file_label, 0, 0, 1, 1)
        limits_grid.attach(self.max_file_spin, 1, 0, 1, 1)
        limits_grid.attach(max_recursion_label, 0, 1, 1, 1)
        limits_grid.attach(self.max_recursion_spin, 1, 1, 1, 1)
        
        limits_frame.add(limits_grid)
        
        box.pack_start(file_types_frame, False, False, 0)
        box.pack_start(detection_frame, False, False, 0)
        box.pack_start(limits_frame, False, False, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label("Scan Options"))
    
    def create_realtime_tab(self):
        """Create real-time protection tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Real-time protection frame
        realtime_frame = Gtk.Frame(label="Real-time Protection")
        realtime_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        realtime_box.set_margin_left(12)
        realtime_box.set_margin_right(12)
        realtime_box.set_margin_top(12)
        realtime_box.set_margin_bottom(12)
        
        self.realtime_enabled_check = Gtk.CheckButton.new_with_label("Enable real-time protection")
        
        # Warning label
        warning_label = Gtk.Label()
        warning_label.set_markup('<span color="red"><b>Warning:</b> Real-time protection requires root privileges and may impact system performance.</span>')
        warning_label.set_line_wrap(True)
        warning_label.set_halign(Gtk.Align.START)
        
        realtime_box.pack_start(self.realtime_enabled_check, False, False, 0)
        realtime_box.pack_start(warning_label, False, False, 0)
        realtime_frame.add(realtime_box)
        
        # Watch directories frame
        watch_frame = Gtk.Frame(label="Directories to Monitor")
        watch_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        watch_box.set_margin_left(12)
        watch_box.set_margin_right(12)
        watch_box.set_margin_top(12)
        watch_box.set_margin_bottom(12)
        
        self.watch_downloads_check = Gtk.CheckButton.new_with_label("Monitor Downloads folder")
        self.watch_home_check = Gtk.CheckButton.new_with_label("Monitor entire Home directory")
        self.watch_removable_check = Gtk.CheckButton.new_with_label("Monitor removable devices")
        self.prevention_mode_check = Gtk.CheckButton.new_with_label("Prevention mode (block infected files)")
        
        watch_box.pack_start(self.watch_downloads_check, False, False, 0)
        watch_box.pack_start(self.watch_home_check, False, False, 0)
        watch_box.pack_start(self.watch_removable_check, False, False, 0)
        watch_box.pack_start(self.prevention_mode_check, False, False, 0)
        
        watch_frame.add(watch_box)
        
        box.pack_start(realtime_frame, False, False, 0)
        box.pack_start(watch_frame, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Real-time"))
    
    def create_updates_tab(self):
        """Create updates tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Auto-update frame
        update_frame = Gtk.Frame(label="Automatic Updates")
        update_grid = Gtk.Grid()
        update_grid.set_margin_left(12)
        update_grid.set_margin_right(12)
        update_grid.set_margin_top(12)
        update_grid.set_margin_bottom(12)
        update_grid.set_row_spacing(6)
        update_grid.set_column_spacing(12)
        
        self.auto_update_check = Gtk.CheckButton.new_with_label("Enable automatic database updates")
        
        frequency_label = Gtk.Label("Update frequency:")
        frequency_label.set_halign(Gtk.Align.START)
        
        self.frequency_combo = Gtk.ComboBoxText()
        self.frequency_combo.append_text("Daily")
        self.frequency_combo.append_text("Weekly")
        self.frequency_combo.append_text("Manual only")
        
        self.check_startup_check = Gtk.CheckButton.new_with_label("Check for updates on startup")
        
        update_grid.attach(self.auto_update_check, 0, 0, 2, 1)
        update_grid.attach(frequency_label, 0, 1, 1, 1)
        update_grid.attach(self.frequency_combo, 1, 1, 1, 1)
        update_grid.attach(self.check_startup_check, 0, 2, 2, 1)
        
        update_frame.add(update_grid)
        box.pack_start(update_frame, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Updates"))
    
    def create_notifications_tab(self):
        """Create notifications tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Notifications frame
        notif_frame = Gtk.Frame(label="Notification Settings")
        notif_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        notif_box.set_margin_left(12)
        notif_box.set_margin_right(12)
        notif_box.set_margin_top(12)
        notif_box.set_margin_bottom(12)
        
        self.show_scan_complete_check = Gtk.CheckButton.new_with_label("Show notification when scan completes")
        self.show_threats_found_check = Gtk.CheckButton.new_with_label("Show notification when threats are found")
        self.show_update_complete_check = Gtk.CheckButton.new_with_label("Show notification when database updates")
        self.system_tray_check = Gtk.CheckButton.new_with_label("Show icon in system tray")
        
        notif_box.pack_start(self.show_scan_complete_check, False, False, 0)
        notif_box.pack_start(self.show_threats_found_check, False, False, 0)
        notif_box.pack_start(self.show_update_complete_check, False, False, 0)
        notif_box.pack_start(self.system_tray_check, False, False, 0)
        
        notif_frame.add(notif_box)
        box.pack_start(notif_frame, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Notifications"))
    
    def create_quarantine_tab(self):
        """Create quarantine tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Quarantine frame
        quarantine_frame = Gtk.Frame(label="Quarantine Settings")
        quarantine_grid = Gtk.Grid()
        quarantine_grid.set_margin_left(12)
        quarantine_grid.set_margin_right(12)
        quarantine_grid.set_margin_top(12)
        quarantine_grid.set_margin_bottom(12)
        quarantine_grid.set_row_spacing(6)
        quarantine_grid.set_column_spacing(12)
        
        self.auto_quarantine_check = Gtk.CheckButton.new_with_label("Automatically quarantine detected threats")
        
        path_label = Gtk.Label("Quarantine directory:")
        path_label.set_halign(Gtk.Align.START)
        
        path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.quarantine_path_entry = Gtk.Entry()
        browse_button = Gtk.Button.new_with_label("Browse...")
        browse_button.connect("clicked", self.on_browse_quarantine_path)
        
        path_box.pack_start(self.quarantine_path_entry, True, True, 0)
        path_box.pack_start(browse_button, False, False, 0)
        
        retention_label = Gtk.Label("Keep quarantined files for (days):")
        retention_label.set_halign(Gtk.Align.START)
        self.retention_spin = Gtk.SpinButton.new_with_range(1, 365, 1)
        
        quarantine_grid.attach(self.auto_quarantine_check, 0, 0, 2, 1)
        quarantine_grid.attach(path_label, 0, 1, 1, 1)
        quarantine_grid.attach(path_box, 1, 1, 1, 1)
        quarantine_grid.attach(retention_label, 0, 2, 1, 1)
        quarantine_grid.attach(self.retention_spin, 1, 2, 1, 1)
        
        quarantine_frame.add(quarantine_grid)
        box.pack_start(quarantine_frame, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Quarantine"))
    
    def create_interface_tab(self):
        """Create interface tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Interface frame
        interface_frame = Gtk.Frame(label="Interface Settings")
        interface_grid = Gtk.Grid()
        interface_grid.set_margin_left(12)
        interface_grid.set_margin_right(12)
        interface_grid.set_margin_top(12)
        interface_grid.set_margin_bottom(12)
        interface_grid.set_row_spacing(6)
        interface_grid.set_column_spacing(12)
        
        self.start_minimized_check = Gtk.CheckButton.new_with_label("Start minimized to system tray")
        self.close_to_tray_check = Gtk.CheckButton.new_with_label("Close to system tray instead of exit")
        
        theme_label = Gtk.Label("Theme:")
        theme_label.set_halign(Gtk.Align.START)
        
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.append_text("Auto (follow system)")
        self.theme_combo.append_text("Light")
        self.theme_combo.append_text("Dark")
        
        language_label = Gtk.Label("Language:")
        language_label.set_halign(Gtk.Align.START)
        
        self.language_combo = Gtk.ComboBoxText()
        self.language_combo.append_text("Auto (system default)")
        self.language_combo.append_text("English")
        self.language_combo.append_text("Hebrew")
        self.language_combo.append_text("Spanish")
        self.language_combo.append_text("French")
        self.language_combo.append_text("German")
        
        interface_grid.attach(self.start_minimized_check, 0, 0, 2, 1)
        interface_grid.attach(self.close_to_tray_check, 0, 1, 2, 1)
        interface_grid.attach(theme_label, 0, 2, 1, 1)
        interface_grid.attach(self.theme_combo, 1, 2, 1, 1)
        interface_grid.attach(language_label, 0, 3, 1, 1)
        interface_grid.attach(self.language_combo, 1, 3, 1, 1)
        
        interface_frame.add(interface_grid)
        box.pack_start(interface_frame, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Interface"))
    
    def create_exclusions_tab(self):
        """Create exclusions tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Excluded paths frame
        paths_frame = Gtk.Frame(label="Excluded Paths")
        paths_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        paths_box.set_margin_left(12)
        paths_box.set_margin_right(12)
        paths_box.set_margin_top(12)
        paths_box.set_margin_bottom(12)
        
        # Paths list
        scrolled_paths = Gtk.ScrolledWindow()
        scrolled_paths.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_paths.set_size_request(-1, 150)
        
        self.paths_liststore = Gtk.ListStore(str)
        self.paths_treeview = Gtk.TreeView(model=self.paths_liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Excluded Paths", renderer, text=0)
        self.paths_treeview.append_column(column)
        
        scrolled_paths.add(self.paths_treeview)
        
        # Paths buttons
        paths_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        add_path_btn = Gtk.Button.new_with_label("Add Path")
        add_path_btn.connect("clicked", self.on_add_excluded_path)
        remove_path_btn = Gtk.Button.new_with_label("Remove")
        remove_path_btn.connect("clicked", self.on_remove_excluded_path)
        
        paths_button_box.pack_start(add_path_btn, False, False, 0)
        paths_button_box.pack_start(remove_path_btn, False, False, 0)
        
        paths_box.pack_start(scrolled_paths, True, True, 0)
        paths_box.pack_start(paths_button_box, False, False, 0)
        paths_frame.add(paths_box)
        
        # Excluded extensions frame
        extensions_frame = Gtk.Frame(label="Excluded File Extensions")
        extensions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        extensions_box.set_margin_left(12)
        extensions_box.set_margin_right(12)
        extensions_box.set_margin_top(12)
        extensions_box.set_margin_bottom(12)
        
        # Extensions list
        scrolled_ext = Gtk.ScrolledWindow()
        scrolled_ext.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_ext.set_size_request(-1, 100)
        
        self.extensions_liststore = Gtk.ListStore(str)
        self.extensions_treeview = Gtk.TreeView(model=self.extensions_liststore)
        ext_renderer = Gtk.CellRendererText()
        ext_column = Gtk.TreeViewColumn("Extensions", ext_renderer, text=0)
        self.extensions_treeview.append_column(ext_column)
        
        scrolled_ext.add(self.extensions_treeview)
        
        # Extensions buttons
        ext_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        add_ext_btn = Gtk.Button.new_with_label("Add Extension")
        add_ext_btn.connect("clicked", self.on_add_excluded_extension)
        remove_ext_btn = Gtk.Button.new_with_label("Remove")
        remove_ext_btn.connect("clicked", self.on_remove_excluded_extension)
        
        ext_button_box.pack_start(add_ext_btn, False, False, 0)
        ext_button_box.pack_start(remove_ext_btn, False, False, 0)
        
        extensions_box.pack_start(scrolled_ext, True, True, 0)
        extensions_box.pack_start(ext_button_box, False, False, 0)
        extensions_frame.add(extensions_box)
        
        box.pack_start(paths_frame, True, True, 0)
        box.pack_start(extensions_frame, True, True, 0)
        
        self.notebook.append_page(box, Gtk.Label("Exclusions"))
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Performance frame
        performance_frame = Gtk.Frame(label="Performance Settings")
        performance_grid = Gtk.Grid()
        performance_grid.set_margin_left(12)
        performance_grid.set_margin_right(12)
        performance_grid.set_margin_top(12)
        performance_grid.set_margin_bottom(12)
        performance_grid.set_row_spacing(6)
        performance_grid.set_column_spacing(12)
        
        threads_label = Gtk.Label("Scan threads:")
        threads_label.set_halign(Gtk.Align.START)
        self.threads_spin = Gtk.SpinButton.new_with_range(1, 16, 1)
        
        memory_label = Gtk.Label("Memory limit (MB):")
        memory_label.set_halign(Gtk.Align.START)
        self.memory_spin = Gtk.SpinButton.new_with_range(128, 4096, 64)
        
        performance_grid.attach(threads_label, 0, 0, 1, 1)
        performance_grid.attach(self.threads_spin, 1, 0, 1, 1)
        performance_grid.attach(memory_label, 0, 1, 1, 1)
        performance_grid.attach(self.memory_spin, 1, 1, 1, 1)
        
        performance_frame.add(performance_grid)
        
        # Database frame
        database_frame = Gtk.Frame(label="Database Settings")
        database_grid = Gtk.Grid()
        database_grid.set_margin_left(12)
        database_grid.set_margin_right(12)
        database_grid.set_margin_top(12)
        database_grid.set_margin_bottom(12)
        database_grid.set_row_spacing(6)
        database_grid.set_column_spacing(12)
        
        mirror_label = Gtk.Label("Database mirror:")
        mirror_label.set_halign(Gtk.Align.START)
        
        self.mirror_combo = Gtk.ComboBoxText()
        self.mirror_combo.append_text("Auto (fastest)")
        self.mirror_combo.append_text("Official (database.clamav.net)")
        self.mirror_combo.append_text("Custom...")
        
        database_grid.attach(mirror_label, 0, 0, 1, 1)
        database_grid.attach(self.mirror_combo, 1, 0, 1, 1)
        
        database_frame.add(database_grid)
        
        # Logging frame
        logging_frame = Gtk.Frame(label="Logging Settings")
        logging_grid = Gtk.Grid()
        logging_grid.set_margin_left(12)
        logging_grid.set_margin_right(12)
        logging_grid.set_margin_top(12)
        logging_grid.set_margin_bottom(12)
        logging_grid.set_row_spacing(6)
        logging_grid.set_column_spacing(12)
        
        log_level_label = Gtk.Label("Log level:")
        log_level_label.set_halign(Gtk.Align.START)
        
        self.log_level_combo = Gtk.ComboBoxText()
        self.log_level_combo.append_text("Debug")
        self.log_level_combo.append_text("Info")
        self.log_level_combo.append_text("Warning")
        self.log_level_combo.append_text("Error")
        
        logging_grid.attach(log_level_label, 0, 0, 1, 1)
        logging_grid.attach(self.log_level_combo, 1, 0, 1, 1)
        
        logging_frame.add(logging_grid)
        
        # Reset button
        reset_button = Gtk.Button.new_with_label("Reset to Defaults")
        reset_button.connect("clicked", self.on_reset_settings)
        reset_button.set_halign(Gtk.Align.CENTER)
        
        box.pack_start(performance_frame, False, False, 0)
        box.pack_start(database_frame, False, False, 0)
        box.pack_start(logging_frame, False, False, 0)
        box.pack_start(reset_button, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label("Advanced"))
    
    def load_current_settings(self):
        """Load current settings into UI controls"""
        # Scan options
        scan_opts = self.settings.get("scan_options")
        self.scan_archives_check.set_active(scan_opts.get("scan_archives", True))
        self.scan_pdf_check.set_active(scan_opts.get("scan_pdf", True))
        self.scan_ole2_check.set_active(scan_opts.get("scan_ole2", True))
        self.scan_html_check.set_active(scan_opts.get("scan_html", True))
        self.scan_pe_check.set_active(scan_opts.get("scan_pe", True))
        self.scan_elf_check.set_active(scan_opts.get("scan_elf", True))
        self.detect_pua_check.set_active(scan_opts.get("detect_pua", False))
        self.scan_hidden_check.set_active(scan_opts.get("scan_hidden", False))
        self.max_file_spin.set_value(scan_opts.get("max_file_size", 20))
        self.max_recursion_spin.set_value(scan_opts.get("max_recursion", 15))
        
        # Real-time
        realtime_opts = self.settings.get("real_time")
        self.realtime_enabled_check.set_active(realtime_opts.get("enabled", False))
        self.watch_downloads_check.set_active(realtime_opts.get("watch_downloads", True))
        self.watch_home_check.set_active(realtime_opts.get("watch_home", False))
        self.watch_removable_check.set_active(realtime_opts.get("watch_removable", True))
        self.prevention_mode_check.set_active(realtime_opts.get("prevention_mode", False))
        
        # Updates
        updates_opts = self.settings.get("updates")
        self.auto_update_check.set_active(updates_opts.get("auto_update", True))
        frequency = updates_opts.get("update_frequency", "daily")
        freq_mapping = {"daily": 0, "weekly": 1, "manual": 2}
        self.frequency_combo.set_active(freq_mapping.get(frequency, 0))
        self.check_startup_check.set_active(updates_opts.get("check_on_startup", True))
        
        # Notifications
        notif_opts = self.settings.get("notifications")
        self.show_scan_complete_check.set_active(notif_opts.get("show_scan_complete", True))
        self.show_threats_found_check.set_active(notif_opts.get("show_threats_found", True))
        self.show_update_complete_check.set_active(notif_opts.get("show_update_complete", False))
        self.system_tray_check.set_active(notif_opts.get("system_tray", True))
        
        # Quarantine
        quarantine_opts = self.settings.get("quarantine")
        self.auto_quarantine_check.set_active(quarantine_opts.get("auto_quarantine", True))
        self.quarantine_path_entry.set_text(quarantine_opts.get("quarantine_path", ""))
        self.retention_spin.set_value(quarantine_opts.get("retention_days", 30))
        
        # Interface
        interface_opts = self.settings.get("interface")
        self.start_minimized_check.set_active(interface_opts.get("start_minimized", False))
        self.close_to_tray_check.set_active(interface_opts.get("close_to_tray", True))
        
        theme = interface_opts.get("dark_mode", "auto")
        theme_mapping = {"auto": 0, "light": 1, "dark": 2}
        self.theme_combo.set_active(theme_mapping.get(theme, 0))
        
        language = interface_opts.get("language", "auto")
        lang_mapping = {"auto": 0, "en": 1, "he": 2, "es": 3, "fr": 4, "de": 5}
        self.language_combo.set_active(lang_mapping.get(language, 0))
        
        # Exclusions
        exclusions = self.settings.get("exclusions")
        for path in exclusions.get("paths", []):
            self.paths_liststore.append([path])
        for ext in exclusions.get("extensions", []):
            self.extensions_liststore.append([ext])
        
        # Advanced
        advanced_opts = self.settings.get("advanced")
        self.threads_spin.set_value(advanced_opts.get("scan_threads", 4))
        self.memory_spin.set_value(advanced_opts.get("memory_limit", 512))
        
        mirror = advanced_opts.get("database_mirror", "auto")
        mirror_mapping = {"auto": 0, "official": 1, "custom": 2}
        self.mirror_combo.set_active(mirror_mapping.get(mirror, 0))
        
        log_level = advanced_opts.get("log_level", "info")
        log_mapping = {"debug": 0, "info": 1, "warning": 2, "error": 3}
        self.log_level_combo.set_active(log_mapping.get(log_level, 1))
    
    def save_current_settings(self):
        """Save UI settings back to settings object"""
        # Scan options
        self.settings.set("scan_options", "scan_archives", self.scan_archives_check.get_active())
        self.settings.set("scan_options", "scan_pdf", self.scan_pdf_check.get_active())
        self.settings.set("scan_options", "scan_ole2", self.scan_ole2_check.get_active())
        self.settings.set("scan_options", "scan_html", self.scan_html_check.get_active())
        self.settings.set("scan_options", "scan_pe", self.scan_pe_check.get_active())
        self.settings.set("scan_options", "scan_elf", self.scan_elf_check.get_active())
        self.settings.set("scan_options", "detect_pua", self.detect_pua_check.get_active())
        self.settings.set("scan_options", "scan_hidden", self.scan_hidden_check.get_active())
        self.settings.set("scan_options", "max_file_size", int(self.max_file_spin.get_value()))
        self.settings.set("scan_options", "max_recursion", int(self.max_recursion_spin.get_value()))
        
        # Real-time
        self.settings.set("real_time", "enabled", self.realtime_enabled_check.get_active())
        self.settings.set("real_time", "watch_downloads", self.watch_downloads_check.get_active())
        self.settings.set("real_time", "watch_home", self.watch_home_check.get_active())
        self.settings.set("real_time", "watch_removable", self.watch_removable_check.get_active())
        self.settings.set("real_time", "prevention_mode", self.prevention_mode_check.get_active())
        
        # Updates
        self.settings.set("updates", "auto_update", self.auto_update_check.get_active())
        freq_mapping = {0: "daily", 1: "weekly", 2: "manual"}
        self.settings.set("updates", "update_frequency", freq_mapping[self.frequency_combo.get_active()])
        self.settings.set("updates", "check_on_startup", self.check_startup_check.get_active())
        
        # Notifications
        self.settings.set("notifications", "show_scan_complete", self.show_scan_complete_check.get_active())
        self.settings.set("notifications", "show_threats_found", self.show_threats_found_check.get_active())
        self.settings.set("notifications", "show_update_complete", self.show_update_complete_check.get_active())
        self.settings.set("notifications", "system_tray", self.system_tray_check.get_active())
        
        # Quarantine
        self.settings.set("quarantine", "auto_quarantine", self.auto_quarantine_check.get_active())
        self.settings.set("quarantine", "quarantine_path", self.quarantine_path_entry.get_text())
        self.settings.set("quarantine", "retention_days", int(self.retention_spin.get_value()))
        
        # Interface
        self.settings.set("interface", "start_minimized", self.start_minimized_check.get_active())
        self.settings.set("interface", "close_to_tray", self.close_to_tray_check.get_active())
        
        theme_mapping = {0: "auto", 1: "light", 2: "dark"}
        self.settings.set("interface", "dark_mode", theme_mapping[self.theme_combo.get_active()])
        
        lang_mapping = {0: "auto", 1: "en", 2: "he", 3: "es", 4: "fr", 5: "de"}
        self.settings.set("interface", "language", lang_mapping[self.language_combo.get_active()])
        
        # Exclusions
        paths = []
        for row in self.paths_liststore:
            paths.append(row[0])
        self.settings.set("exclusions", "paths", paths)
        
        extensions = []
        for row in self.extensions_liststore:
            extensions.append(row[0])
        self.settings.set("exclusions", "extensions", extensions)
        
        # Advanced
        self.settings.set("advanced", "scan_threads", int(self.threads_spin.get_value()))
        self.settings.set("advanced", "memory_limit", int(self.memory_spin.get_value()))
        
        mirror_mapping = {0: "auto", 1: "official", 2: "custom"}
        self.settings.set("advanced", "database_mirror", mirror_mapping[self.mirror_combo.get_active()])
        
        log_mapping = {0: "debug", 1: "info", 2: "warning", 3: "error"}
        self.settings.set("advanced", "log_level", log_mapping[self.log_level_combo.get_active()])
    
    def on_browse_quarantine_path(self, button):
        """Browse for quarantine directory"""
        dialog = Gtk.FileChooserDialog(
            title="Choose Quarantine Directory",
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
            self.quarantine_path_entry.set_text(path)
        
        dialog.destroy()
    
    def on_add_excluded_path(self, button):
        """Add excluded path"""
        dialog = Gtk.FileChooserDialog(
            title="Choose Path to Exclude",
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
            self.paths_liststore.append([path])
        
        dialog.destroy()
    
    def on_remove_excluded_path(self, button):
        """Remove selected excluded path"""
        selection = self.paths_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            model.remove(treeiter)
    
    def on_add_excluded_extension(self, button):
        """Add excluded extension"""
        dialog = Gtk.Dialog(
            title="Add File Extension",
            parent=self,
            modal=True
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        
        content_area = dialog.get_content_area()
        content_area.set_margin_left(12)
        content_area.set_margin_right(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        
        label = Gtk.Label("File extension (e.g., .tmp, .log):")
        entry = Gtk.Entry()
        
        content_area.pack_start(label, False, False, 6)
        content_area.pack_start(entry, False, False, 6)
        
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            extension = entry.get_text().strip()
            if extension and not extension.startswith('.'):
                extension = '.' + extension
            if extension:
                self.extensions_liststore.append([extension])
        
        dialog.destroy()
    
    def on_remove_excluded_extension(self, button):
        """Remove selected excluded extension"""
        selection = self.extensions_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            model.remove(treeiter)
    
    def on_reset_settings(self, button):
        """Reset settings to defaults"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset Settings"
        )
        dialog.format_secondary_text(
            "Are you sure you want to reset all settings to their default values? "
            "This action cannot be undone."
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            # Reset settings to defaults
            self.settings.settings = self.settings.default_settings.copy()
            self.settings.save_settings()
            
            # Clear lists
            self.paths_liststore.clear()
            self.extensions_liststore.clear()
            
            # Reload UI
            self.load_current_settings()
        
        dialog.destroy()

class QuarantineManager:
    """Manage quarantined files"""
    
    def __init__(self, settings):
        self.settings = settings
        self.quarantine_path = Path(settings.get("quarantine", "quarantine_path"))
        self.ensure_quarantine_dir()
    
    def ensure_quarantine_dir(self):
        """Ensure quarantine directory exists"""
        self.quarantine_path.mkdir(parents=True, exist_ok=True)
    
    def quarantine_file(self, source_path, threat_name):
        """Move file to quarantine"""
        try:
            source = Path(source_path)
            if not source.exists():
                return False
            
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{source.name}_{threat_name}"
            quarantine_file = self.quarantine_path / quarantine_name
            
            # Move file to quarantine
            source.rename(quarantine_file)
            
            # Create info file
            info_file = quarantine_file.with_suffix('.info')
            info = {
                "original_path": str(source),
                "threat_name": threat_name,
                "quarantine_date": timestamp,
                "file_size": quarantine_file.stat().st_size
            }
            
            with open(info_file, 'w') as f:
                json.dump(info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error quarantining file: {e}")
            return False
    
    def list_quarantined_files(self):
        """List all quarantined files"""
        quarantined = []
        
        for info_file in self.quarantine_path.glob("*.info"):
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                
                quarantine_file = info_file.with_suffix('')
                if quarantine_file.exists():
                    info['quarantine_file'] = str(quarantine_file)
                    quarantined.append(info)
                    
            except Exception as e:
                print(f"Error reading quarantine info: {e}")
        
        return quarantined
    
    def restore_file(self, quarantine_file, original_path):
        """Restore file from quarantine"""
        try:
            qfile = Path(quarantine_file)
            original = Path(original_path)
            
            # Ensure original directory exists
            original.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back
            qfile.rename(original)
            
            # Remove info file
            info_file = qfile.with_suffix('.info')
            if info_file.exists():
                info_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error restoring file: {e}")
            return False
    
    def delete_quarantined_file(self, quarantine_file):
        """Permanently delete quarantined file"""
        try:
            qfile = Path(quarantine_file)
            info_file = qfile.with_suffix('.info')
            
            if qfile.exists():
                qfile.unlink()
            if info_file.exists():
                info_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting quarantined file: {e}")
            return False
    
    def cleanup_old_files(self):
        """Clean up old quarantined files based on retention policy"""
        retention_days = self.settings.get("quarantine", "retention_days")
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for info_file in self.quarantine_path.glob("*.info"):
            try:
                # Check file modification time
                file_time = datetime.fromtimestamp(info_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    quarantine_file = info_file.with_suffix('')
                    self.delete_quarantined_file(str(quarantine_file))
                    
            except Exception as e:
                print(f"Error during cleanup: {e}")

# Example usage
if __name__ == "__main__":
    # Test settings
    settings = XClamAVSettings()
    
    # Create simple test window
    app = Gtk.Application()
    window = Gtk.ApplicationWindow(application=app)
    window.set_title("XClamAV Settings Test")
    window.set_default_size(400, 300)
    
    button = Gtk.Button.new_with_label("Open Settings")
    
    def on_button_clicked(btn):
        dialog = SettingsDialog(window, settings)
        response = dialog.run()
        if response in (Gtk.ResponseType.OK, Gtk.ResponseType.APPLY):
            dialog.save_current_settings()
        dialog.destroy()
    
    button.connect("clicked", on_button_clicked)
    window.add(button)
    
    window.show_all()
    app.run()