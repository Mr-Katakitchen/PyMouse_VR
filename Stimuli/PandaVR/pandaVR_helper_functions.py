def get_bounds(model):
        # Model bounds
        bound_coordinates = dict()
        bound_coordinates['x0'] = model.getTightBounds()[0][0]
        bound_coordinates['y0'] = model.getTightBounds()[0][1]
        bound_coordinates['z0'] = model.getTightBounds()[0][2]
        bound_coordinates['x1'] = model.getTightBounds()[1][0]
        bound_coordinates['y1'] = model.getTightBounds()[1][1]
        bound_coordinates['z1'] = model.getTightBounds()[1][2]
        
        return bound_coordinates
    
def get_cond(curr_cond, cond_name, idx=0):
    return {k.split(cond_name, 1)[1]: v if type(v) is int or type(v) is float or type(v) is str else v[idx] #added string parameter
    for k, v in curr_cond.items() if k.startswith(cond_name)}
    
