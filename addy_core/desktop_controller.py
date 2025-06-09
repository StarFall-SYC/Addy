# addy_core/desktop_controller.py

import pyautogui
from PIL import Image
import time
import os
import logging
import pygetwindow # For window manipulation

class DesktopController:
    def __init__(self, config=None):
        """Initializes the Desktop Controller."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.info("DesktopController initialized.")
        # pyautogui.FAILSAFE = True # Enable failsafe by moving mouse to top-left corner

    def capture_screen(self, filename="screenshot.png", region=None):
        """
        Captures the screen or a region of the screen.

        Args:
            filename (str): The name to save the screenshot as.
            region (tuple, optional): A tuple (left, top, width, height) specifying the region to capture.
                                      If None, captures the full screen.

        Returns:
            str: Path to the saved screenshot, or None if failed.
        """
        try:
            self.logger.info(f"Capturing screen to {filename} (region: {region})")
            screenshot = pyautogui.screenshot(region=region)
            # Ensure screenshots directory exists
            screenshots_dir = self.config.get('Paths', 'screenshots_dir', fallback='screenshots')
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            filepath = os.path.join(screenshots_dir, filename)
            screenshot.save(filepath)
            self.logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            return None

    def move_mouse(self, x, y, duration=0.25, relative=False):
        """
        Moves the mouse cursor to the specified coordinates.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            duration (float): Time in seconds to move the mouse.
            relative (bool): If True, x and y are relative to the current mouse position.
        """
        try:
            self.logger.info(f"Moving mouse to ({x}, {y}), duration: {duration}, relative: {relative}")
            if relative:
                pyautogui.moveRel(x, y, duration=duration)
            else:
                pyautogui.moveTo(x, y, duration=duration)
            self.logger.info("Mouse move complete.")
            return True
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return False

    def click_mouse(self, x=None, y=None, button='left', clicks=1, interval=0.1, duration=0.0):
        """
        Performs a mouse click.

        Args:
            x (int, optional): The x-coordinate to move to before clicking. If None, clicks at current position.
            y (int, optional): The y-coordinate to move to before clicking. If None, clicks at current position.
            button (str): 'left', 'middle', 'right'.
            clicks (int): Number of clicks.
            interval (float): Time in seconds between clicks.
            duration (float): Time in seconds to spend pressing the button down (for drags).
        """
        try:
            self.logger.info(f"Performing mouse click at ({x}, {y}), button: {button}, clicks: {clicks}")
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval, duration=duration)
            self.logger.info("Mouse click complete.")
            return True
        except Exception as e:
            self.logger.error(f"Error clicking mouse: {e}")
            return False

    def type_text(self, text, interval=0.05):
        """
        Types the given text using the keyboard.

        Args:
            text (str): The text to type.
            interval (float): Time in seconds between keystrokes.
        """
        try:
            self.logger.info(f"Typing text: '{text}'")
            pyautogui.typewrite(text, interval=interval)
            self.logger.info("Text typing complete.")
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False

    def press_key(self, key_name):
        """
        Presses a special key (e.g., 'enter', 'ctrl', 'shift', 'alt', 'f1').

        Args:
            key_name (str): The name of the key to press.
        """
        try:
            self.logger.info(f"Pressing key: {key_name}")
            pyautogui.press(key_name)
            self.logger.info(f"Key '{key_name}' pressed.")
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key '{key_name}': {e}")
            return False

    def hotkey(self, *args):
        """
        Presses a combination of keys simultaneously (e.g., 'ctrl', 'c').

        Args:
            *args: A sequence of key names.
        """
        try:
            self.logger.info(f"Performing hotkey: {args}")
            pyautogui.hotkey(*args)
            self.logger.info(f"Hotkey {args} performed.")
            return True
        except Exception as e:
            self.logger.error(f"Error performing hotkey {args}: {e}")
            return False

    def locate_on_screen(self, image_path, confidence=0.9, region=None, grayscale=False):
        """
        Locates an image on the screen.

        Args:
            image_path (str): Path to the image file to search for.
            confidence (float): The confidence level for the match (0.0 to 1.0).
                                Requires OpenCV and opencv-python to be installed.
            region (tuple, optional): A tuple (left, top, width, height) specifying the region to search in.
            grayscale (bool): If True, converts the image and screen to grayscale for faster matching.

        Returns:
            Box(left, top, width, height) or None: A named tuple of the coordinates and size of the found image,
                                                  or None if not found.
        """
        try:
            self.logger.info(f"Locating image '{image_path}' on screen (confidence: {confidence}, region: {region})")
            # PyAutoGUI's locateOnScreen can be slow and might require OpenCV for confidence.
            # For basic use without OpenCV, confidence might not be as effective.
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
            if location:
                self.logger.info(f"Image '{image_path}' found at: {location}")
            else:
                self.logger.info(f"Image '{image_path}' not found on screen.")
            return location
        except Exception as e:
            # pyautogui.ImageNotFoundException might be raised if not found, but we catch generic Exception too.
            if "locateOnScreen() requires an Pillow module" in str(e) or \
               "locateOnScreen() requires an OpenCV module" in str(e):
                self.logger.warning(f"Missing dependency for locateOnScreen: {e}. Please install Pillow and/or opencv-python.")
            else:
                self.logger.error(f"Error locating image '{image_path}' on screen: {e}")
            return None

    def get_screen_size(self):
        """
        Gets the current screen resolution.

        Returns:
            tuple: (width, height) of the screen.
        """
        return pyautogui.size()

    # --- Window Management Functions ---
    def get_active_window(self):
        """
        Gets the currently active window.

        Returns:
            pygetwindow.Window or None: The active window object, or None if error.
        """
        try:
            active_window = pygetwindow.getActiveWindow()
            if active_window:
                self.logger.info(f"Active window: '{active_window.title}'")
                return active_window
            else:
                self.logger.warning("No active window found.")
                return None
        except Exception as e:
            self.logger.error(f"Error getting active window: {e}")
            return None

    def get_window_by_title(self, title_substring, exact_match=False):
        """
        Finds a window by its title (or a substring of it).

        Args:
            title_substring (str): The substring to search for in window titles.
            exact_match (bool): If True, requires an exact title match (case-sensitive).

        Returns:
            pygetwindow.Window or None: The first matching window object, or None if not found/error.
        """
        try:
            self.logger.info(f"Searching for window with title containing: '{title_substring}' (exact: {exact_match})")
            windows = pygetwindow.getWindowsWithTitle(title_substring)
            if windows:
                if exact_match:
                    for window in windows:
                        if window.title == title_substring:
                            self.logger.info(f"Found exact match window: '{window.title}'")
                            return window
                    self.logger.info(f"No exact match found for title '{title_substring}'.")
                    return None
                else:
                    self.logger.info(f"Found window: '{windows[0].title}' (first match)")
                    return windows[0] # Return the first match
            else:
                self.logger.info(f"No window found with title containing '{title_substring}'.")
                return None
        except Exception as e:
            self.logger.error(f"Error finding window by title '{title_substring}': {e}")
            return None

    def activate_window(self, window_title_substring=None, window_obj=None):
        """
        Activates (brings to front) the specified window.

        Args:
            window_title_substring (str, optional): Title substring of the window to activate.
            window_obj (pygetwindow.Window, optional): A pygetwindow.Window object to activate.
                                                    If both are provided, window_obj takes precedence.
        Returns:
            bool: True if successful, False otherwise.
        """
        target_window = window_obj
        if not target_window and window_title_substring:
            target_window = self.get_window_by_title(window_title_substring)
        
        if target_window:
            try:
                self.logger.info(f"Activating window: '{target_window.title}'")
                if target_window.isMinimized:
                    target_window.restore()
                target_window.activate()
                self.logger.info(f"Window '{target_window.title}' activated.")
                return True
            except Exception as e:
                self.logger.error(f"Error activating window '{target_window.title}': {e}")
                return False
        else:
            self.logger.warning(f"Window not found for activation (title: {window_title_substring}).")
            return False

    def minimize_window(self, window_title_substring=None, window_obj=None):
        """Minimizes the specified window."""
        target_window = window_obj
        if not target_window and window_title_substring:
            target_window = self.get_window_by_title(window_title_substring)
        
        if target_window:
            try:
                self.logger.info(f"Minimizing window: '{target_window.title}'")
                target_window.minimize()
                self.logger.info(f"Window '{target_window.title}' minimized.")
                return True
            except Exception as e:
                self.logger.error(f"Error minimizing window '{target_window.title}': {e}")
                return False
        else:
            self.logger.warning(f"Window not found for minimizing (title: {window_title_substring}).")
            return False

    def maximize_window(self, window_title_substring=None, window_obj=None):
        """Maximizes the specified window."""
        target_window = window_obj
        if not target_window and window_title_substring:
            target_window = self.get_window_by_title(window_title_substring)
        
        if target_window:
            try:
                self.logger.info(f"Maximizing window: '{target_window.title}'")
                target_window.maximize()
                self.logger.info(f"Window '{target_window.title}' maximized.")
                return True
            except Exception as e:
                self.logger.error(f"Error maximizing window '{target_window.title}': {e}")
                return False
        else:
            self.logger.warning(f"Window not found for maximizing (title: {window_title_substring}).")
            return False

    def close_window(self, window_title_substring=None, window_obj=None):
        """Closes the specified window."""
        target_window = window_obj
        if not target_window and window_title_substring:
            target_window = self.get_window_by_title(window_title_substring)
        
        if target_window:
            try:
                self.logger.info(f"Closing window: '{target_window.title}'")
                target_window.close()
                self.logger.info(f"Window '{target_window.title}' closed.")
                return True
            except Exception as e:
                self.logger.error(f"Error closing window '{target_window.title}': {e}")
                return False
        else:
            self.logger.warning(f"Window not found for closing (title: {window_title_substring}).")
            return False

    def list_all_windows(self):
        """
        Lists all visible window titles.

        Returns:
            list: A list of window titles.
        """
        try:
            titles = pygetwindow.getAllTitles()
            self.logger.info(f"All window titles: {titles}")
            return [title for title in titles if title] # Filter out empty titles
        except Exception as e:
            self.logger.error(f"Error listing all windows: {e}")
            return []

# Example Usage (for testing purposes)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    
    # Create a dummy config for testing paths
    class DummyConfig:
        def get(self, section, option, fallback=None):
            if section == 'Paths' and option == 'screenshots_dir':
                return 'test_screenshots'
            return fallback

    controller = DesktopController(config=DummyConfig())

    print(f"Screen size: {controller.get_screen_size()}")

    # Test screenshot
    # controller.capture_screen("full_screen_test.png")
    # controller.capture_screen("region_test.png", region=(0, 0, 300, 300))

    # Test mouse movement (BE CAREFUL WITH MOUSE CONTROL)
    # print("Moving mouse to (100, 100) in 1 second...")
    # time.sleep(1)
    # controller.move_mouse(100, 100, duration=0.5)
    # print("Moving mouse relatively by (50, 50) in 1 second...")
    # time.sleep(1)
    # controller.move_mouse(50, 50, relative=True, duration=0.5)

    # Test mouse click (BE CAREFUL)
    # print("Clicking at current position in 2 seconds...")
    # time.sleep(2)
    # controller.click_mouse()
    # print("Double clicking at (200,200) in 2 seconds...")
    # time.sleep(2)
    # controller.click_mouse(x=200, y=200, clicks=2)

    # Test typing (BE CAREFUL - ensure a safe place to type, like a notepad)
    # print("Typing 'Hello, Addy!' in Notepad in 3 seconds...")
    # print("Please open Notepad and make it the active window.")
    # time.sleep(3) 
    # controller.type_text("Hello, Addy! This is a test.\n", interval=0.1)
    # controller.press_key('enter')
    # controller.hotkey('ctrl', 's') # Example: try to save

    # Test locate on screen (requires an image file 'test_icon.png' to be present)
    # Create a dummy 'test_icon.png' or use an existing small icon for testing.
    # For example, take a screenshot of a small, unique icon on your desktop.
    # print("Attempting to locate 'test_icon.png' on screen...")
    # location = controller.locate_on_screen('test_icon.png', confidence=0.8) # Adjust confidence
    # if location:
    #     print(f"Found 'test_icon.png' at: {location}")
    #     # Example: click on the found icon's center
    #     # center_x = location.left + location.width // 2
    #     # center_y = location.top + location.height // 2
    #     # controller.click_mouse(x=center_x, y=center_y)
    # else:
    #     print("'test_icon.png' not found.")

    print("DesktopController tests finished. Remember to be cautious with automation.")