bl_info = {
    "name": "ASCII",
    "author": "XDRANDY",
    "version": (0,0,1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > ASCII Render",
    "description": "Render the active camera view of the current scene to ASCII art in txt file",
    "category": "Render",
}

if "render_ascii" in locals():
    import importlib
    importlib.reload(render_ascii)
    importlib.reload(ui_panel)
else:
    from . import render_ascii
    from . import ui_panel
def register():
    ui_panel.register()
def unregister():
    ui_panel.unregister()
if __name__ == "__main__":
    register()
