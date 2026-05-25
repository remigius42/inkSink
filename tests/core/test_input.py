import sys
from unittest.mock import MagicMock

import pytest

# Stub RPi.GPIO before importing input module
_gpio_stub = MagicMock()
sys.modules.setdefault("RPi", MagicMock(GPIO=_gpio_stub))
sys.modules.setdefault("RPi.GPIO", _gpio_stub)

from inksink.core.input import InputHandler  # noqa: E402


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


def test_default_mapping_show_answer_is_pin_12():
    h = InputHandler()
    assert h._pin_map[12] == "show_answer"


def test_default_mapping_has_all_six_buttons():
    h = InputHandler()
    actions = set(h._pin_map.values())
    assert actions == {"power", "show_answer", "again", "hard", "good", "easy"}


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


def test_clean_press_returns_action(mocker):
    gpio = MagicMock()
    gpio.input.side_effect = [0, 0]  # LOW on poll, LOW after debounce → clean press

    h = InputHandler(pin_map={19: "good"})
    h._gpio = gpio
    h.setup()

    mocker.patch("inksink.core.input.time.sleep")
    result = h.wait_for_action()
    assert result == "good"
