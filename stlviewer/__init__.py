# -*- coding: utf-8 -*-
"""

based on: http://sukhbinder.wordpress.com/2013/11/28/binary-stl-file-reader-in-python-powered-by-numpy/

"""

__author__ = 'Alexander Weigl'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from struct import unpack

class STLFile(object):
    def __init__(self, data):
        self.data = data
        num, m,n = data.shape
        assert m == 4 and n == 3

    def draw(self):
        glBegin(GL_TRIANGLES)
        num, m, n = self.data.shape
        for i in range(num):
            triangle = self.data[num,:,:]
            glNormal3f(*triangle[0,:])
            glVertex3f(*triangle[1,:])
            glVertex3f(*triangle[2,:])
            glVertex3f(*triangle[3,:])
        glEnd()



def BinarySTL(fname):
    with open(fname) as fp:
        Header = fp.read(80)
        nn = fp.read(4)
        Numtri = unpack('i', nn)[0]

        record_dtype = np.dtype([
            ("vertices", np.float32, (4,3)),
            ("attr", '<i2', (1,)),
        ])

        data = np.fromfile(fp, dtype=record_dtype, count=Numtri)
        vertices = data['vertices']
        return STLFile(data = vertices)

def _BinarySTL(fname):
    with open(fname) as fp:
        Header = fp.read(80)
        nn = fp.read(4)
        Numtri = unpack('i', nn)[0]
        #print nn
        record_dtype = np.dtype([
            ('normals', np.float32, (3,)),
            ('Vertex1', np.float32, (3,)),
            ('Vertex2', np.float32, (3,)),
            ('Vertex3', np.float32, (3,)),
            ('atttr', '<i2', (1,) )])

        data = np.fromfile(fp, dtype=record_dtype, count=Numtri)

        Normals = data['normals']
        Vertex1 = data['Vertex1']
        Vertex2 = data['Vertex2']
        Vertex3 = data['Vertex3']
        p = np.append(Vertex1, Vertex2, axis=0)
        p = np.append(p, Vertex3, axis=0)  #list(v1)
        Points = np.array(list(set(tuple(p1) for p1 in p)))

    return Header, Points, Normals, Vertex1, Vertex2, Vertex3

from itertools import  imap

def TextSTL(fname):
    def as_float_vec(s):
        l = filter(lambda x:x != "", s.strip().split(" "))
        return map(float, l[1:])

    triangles = []
    with open(fname) as fp:
        lines = imap(lambda x: x.strip(), fp.readlines())

        line = lines.next()
        if line.startswith("solid"):
            solid, name = line.split(" ")
        else:
            raise EOFError("no solid found")

        for line in lines:
            if line == "":
                continue

            if line.startswith('endsolid'):
                break

            if line.startswith('facet'):
                facet, normal, ni, nj, nk = filter(lambda x: x!="", line.split(" "))

                normals = [float(ni), float(nj), float(nk)]

                for outer in lines:
                    if outer.startswith("endloop"):
                        break

                    if outer.startswith('outer loop'):
                        package = [  normals,
                                as_float_vec(lines.next()),
                                as_float_vec(lines.next()),
                                as_float_vec(lines.next()) ]
                        triangles.append(package)
                        
                line = lines.next()
                if not line.startswith('endfacet'):
                    print "ERROR: endfacet"

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtOpenGL import *

class STLWidget(QGLWidget):
    def __init__(self, stlfile, parent = None):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(500,500)

        if isinstance(stlfile, (list, tuple)):
            self.stl = stlfile
        else:
            self.stl = (stlfile, )

    #solid model with a light / shading
    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))
        glMatrixMode(GL_MODELVIEW)

        # glShadeModel(GL_SMOOTH)
        # glClearColor(0.0, 0.0, 0.0, 0.0)
        # glClearDepth(1.0)
        # glEnable(GL_DEPTH_TEST)
        # glShadeModel(GL_SMOOTH)
        # glDepthFunc(GL_LEQUAL)
        # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        # glEnable(GL_COLOR_MATERIAL)
        # glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)
        # glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))
        # glMatrixMode(GL_MODELVIEW)

    def resizeGL(self,width, height):
        if height==0:
            height=1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0*width/height, 0.1, 100.0)
        #gluLookAt(0.0,0.0,45.0,0,0,0,0,40.0,0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0,-26.0, -100.0)

        for s in self.stl:
            s.draw()


class STLFrame(QMainWindow):
    def __init__(self, stlfile):
        QMainWindow.__init__(self)

        widget = STLWidget(stlfile)
        self.setCentralWidget(widget)



if __name__ == '__main__':
    # binary
    fname = "porsche.stl"
    porsche = BinarySTL(fname)

    fname = "bottle.stl"
    bottle = TextSTL(fname)

    import sys
    app = QApplication(sys.argv)
    window = STLFrame(porsche)
    window.show()
    app.exec_()