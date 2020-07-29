import bpy
from . import mss
from . import ramp_utils
from . import stroke_utils

# An operator, that allows to draw a stroke, which gets sampled into the
# color ramp.
class StrokeOperator(bpy.types.Operator):
    """Paint a stroke to sample a gradient"""
    bl_idname = "wm.gradient_sampler"
    bl_label = "Gradient Sampler"
    bl_options = {'BLOCKING'}

    def __init__(self):
        """ Constructor """
        self._left_mouse_pressed = False
        self._right_mouse_pressed = False
        self._lmb_stroke = []
        self._rmb_stroke = []
    
    def modal(self, context, event):
        """ Callback, if some event was happening """

        if event.type == 'MOUSEMOVE':
            # Convert from local blender's window coordinates to some sort of
            # global screen coordinates. Also see function __create_gradient for
            # further coordinate transformations.
            x = context.window.x+event.mouse_x
            y = context.window.y+event.mouse_y
            if self._left_mouse_pressed:
                self._lmb_stroke.append((x, y))
            if self._right_mouse_pressed:
                self._rmb_stroke.append((x, y))
        elif event.type == 'LEFTMOUSE':
            self._left_mouse_pressed = (event.value=="PRESS")
            if self.__finish_stroke(context):
                context.window.cursor_modal_restore()
                return {'FINISHED'}
        elif event.type == 'RIGHTMOUSE':
            self._right_mouse_pressed = (event.value=="PRESS")
            if self.__finish_stroke(context):
                context.window.cursor_modal_restore()
                return {'FINISHED'}
        elif event.type == 'ESC':
            context.window.cursor_modal_restore()
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if context.space_data.type == 'NODE_EDITOR':
            if context.active_node == None or context.active_node.type != 'VALTORGB':
                self.report({'ERROR'}, "A color ramp node needs to be selected.")
                return {'CANCELLED'}
            context.window_manager.modal_handler_add(self)
            context.window.cursor_modal_set('EYEDROPPER')
            return {'RUNNING_MODAL'}
        else:
            self.report({'ERROR'}, "Only works in a node editor.")
            return {'CANCELLED'}

    def __finish_stroke(self, context):
        """ Returns True, if the stroke was finished, otherwise False """
        if not self._left_mouse_pressed and not self._right_mouse_pressed:
            # Get the shortest stroke, that's not empty
            stroke = self._lmb_stroke if len(self._lmb_stroke)<len(self._rmb_stroke) else self._rmb_stroke
            if stroke==[]:
                stroke = self._lmb_stroke if self._rmb_stroke==[] else self._rmb_stroke
            self.__create_gradient(stroke, context.active_node)
            return True
        else:
            return False

    def __create_gradient(self, stroke, gradient_node):
        """ Given a stroke, creates a blender gradient inside the given color
            ramp node """
        # Reinitialize the screenshotter, in case monitor configuration changed
        sct = mss.mss()
        # Blender is managing a bottom up coordinate system, so we need to
        # subtract the stroke's coordinates from the overall height
        all_monitors = sct.monitors[0]
        stroke_offset = all_monitors['height']
        stroke = stroke_utils.transformed(stroke, 1, -1, 0, stroke_offset)
        # Optimize the region to capture by the bounding box of the stroke
        optimized_region = stroke_utils.bbox(stroke)
        sct_img = sct.grab(optimized_region)
        # Readapt the stroke to the smaller captured region
        stroke = stroke_utils.transformed(stroke, 1, 1,
                                          -optimized_region['left'],
                                          -optimized_region['top'])
        stroke = stroke_utils.connect(stroke)
        # Sample the screen shot
        stroke_len = len(stroke)
        ramp = []
        for idx,p in enumerate(stroke):
            ramp.append(ramp_utils.ColorSample(idx, float(idx)/(stroke_len-1),
                        sct_img.pixel(p[0], p[1])))
        # Blender has a limit of max. 32 color ramp entries
        ramp = ramp_utils.resample(ramp, 32)
        # Initialize the color ramp node
        ramp_elements = gradient_node.color_ramp.elements
        while len(ramp_elements)>1:
            ramp_elements.remove(ramp_elements[0])
        # Copy over the resampled gradient to the node
        for index,sample in enumerate(ramp):
            pixel = sample.color
            if index>0:
                ramp_elements.new(sample.t)
            else:
                ramp_elements[0].position = sample.t
            ramp_elements[index].color = pixel
        # DEBUG: Draw the stroke into the image and save:
        # self.__draw_debug_image(sct_img, stroke)
    
    def __draw_debug_image(self, sct_img, stroke):
        # Draw the stroke into the image and save
        myrgb=bytearray(sct_img.rgb)
        for x,y in stroke:
            myrgb[(y*sct_img.width+x)*3] = 0xff
        mss.tools.to_png(myrgb, sct_img.size, output='stroke.png')
