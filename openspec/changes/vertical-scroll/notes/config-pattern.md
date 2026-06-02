# Config: per-app override pattern already in Compositor

File: `src/inksink/core/ui/compositor.py`

The Compositor already reads per-app config overrides in `__init__`. Follow
the same pattern for `vertical_scroll_step`:

```python
# existing pattern (from __init__):
active = settings.get("_active_app", "")
app_cfg = settings.get("apps", {}).get(active, {})
display_sub = app_cfg.get("display", {})
self._double_vertical = display_sub.get("double_vertical_button_size", False)

# new — add alongside existing display_sub reads:
global_step = settings.get("display", {}).get("vertical_scroll_step", 50)
self._scroll_step = display_sub.get("vertical_scroll_step", global_step)
```

`_active_app` is injected into settings at startup — it's not a user config key.
