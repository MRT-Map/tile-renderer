import colorama

def renderer(plaList: dict, nodeList: dict, **kwargs):
    tiles = kwargs['tiles'] if 'tiles' in kwargs.keys() else None # array of (z,x,y)