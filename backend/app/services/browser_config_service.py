import os
import platform
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class BrowserConfigService:
    """Service for managing browser configurations and detection."""
    
    def __init__(self):
        """Initialize the browser configuration service."""
        self.supported_browsers = {
            "chrome": {
                "name": "Google Chrome",
                "executable_paths": self._get_chrome_paths(),
                "args": [
                    "--no-first-run", 
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-observable",
                    "--disable-ipc-flooding-protection",
                    "--disable-web-security",  # For parallel execution
                    "--allow-running-insecure-content",
                    "--disable-features=VizDisplayCompositor"
                ]
            },
            "edge": {
                "name": "Microsoft Edge",
                "executable_paths": self._get_edge_paths(),
                "args": [
                    "--no-first-run", 
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-observable",
                    "--disable-ipc-flooding-protection",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
            },
            "firefox": {
                "name": "Mozilla Firefox",
                "executable_paths": self._get_firefox_paths(),
                "args": [
                    "--no-first-run", 
                    "--disable-background-timer-throttling",
                    "--disable-web-security"
                ]
            },
            "chromium": {
                "name": "Chromium",
                "executable_paths": self._get_chromium_paths(),
                "args": [
                    "--no-first-run", 
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-observable",
                    "--disable-ipc-flooding-protection",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
            }
        }
    
    def _get_chrome_paths(self) -> List[str]:
        """Get possible Chrome executable paths based on the operating system."""
        paths = []
        system = platform.system()
        
        if system == "Windows":
            paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome"
            ]
        else:  # Linux
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        
        return [path for path in paths if os.path.exists(path)]
    
    def _get_edge_paths(self) -> List[str]:
        """Get possible Edge executable paths based on the operating system."""
        paths = []
        system = platform.system()
        
        if system == "Windows":
            paths = [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\Application\\msedge.exe"),
                os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge SxS\\Application\\msedge.exe")  # Edge Dev
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        
        return [path for path in paths if os.path.exists(path)]
    
    def _get_firefox_paths(self) -> List[str]:
        """Get possible Firefox executable paths based on the operating system."""
        paths = []
        system = platform.system()
        
        if system == "Windows":
            paths = [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
                os.path.expanduser("~\\AppData\\Local\\Mozilla Firefox\\firefox.exe"),
                os.path.expanduser("~\\AppData\\Local\\Firefox Developer Edition\\firefox.exe")
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Firefox.app/Contents/MacOS/firefox",
                "/usr/bin/firefox"
            ]
        else:  # Linux
            paths = [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr"
            ]
        
        return [path for path in paths if os.path.exists(path)]
    
    def _get_chromium_paths(self) -> List[str]:
        """Get possible Chromium executable paths based on the operating system."""
        paths = []
        system = platform.system()
        
        if system == "Windows":
            paths = [
                "C:\\Program Files\\Chromium\\Application\\chrome.exe",
                os.path.expanduser("~\\AppData\\Local\\Chromium\\Application\\chrome.exe")
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        else:  # Linux
            paths = [
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        
        return [path for path in paths if os.path.exists(path)]
    
    def detect_installed_browsers(self) -> Dict[str, str]:
        """
        Detect installed browsers on the system.
        
        Returns:
            Dict[str, str]: Dictionary of browser names and their executable paths
        """
        installed_browsers = {}
        
        for browser_key, browser_info in self.supported_browsers.items():
            for path in browser_info["executable_paths"]:
                if os.path.exists(path):
                    installed_browsers[browser_key] = path
                    break
        
        return installed_browsers
    
    def get_browser_config(self, browser_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific browser.
        
        Args:
            browser_name (str): Name of the browser (chrome, edge, chromium)
            
        Returns:
            Optional[Dict]: Browser configuration or None if not found
        """
        return self.supported_browsers.get(browser_name.lower())
    
    def validate_browser_config(self, browser_name: str, executable_path: str = None) -> Tuple[bool, str]:
        """
        Validate browser configuration.
        
        Args:
            browser_name (str): Name of the browser
            executable_path (str, optional): Custom executable path
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if browser_name.lower() not in self.supported_browsers:
            return False, f"Browser '{browser_name}' is not supported"
        
        # If custom path provided, validate it
        if executable_path:
            if not os.path.exists(executable_path):
                return False, f"Browser executable not found at '{executable_path}'"
            if not os.access(executable_path, os.X_OK):
                return False, f"Browser executable at '{executable_path}' is not executable"
            return True, ""
        
        # Check if browser is installed
        installed_browsers = self.detect_installed_browsers()
        if browser_name.lower() not in installed_browsers:
            return False, f"Browser '{browser_name}' is not installed or not found"
        
        return True, ""
    
    def get_default_resolution(self) -> Tuple[int, int]:
        """
        Get default browser window resolution.
        
        Returns:
            Tuple[int, int]: Width and height
        """
        return (1920, 1080)
    
    def validate_resolution(self, width: int, height: int) -> Tuple[bool, str]:
        """
        Validate browser window resolution.
        
        Args:
            width (int): Window width
            height (int): Window height
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(width, int) or not isinstance(height, int):
            return False, "Width and height must be integers"
        
        if width < 800 or height < 600:
            return False, "Minimum resolution is 800x600"
        
        if width > 3840 or height > 2160:
            return False, "Maximum resolution is 3840x2160"
        
        return True, ""
    
    def get_browser_version(self, executable_path: str) -> Optional[str]:
        """
        Get the version of a browser executable.
        
        Args:
            executable_path (str): Path to the browser executable
            
        Returns:
            Optional[str]: Browser version or None if not found
        """
        try:
            import subprocess
            # Different browsers might have different version flags
            version_flags = ['--version', '-version', '/version']
            
            for flag in version_flags:
                try:
                    result = subprocess.run([executable_path, flag], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Extract version from output
                        output = result.stdout.strip()
                        # For Chrome/Chromium/Edge: "Google Chrome 123.0.6312.86"
                        # For Firefox: "Mozilla Firefox 123.0"
                        parts = output.split()
                        if len(parts) >= 3:
                            return parts[-1]  # Return the version part
                        elif len(parts) >= 1:
                            # Try to find version-like string in the output
                            import re
                            version_match = re.search(r'\d+\.\d+(\.\d+)*', output)
                            if version_match:
                                return version_match.group(0)
                except Exception:
                    continue  # Try next flag
            return None
        except Exception:
            return None
    
    def get_installed_browsers_with_versions(self) -> Dict[str, Dict[str, str]]:
        """
        Get installed browsers with their versions.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary of browser info {name: {path, version}}
        """
        browsers_info = {}
        installed_browsers = self.detect_installed_browsers()
        
        for browser_name, path in installed_browsers.items():
            version = self.get_browser_version(path)
            browsers_info[browser_name] = {
                "path": path,
                "version": version or "Unknown"
            }
        
        return browsers_info
    
    def get_parallel_execution_args(self, browser_name: str) -> List[str]:
        """
        Get browser arguments optimized for parallel execution.
        
        Args:
            browser_name (str): Name of the browser
            
        Returns:
            List[str]: Browser arguments for parallel execution
        """
        browser_config = self.get_browser_config(browser_name)
        if not browser_config:
            return []
        
        # Base arguments for parallel execution
        parallel_args = browser_config.get("args", []).copy()
        
        # Add parallel execution specific arguments (excluding CDP port which is added separately)
        parallel_specific_args = [
            "--disable-dev-shm-usage",  # Overcome limited resource problems
            "--disable-gpu",  # Disable GPU for headless environments
            "--disable-extensions",  # Disable extensions for consistency
            "--disable-default-apps",  # Disable default apps
            "--disable-breakpad",  # Disable crash reporting
            "--no-sandbox",  # Disable sandbox for better compatibility
            "--disable-background-networking",  # Disable background networking
            "--disable-client-side-phishing-detection",  # Disable phishing detection
            "--disable-component-update",  # Disable component updates
            "--disable-hang-monitor",  # Disable hang monitor
            "--disable-popup-blocking",  # Disable popup blocking
            "--disable-prompt-on-repost",  # Disable prompt on repost
            "--disable-sync",  # Disable sync
            "--enable-automation",  # Enable automation
            "--enable-logging",  # Enable logging
            "--ignore-certificate-errors",  # Ignore certificate errors
            "--log-level=0",  # Set log level
            "--metrics-recording-only",  # Metrics recording only
            "--password-store=basic",  # Use basic password store
            "--use-mock-keychain"  # Use mock keychain
        ]
        
        # Merge the arguments
        parallel_args.extend(parallel_specific_args)
        
        return parallel_args
    
    def get_vision_args(self, vision_enabled: bool = True) -> List[str]:
        """
        Get browser arguments for vision capabilities.
        
        Args:
            vision_enabled (bool): Whether vision capabilities are enabled
            
        Returns:
            List[str]: Browser arguments for vision capabilities
        """
        if not vision_enabled:
            return []
        
        # Vision-specific arguments (simplified for on/off only)
        vision_args = [
            "--enable-features=WebContentsForceDark:force_dark_mode_enabled",
            "--force-dark-mode",
            "--enable-automation",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-observable"
        ]
        
        return vision_args
    
    def get_cdp_args(self, cdp_port: Optional[int] = None) -> List[str]:
        """
        Get browser arguments for CDP (Chrome DevTools Protocol) connections.
        
        Args:
            cdp_port (Optional[int]): Custom CDP port, defaults to 9222 if not specified
            
        Returns:
            List[str]: Browser arguments for CDP connections
        """
        port = cdp_port or 9222
        return [f"--remote-debugging-port={port}"]
    
    def get_custom_resolution_args(self, width: int, height: int) -> List[str]:
        """
        Get browser arguments for custom window resolution.
        
        Args:
            width (int): Window width
            height (int): Window height
            
        Returns:
            List[str]: Browser arguments for custom resolution
        """
        return [f"--window-size={width},{height}"]
    
    def get_all_browser_args(self, browser_name: str, 
                           vision_enabled: bool = True, 
                           cdp_port: Optional[int] = None,
                           custom_width: Optional[int] = None,
                           custom_height: Optional[int] = None) -> List[str]:
        """
        Get all browser arguments combining parallel execution, vision, CDP, and custom resolution settings.
        
        Args:
            browser_name (str): Name of the browser
            vision_enabled (bool): Whether vision capabilities are enabled
            cdp_port (Optional[int]): Custom CDP port
            custom_width (Optional[int]): Custom window width
            custom_height (Optional[int]): Custom window height
            
        Returns:
            List[str]: Combined browser arguments
        """
        try:
            # Get base parallel execution arguments
            args = self.get_parallel_execution_args(browser_name)
            
            # Add vision arguments
            args.extend(self.get_vision_args(vision_enabled))
            
            # Add CDP arguments
            args.extend(self.get_cdp_args(cdp_port))
            
            # Add custom resolution arguments if provided
            if custom_width and custom_height:
                args.extend(self.get_custom_resolution_args(custom_width, custom_height))
            
            # Use a set to store unique arguments to prevent duplicates
            # For arguments with values (like --window-size=1920,1080), we need special handling
            unique_args = []
            seen_flags = set()
            
            for arg in args:
                # Handle arguments with values
                if '=' in arg:
                    flag = arg.split('=')[0]
                    if flag not in seen_flags:
                        unique_args.append(arg)
                        seen_flags.add(flag)
                else:
                    # Handle simple flags
                    if arg not in seen_flags:
                        unique_args.append(arg)
                        seen_flags.add(arg)
            
            return unique_args
        except Exception as e:
            import logging
            logging.error(f"Error generating browser arguments: {e}")
            # Return minimal safe arguments
            return [
                "--no-first-run",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-observable"
            ]

# Global instance
browser_config_service = BrowserConfigService()