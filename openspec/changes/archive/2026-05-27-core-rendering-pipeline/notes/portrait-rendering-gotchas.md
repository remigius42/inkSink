# Portrait Rendering Gotchas

## PIL rotation: `expand=True` is mandatory

The Waveshare driver always expects an 800×480 buffer. When rotating a
portrait image (480×800) by 90°, PIL's default `expand=False` keeps the
output at 480×800 — the wrong shape for the driver. `expand=True` swaps
the dimensions correctly:

```python
# WRONG — silently produces 480×800, driver receives wrong buffer
image.rotate(90)

# CORRECT — produces 800×480 after rotating a 480×800 portrait image
image.rotate(90, expand=True)
```

The unit test for this should assert the driver always receives exactly
800×480 regardless of input orientation.

## wkhtmltoimage at portrait dimensions

wkhtmltoimage's `--width` and `--height` flags set the viewport size, not
a crop. At `--width 480 --height 800` the tool renders a mobile-style
narrow viewport. Known behaviors to test:

- Long content overflows below 800px — wkhtmltoimage extends the canvas;
  the subsequent `img.resize((480, 800))` in the renderer crops it. Ensure
  CSS body height is fixed (`height: 100vh; overflow: hidden`) in templates
  to avoid content being silently cropped.
- The `body { width: 760px }` in the current template is wider than the
  480px portrait viewport — this must be parameterized (see task 1.2).
  At 480px, content width should be `440px` (480 − 2×20px padding).

## Cache key must include orientation

Two renders of the same HTML at different orientations must not collide.
The old key `(sha256(html), mode)` is wrong once orientation varies.
New key: `(sha256(html), mode, orientation)`. Forgetting this causes
portrait renders to return cached landscape images silently.
