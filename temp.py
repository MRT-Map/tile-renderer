import sympy as sym
from typing import Union
import math
import renderer

def midpoint(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], o: Union[int, float], n=1, returnBoth=False):
        points = []
        for p in range(1, n+1):
            x3, y3 = (x1+p*(x2-x1)/(n+1),y1+p*(y2-y1)/(n+1))
            #x3, y3 = ((x1+x2)/2, (y1+y2)/2)
            xv, yv = sym.symbols('xv,yv')
            if x1 == x2:
                m1 = None
                m2 = 0
                eq1 = sym.Eq(yv,y3)
            elif y1 == y2:
                m1 = 0
                m2 = None
                eq1 = sym.Eq(xv,x3)
            else:
                m1 = (y2-y1)/(x2-x1)
                m2 = -1 / m1
                eq1 = sym.Eq(yv-y3,m2*(xv-x3))
            eq2 = sym.Eq(((yv-y3)**2 + (xv-x3)**2)**0.5,abs(o))
            results = sym.solve([eq1, eq2], (xv, yv)) if o != 0 else [(x3, y3), (x3, y3)]
            if returnBoth:
                rot = 90 if x1 == x2 else math.degrees(-math.atan(m1))
                points += [(results[0][0], results[0][1], rot), (results[1][0], results[1][1], rot)]
            #print(results)
            elif x1 == x2:
                if o < 0:
                    x4, y4 = results[0] if results[0][0] < results[1][0] else results[1]
                else:
                    x4, y4 = results[0] if results[0][0] > results[1][0] else results[1]
                rot = 90
                points.append((x4, y4, rot))
            else:
                if o < 0:
                    x4, y4 = results[0] if results[0][1] < results[1][1] else results[1]
                else:
                    x4, y4 = results[0] if results[0][1] > results[1][1] else results[1]
                rot = math.degrees(-math.atan(m1))
                points.append((x4, y4, rot))
        return points