import sys
import threading
from unittest.mock import MagicMock

import pytest

# Stub RPi.GPIO before importing input module
_gpio_stub = MagicMock()
sys.modules.setdefault("RPi", MagicMock(GPIO=_gpio_stub))
sys.modules.setdefault("RPi.GPIO", _gpio_stub)

from inksink.core.input import InputHandler  # noqa: E402


def test_setup_raises_hardware_not_available_when_gpio_absent():
    from inksink.core.input import HardwareNotAvailable

    h = InputHandler()
    h._gpio = None
    with pytest.raises(HardwareNotAvailable):
        h.setup()


def test_wait_for_action_raises_hardware_not_available_when_gpio_absent():
    from inksink.core.input import HardwareNotAvailable

    h = InputHandler()
    h._gpio = None
    with pytest.raises(HardwareNotAvailable):
        h.wait_for_action()


def test_setup_configures_pull_ups():
    gpio = MagicMock()
    gpio.BCM = 11
    gpio.IN = 1
    gpio.PUD_UP = 22
    h = InputHandler()
    h._gpio = gpio
    h.setup()
    gpio.setmode.assert_called_once_with(gpio.BCM)
    for pin in h._pin_map:
        gpio.setup.assert_any_call(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
    assert gpio.setup.call_count == len(h._pin_map)


def test_raises_on_empty_pin_map():
    with pytest.raises(ValueError, match="pin_map"):
        InputHandler(pin_map={})


def test_default_mapping_pin_12_is_btn_2():
    h = InputHandler()
    assert h._pin_map[12] == "btn_2"


def test_default_mapping_has_all_eight_generic_buttons():
    h = InputHandler()
    assert set(h._pin_map.values()) == {
        "btn_1",
        "btn_2",
        "btn_3",
        "btn_4",
        "btn_5",
        "btn_6",
        "btn_7",
        "btn_8",
    }


def test_default_mapping_power_not_a_value():
    h = InputHandler()
    assert "power" not in h._pin_map.values()


def test_default_mapping_gpio_assignments():
    h = InputHandler()
    assert h._pin_map == {
        4: "btn_1",
        12: "btn_2",
        13: "btn_3",
        16: "btn_4",
        19: "btn_5",
        22: "btn_6",
        26: "btn_7",
        27: "btn_8",
    }


def test_wait_for_action_raises_if_setup_not_called():
    gpio = MagicMock()
    gpio.input.side_effect = StopIteration  # escape hatch if guard is missing
    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio  # gpio available but setup() never called
    with pytest.raises(RuntimeError, match="setup"):
        h.wait_for_action()


def test_bounce_shorter_than_debounce_is_ignored(mocker):
    gpio = MagicMock()
    gpio.BCM = 11
    gpio.IN = 1
    gpio.PUD_UP = 22
    # Pin reads LOW then HIGH (bounce) — never stays LOW after debounce sleep.
    # Third read raises StopIteration so the loop doesn't block indefinitely.
    gpio.input.side_effect = [0, 1, StopIteration]

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()

    mocker.patch("inksink.core.input.time.sleep")
    with pytest.raises(StopIteration):
        h.wait_for_action()

    # The action should NOT have returned on the bounce
    # (if it had, wait_for_action would have returned before StopIteration)


def test_wait_for_action_returns_btn5_for_gpio19(mocker):
    gpio = MagicMock()
    gpio.input.side_effect = [0, 0]  # LOW on poll, LOW after debounce → clean press

    h = InputHandler(pin_map={19: "btn_5"})
    h._gpio = gpio
    h.setup()

    mocker.patch("inksink.core.input.time.sleep")
    result = h.wait_for_action()
    assert result == "btn_5"


def test_clean_press_returns_action(mocker):
    gpio = MagicMock()
    gpio.input.side_effect = [0, 0]  # LOW on poll, LOW after debounce → clean press

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()

    mocker.patch("inksink.core.input.time.sleep")
    result = h.wait_for_action()
    assert result == "good"


def test_stop_event_already_set_returns_empty_string(mocker):
    gpio = MagicMock()
    gpio.input.return_value = 1  # no button pressed

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()
    mocker.patch("inksink.core.input.time.sleep")

    event = threading.Event()
    event.set()
    assert h.wait_for_action(stop_event=event) == ""


def test_stop_event_set_during_debounce_returns_empty_string(mocker):
    """If stop_event fires during the 50ms debounce sleep, return "" not the action."""
    gpio = MagicMock()
    # First read: LOW (pin pressed) — enters debounce path
    gpio.input.return_value = 0

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()

    event = threading.Event()

    sleep_calls = []

    def set_event_on_debounce_sleep(dur):
        sleep_calls.append(dur)
        if dur == 0.05:  # _DEBOUNCE_S
            event.set()

    mocker.patch(
        "inksink.core.input.time.sleep", side_effect=set_event_on_debounce_sleep
    )
    result = h.wait_for_action(stop_event=event)
    assert result == ""


def test_stop_event_set_during_poll_returns_empty_string(mocker):
    gpio = MagicMock()
    gpio.input.return_value = 1  # no button pressed

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()

    event = threading.Event()

    def set_event_on_second_sleep(_dur):
        event.set()

    mocker.patch("inksink.core.input.time.sleep", side_effect=set_event_on_second_sleep)
    assert h.wait_for_action(stop_event=event) == ""
