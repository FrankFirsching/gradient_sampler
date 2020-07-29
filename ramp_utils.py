# A local color ramp module, because blender's own one only manages 32 entries

import sys

class ColorSample:
    """ Encapsulates all information we store for a single color ramp entry """
    
    def __init__(self, index, t, color):
        """ t is given as relative position in range [0..1].
            color is given as 8bit RGB 0..255. """
        self.index = index
        self.t = t
        self.color = srgb_to_linear((color[0]/255.0, color[1]/255.0, color[2]/255.0,1))
        self.weight = -1

def color_difference_sqr(c0,c1):
    """ Returns the square of the color difference """
    return (c1[0]-c0[0])**2+(c1[1]-c0[1])**2+(c1[2]-c0[2])**2

def color_lerp(c0,c1,t):
    """ Interpolate the 2 given colors """
    return [a*(1-t)+b*t for a,b in zip(c0,c1)]

def interpolate(s0,s1,t):
    """ Interpolate 2 color samples from a ramp """
    assert s0.t<=t
    assert s1.t>=t
    t_normalized = (t-s0.t)/(s1.t-s0.t)
    return color_lerp(s0.color, s1.color, t_normalized)

def update_weight(r, idx):
    """ Update the weight of given ramp entry """
    interpolated = interpolate(r[idx-1], r[idx+1], r[idx].t)
    r[idx].weight = color_difference_sqr(interpolated, r[idx].color)

def initialize_weights(r):
    """ Helper function initializing the weights """
    rLength = len(r)
    if rLength==0:
        return
    lastIdx = rLength-1
    for idx in range(rLength):
        if idx==0 or idx==lastIdx:
            # Initialize boundary weights
            r[idx].weight = sys.float_info.max
        else:
            # Update the internal weight
            update_weight(r, idx)

def resample(r, num_elements):
    """ Resample given color ramp using up to given number of elements """
    res = r[:]
    initialize_weights(res)
    weight_threshold = 10*sys.float_info.epsilon
    while True:
        min_idx = min(range(len(res)), key=lambda idx: res[idx].weight)
        if len(res)<num_elements:
            if res[min_idx].weight > weight_threshold:
                break
        del res[min_idx]
        if min_idx>1:
            # Only update the previous one, if that one isn't the first boundary
            update_weight(res,min_idx-1)
        if min_idx<len(res)-1:
            # Only update, if the element after the remove isn't the boundary
            update_weight(res,min_idx)
    return res


def srgb_to_linear_comp(x):
    """ Convert a single color component from sRGB to linear """
    a = 0.055
    return x * (1.0 / 12.92) if x <= 0.04045 else pow((x + a) * (1.0 / (1 + a)), 2.4)

def srgb_to_linear(c):
    """ Convert a color from sRGB to linear """
    return (srgb_to_linear_comp(c[0]),
            srgb_to_linear_comp(c[1]),
            srgb_to_linear_comp(c[2]),
            srgb_to_linear_comp(c[3]))
