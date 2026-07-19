import os
import bpy
from bpy.types import Operator, Panel
from bpy.props import IntProperty, StringProperty, BoolProperty
from .render_ascii import render as render_scene_to_ascii

ASCII_TEXT_NAME = "ascii_output.txt"
class ASCII_OT_render(Operator):
    bl_idname = "ascii_render.render"
    bl_label = "Render ASCII"
    bl_description = "Render the current scene (active camera view) to ASCII art"

    def execute(self, context):

        settings = context.scene.ascii_render_settings
        try:
            result = render_scene_to_ascii(context, settings.width, settings.height)
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        text_block = bpy.data.texts.get(ASCII_TEXT_NAME)
        if text_block is None:
            text_block = bpy.data.texts.new(ASCII_TEXT_NAME)
        text_block.clear()
        text_block.write(result)
        if settings.save_to_file:
            blend_dir = os.path.dirname(bpy.data.filepath) or os.path.expanduser("~")
            out_path = os.path.join(blend_dir, "ascii_render_output.txt")
            with open(out_path, 'w') as f:
                f.write(result)
            self.report({'INFO'}, f"ASCII rendered to '{ASCII_TEXT_NAME}' and saved to {out_path}")
        else:
            self.report({'INFO'}, f"ASCII rendered to text block '{ASCII_TEXT_NAME}'")

        return {'FINISHED'}


class ASCII_RenderSettings(bpy.types.PropertyGroup):

    width: IntProperty(name="Width", default=100, min=10, max=400)
    height: IntProperty(name="Height", default=50, min=10, max=400)
    save_to_file: BoolProperty(name="Also save .txt next to blend file", default=False)


class ASCII_PT_panel(Panel):

    bl_idname = "ASCII_PT_panel"
    bl_label = "ASCII Renderer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ASCII Renderer"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ascii_render_settings
        layout.prop(settings, "width")
        layout.prop(settings, "height")
        layout.prop(settings, "save_to_file")
        layout.operator(ASCII_OT_render.bl_idname, icon='CONSOLE')
        text_block = bpy.data.texts.get(ASCII_TEXT_NAME)
        if text_block is not None:
            layout.label(text=f"Output in Text Editor: {ASCII_TEXT_NAME}")
classes = (
    ASCII_RenderSettings,
    ASCII_OT_render,
    ASCII_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ascii_render_settings = bpy.props.PointerProperty(type=ASCII_RenderSettings)


def unregister():
    del bpy.types.Scene.ascii_render_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
