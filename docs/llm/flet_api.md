# Flet 0.80+ API Reference

This document covers the Flet API changes introduced in version 0.80.0 that affect Storyteller.

## Breaking Changes Summary

| Component | Old API | New API |
|-----------|---------|---------|
| Icon | `ft.Icon(name=ft.Icons.X)` | `ft.Icon(ft.Icons.X)` |
| Icon property | `icon.name = ft.Icons.X` | `icon.icon = ft.Icons.X` |
| Buttons | `text="Label"` | `content=ft.Text("Label")` |
| Dropdown | `on_change=handler` | `on_select=handler` |
| Tabs | `tabs=[ft.Tab(...)]` | `TabBar` + `TabBarView` structure |
| Alignment | `ft.alignment.center` | `ft.Alignment.CENTER` |
| Control.page | Returns `None` if unmounted | Raises `RuntimeError` |

## Icon

The `name` parameter was renamed to `icon` and is now positional.

```python
# Old API
icon = ft.Icon(name=ft.Icons.CHECK_CIRCLE, color="green", size=24)
icon.name = ft.Icons.ERROR  # Update icon

# New API
icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=24)
icon.icon = ft.Icons.ERROR  # Update icon
```

## Buttons (TextButton, ElevatedButton, OutlinedButton)

The `text` parameter was replaced with `content`, which accepts a Control.

```python
# Old API
ft.ElevatedButton(text="Click Me", icon=ft.Icons.ADD)
ft.TextButton(text="Cancel")
ft.OutlinedButton(text="Submit")

# New API
ft.ElevatedButton(content=ft.Text("Click Me"), icon=ft.Icons.ADD)
ft.TextButton(content=ft.Text("Cancel"))
ft.OutlinedButton(content=ft.Text("Submit"))
```

## Dropdown

The `on_change` event was renamed to `on_select`.

```python
# Old API
ft.Dropdown(
    label="Select Option",
    options=[...],
    on_change=handle_change,
)

# New API
ft.Dropdown(
    label="Select Option",
    options=[...],
    on_select=handle_change,
)
```

## Tabs

Tabs were completely restructured. Instead of a list of `Tab` objects with content, use `TabBar` + `TabBarView` inside a `Tabs` wrapper.

```python
# Old API
ft.Tabs(
    selected_index=0,
    tabs=[
        ft.Tab(text="Tab 1", icon=ft.Icons.HOME, content=view1),
        ft.Tab(text="Tab 2", icon=ft.Icons.SETTINGS, content=view2),
    ],
    on_change=handle_change,
)

# New API
ft.Tabs(
    length=2,  # Required: must match number of tabs
    selected_index=0,
    on_change=handle_change,
    content=ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.TabBar(
                tabs=[
                    ft.Tab(label="Tab 1", icon=ft.Icons.HOME),
                    ft.Tab(label="Tab 2", icon=ft.Icons.SETTINGS),
                ],
            ),
            ft.TabBarView(
                expand=True,
                controls=[
                    view1,
                    view2,
                ],
            ),
        ],
    ),
)
```

Key changes:
- `Tabs` requires `length` parameter matching tab count
- `Tabs` takes a single `content` (typically a Column)
- Tab headers go in `TabBar.tabs`
- Tab content goes in `TabBarView.controls`
- `Tab.text` renamed to `Tab.label`
- `Tab.content` removed (content now in `TabBarView`)

## Alignment

Alignment constants moved from lowercase module to uppercase class attributes.

```python
# Old API
container.alignment = ft.alignment.center
container.alignment = ft.alignment.top_left

# New API
container.alignment = ft.Alignment.CENTER
container.alignment = ft.Alignment.TOP_LEFT
```

Available alignments:
- `ft.Alignment.TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`
- `ft.Alignment.CENTER_LEFT`, `CENTER`, `CENTER_RIGHT`
- `ft.Alignment.BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`

## Control.page Property

Accessing `.page` on an unmounted control now raises `RuntimeError` instead of returning `None`.

```python
# Old API
if self.page:
    self.update()

# New API - Option 1: Try/except wrapper
def _safe_update(func):
    from functools import wraps
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError:
            pass  # Control not mounted
    return wrapper

@_safe_update
def my_method(self):
    if self.page:
        self.update()

# New API - Option 2: Inline try/except
try:
    if self.page:
        self.update()
except RuntimeError:
    pass  # Control not mounted yet
```

## Other Changes

### Color Constants

```python
# Old API
ft.Colors.BLACK54
ft.Colors.WHITE70

# New API
ft.Colors.BLACK_54
ft.Colors.WHITE_70
```

### Method Renames

```python
# copy_with() -> copy()
new_control = control.copy()
```

### Image Source

Image sources consolidated into single `src` property:

```python
# Old API
ft.Image(src="url")
ft.Image(src_base64="base64data")

# New API
ft.Image(src="url")
ft.Image(src="base64data")  # Automatically detected
```

## Version Check

```python
import flet as ft
print(ft.__version__)  # Should be 0.80.0 or higher
```
