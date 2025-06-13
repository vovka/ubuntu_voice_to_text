import os


class TrayIconManager:
    def __init__(self, state_ref):
        self.state_ref = state_ref
        self.icon = None

    def create_image_text(self, state="idle"):
        try:
            from PIL import Image, ImageDraw

            width, height = 32, 32
            image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            dc = ImageDraw.Draw(image)

            if state == "finish_listening":
                color = (40, 150, 150)  # blue
            elif state == "listening":
                color = (40, 255, 40)  # green
            else:
                color = (120, 120, 120)  # grey

            # Draw a filled circle
            dc.ellipse(
                [(4, 4), (width - 4, height - 4)],
                fill=color,
                outline=(60, 60, 60),
                width=2,
            )

            return image
        except ImportError:
            print(
                "[TrayIconManager] PIL not available, tray icon functionality disabled"
            )
            return None

    def update_icon(self):
        if self.icon:
            print(f"[TrayIconManager] Updating icon: state={self.state_ref.state}")
            self.icon.icon = self.create_image_text(self.state_ref.state)
            if self.state_ref.state == "finish_listening":
                self.icon.title = "Voice Typing: finish_listening"
            elif self.state_ref.state == "listening":
                self.icon.title = "Voice Typing: ON"
            else:
                self.icon.title = "Voice Typing: OFF"

    def exit_application(self, icon, item):
        """Exit the application cleanly."""
        print("[TrayIconManager] Exit requested from tray menu")
        icon.stop()
        os._exit(0)

    def tray_thread(self):
        print("[TrayIconManager] Starting tray icon thread")
        try:
            import pystray

            # Create menu with Exit item
            menu = pystray.Menu(pystray.MenuItem("Exit", self.exit_application))
            self.icon = pystray.Icon("voice_typing", menu=menu)
            self.state_ref.icon = self.icon
            self.update_icon()
            self.icon.run()
        except ImportError:
            print(
                "[TrayIconManager] pystray not available, "
                "tray icon functionality disabled"
            )
