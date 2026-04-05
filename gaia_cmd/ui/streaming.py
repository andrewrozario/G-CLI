import time
import sys
from rich.live import Live
from rich.text import Text
from gaia_cmd.ui.display import console

class GaiaStreamer:
    @staticmethod
    def stream_text(text: str, delay: float = 0.005, prefix: str = "◉ GAIA > "):
        """
        Streams text with a typing effect using rich.live for smooth rendering.
        """
        console.print(f"\n[gaia.prompt]{prefix}[/]", end="")
        
        # Use simple iterative print for character-level streaming
        # Live is better for block-level updates, but for char-level,
        # simple stdout flush works well with rich console formatting.
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print("\n")

    @staticmethod
    def live_render(content_generator):
        """
        Uses rich.live.Live to render content that updates in real-time.
        """
        with Live(console=console, refresh_per_second=10) as live:
            for update in content_generator():
                live.update(update)
