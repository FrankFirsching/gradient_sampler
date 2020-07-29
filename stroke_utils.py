# Utility functions for stroke handling

def bbox(stroke):
    """ Returns a bounding box of given stroke (compatible with mss region 
        definition) """
    stroke_min_x=min(stroke, key=lambda x:x[0])[0]
    stroke_min_y=min(stroke, key=lambda x:x[1])[1]
    result = {
        "left": stroke_min_x,
        "top": stroke_min_y,
        "width": max(stroke, key=lambda x:x[0])[0]-stroke_min_x+1,
        "height": max(stroke, key=lambda x:x[1])[1]-stroke_min_y+1
    }
    return result

def transformed(stroke, factor_x, factor_y, offset_x, offset_y):
    """ Returns a moved the version of the stroke """
    return [(factor_x*x+offset_x, factor_y*y+offset_y) for x,y in stroke]

def line(a,b):
    """ Returns a list of points for a line between a and b """
    diff = (b[0]-a[0], b[1]-a[1])
    sample_idx = 0 if abs(diff[0])>abs(diff[1]) else 1
    calc_idx = (sample_idx+1)%2
    if diff[sample_idx] == 0:
        # The 2 points are the same, so we're done.
        return
    slope = float(diff[calc_idx])/float(diff[sample_idx])
    p = [float(a[0]), float(a[1])]
    if diff[sample_idx] < 0:
        while p[sample_idx]>b[sample_idx]:
            yield (int(p[0]), int(p[1]))
            p[sample_idx] -= 1
            p[calc_idx] -= slope
    else:
        while p[sample_idx]<b[sample_idx]:
            yield (int(p[0]), int(p[1]))
            p[sample_idx] += 1
            p[calc_idx] += slope

def connect(stroke):
    """ Returns a stroke with the sampled points connected through neighboring
        pixels """
    result = [p for i in range(1,len(stroke)) for p in line(stroke[i-1], stroke[i])]
    result.append(stroke[-1])
    return result