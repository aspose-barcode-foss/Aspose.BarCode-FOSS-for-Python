# Examples

Runnable scripts demonstrating the public API. Install the package first (from the
repository root: `pip install .`), then run any script:

```bash
python examples/quickstart.py
```

| Script | Shows |
| --- | --- |
| `quickstart.py` | Generate a Code 128 and a QR code, then save SVG and PNG |
| `all_symbologies.py` | Every supported symbology via its dedicated helper |
| `render_options.py` | Styling output with `RenderOptions` and a custom `Renderer` |
| `error_handling.py` | The typed exceptions raised on invalid input |

Scripts that write files produce `*.output.svg` / `*.output.png` next to the script;
those outputs are gitignored.
