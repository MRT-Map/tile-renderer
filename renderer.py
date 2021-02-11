import colorama



def render(plaList: dict, nodeList: dict, minZoom, maxZoom, maxZoomRange, **kwargs):
    tiles = kwargs['tiles'] if 'tiles' in kwargs.keys() else None # array of (z,x,y)