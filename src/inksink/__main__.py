# spellchecker:ignore signum

import logging
import signal
import threading

from inksink.core.config import load_settings
from inksink.core.display import Display
from inksink.core.input import HardwareNotAvailable, InputHandler
from inksink.core.layout import fill_error
from inksink.core.renderer import Orientation, render
from inksink.core.startup import startup
from inksink.display_server import DisplayServer
from inksink.launcher.app import Launcher


def _render_loop(
    display_server,
    compositor,
    input_handler,
    display,
    settings: dict,
    display_server_event: threading.Event,
) -> None:
    """Poll display server slot, run Launcher, recover from errors."""
    while True:
        if display_server is not None:
            pending = display_server.take()
            if pending is not None:
                img, mode = pending
                if compositor is not None:
                    compositor.set_content(img, mode=mode)
                    if input_handler.wait_for_action(display_server_event) == "":
                        continue
        display_server_event.clear()
        try:
            Launcher(
                display,
                input_handler,
                settings,
                compositor,
                stop_event=display_server_event,
            ).run()
        except KeyboardInterrupt:
            break
        # intentional top-level recovery handler to show error screen
        except Exception as e:  # noqa: BLE001
            _handle_app_exception(e, compositor, display, input_handler, settings)


def _handle_app_exception(
    e: Exception,
    compositor,
    display,
    input_handler,
    settings: dict,
) -> None:
    logging.exception("App error")
    if compositor is not None:
        compositor.stop()
    html = fill_error(str(e))
    image = render(
        html,
        orientation=Orientation(settings["apps"]["launcher"]["orientation"]),
    )
    display.display_full(image)
    input_handler.wait_for_action()
    if compositor is not None:
        compositor.start()


def main() -> None:
    settings = load_settings()

    display = Display(
        idle_timeout=settings["display"]["idle_timeout"],
        portrait_rotation=settings["display"]["portrait_rotation"],
        landscape_rotation=settings["display"]["landscape_rotation"],
        full_refresh_interval=settings["display"]["full_refresh_interval"],
    )
    compositor = startup(settings, display, active_app="launcher")
    input_handler = InputHandler()

    def _sigterm_handler(*_):  # noqa: ANN002
        if compositor is not None:
            compositor.stop()
        display.sleep()
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, _sigterm_handler)

    try:
        input_handler.setup()
    except HardwareNotAvailable as e:
        print(f"Hardware not available: {e}. Exiting (non-Pi host).")
        return

    display.init()
    if compositor is not None:
        compositor.start()

    display_server = None
    display_server_event = threading.Event()
    try:
        if settings["apps"]["display_server"]["enabled"]:
            display_server = DisplayServer(settings, notify_event=display_server_event)
            display_server.start()
        _render_loop(
            display_server,
            compositor,
            input_handler,
            display,
            settings,
            display_server_event,
        )
    finally:
        if display_server is not None:
            display_server.stop()
        if compositor is not None:
            compositor.stop()
        display.sleep()


if __name__ == "__main__":
    main()
