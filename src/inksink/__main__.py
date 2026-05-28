# spellchecker:ignore signum

import logging
import signal

from inksink.core.config import load_settings
from inksink.core.display import Display
from inksink.core.input import HardwareNotAvailable, InputHandler
from inksink.core.layout import fill_error
from inksink.core.renderer import Orientation, render
from inksink.core.startup import startup
from inksink.launcher.app import Launcher


def main() -> None:
    settings = load_settings()
    startup(settings)

    display = Display(
        idle_timeout=settings["display"]["idle_timeout"],
        portrait_rotation=settings["display"]["portrait_rotation"],
        landscape_rotation=settings["display"]["landscape_rotation"],
        full_refresh_interval=settings["display"]["full_refresh_interval"],
    )
    input_handler = InputHandler()

    def _sigterm_handler(signum, frame):  # noqa: ANN001
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, _sigterm_handler)

    try:
        input_handler.setup()
    except HardwareNotAvailable as e:
        print(f"Hardware not available: {e}. Exiting (non-Pi host).")
        return

    display.init()
    while True:
        try:
            Launcher(display, input_handler, settings).run()
        except KeyboardInterrupt:
            display.sleep()
            break
        except Exception as e:
            logging.exception("App error")
            html = fill_error(str(e))
            image = render(
                html,
                orientation=Orientation(settings["apps"]["launcher"]["orientation"]),
            )
            display.display_full(image)
            input_handler.wait_for_action()


if __name__ == "__main__":
    main()
