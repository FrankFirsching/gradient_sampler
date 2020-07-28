# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from . import operator
import bpy

bl_info = {
    "name" : "Gradient Sampler",
    "author" : "Frank Firsching",
    "version": (0, 1),
    "blender" : (2, 83, 0),
    "description" : "Sample gradients from anything on the screen",
    "location" : "Context menu of color ramp node",
    "warning" : "",
    "category" : "Node"
}

classes = (
    operator.StrokeOperator,
)

def menu_func(self, context):
    if context.space_data.type == 'NODE_EDITOR':
        if context.active_node != None and context.active_node.type == 'VALTORGB':
            layout = self.layout
            layout.separator()
            layout.operator(operator.StrokeOperator.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_context_menu.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.NODE_MT_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
