# -*- coding: utf-8 -*-
from __future__ import division, print_function

"""
based on: http://sukhbinder.wordpress.com/2013/11/28/binary-stl-file-reader-in-python-powered-by-numpy/
"""

__author__ = 'Alexander Weigl <alexander.weigl@student.kit.edu>'

from struct import unpack

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import *
from PyQt4.QtOpenGL import QGLWidget

from time import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np

import sys, os
import argparse

LIST_COUNTER = 1

class STLFile(object):
    def __init__(self, data):
        self.data = data
        num, m, n = data.shape
        assert m == 4 and n == 3
        self.program = None
        self.translate = None
        self.rotate = None
        self.wireframe = False

        #self._gen_list()

    def _gen_list(self):

        self.list_number = glGenLists(1)
        print("Making genlist %d" % self.list_number)

        glNewList(self.list_number, GL_COMPILE_AND_EXECUTE)
        self.draw_vertices()
        glEndList()

    def center(self):
        without_normals = self.data[:, 1:4, :]
        mean = np.mean(without_normals, axis=(0, 1))
        return mean

    #
    # def _compile(self):
    #     from StringIO import StringIO
    #
    #     program = StringIO()
    #     program.write("glBegin(GL_TRIANGLES);")
    #     num, m, n = self.data.shape
    #     for i in range(num):
    #         args = self.data[i, :, :].reshape(1, 12)
    #         t = tuple((float(x) for x in np.nditer(args)))
    #         program.write(
    #             "glNormal3f(%f,%f,%f);\nglVertex3f(%f,%f,%f);\nglVertex3f(%f,%f,%f);\nglVertex3f(%f,%f,%f);\n" % t)
    #
    #     program.write("glEnd();")
    #     self.program = program.getvalue()
    #     return self.program
    #
    #
    # def arrow(self, x1, y1, z1, x2, y2, z2, D):
    #     RADPERDEG = 0.0174533
    #     import math
    #
    #     x = x2 - x1
    #     y = y2 - y1
    #     z = z2 - z1
    #     L = math.sqrt(x * x + y * y + z * z)
    #
    #     glPushMatrix()
    #     glTranslated(x1, y1, z1)
    #
    #     if x != 0 and y != 0:
    #         glRotated(math.atan2(y, x) / RADPERDEG, 0., 0., 1.)
    #         glRotated(math.atan2(math.sqrt(x * x + y * y), z) / RADPERDEG, 0., 1., 0.)
    #     elif z < 0:
    #         glRotated(180, 1., 0., 0.)
    #
    #     glTranslatef(0, 0, L - 4 * D);
    #
    #     quadObj = gluNewQuadric();
    #     gluQuadricDrawStyle(quadObj, GLU_FILL);
    #     gluQuadricNormals(quadObj, GLU_SMOOTH);
    #     gluCylinder(quadObj, 2 * D, 0.0, 4 * D, 32, 1);
    #     gluDeleteQuadric(quadObj);
    #
    #     quadObj = gluNewQuadric();
    #     gluQuadricDrawStyle(quadObj, GLU_FILL);
    #     gluQuadricNormals(quadObj, GLU_SMOOTH);
    #     gluDisk(quadObj, 0.0, 2 * D, 32, 1);
    #     gluDeleteQuadric(quadObj);
    #
    #     glTranslatef(0, 0, -L + 4 * D);
    #
    #     quadObj = gluNewQuadric();
    #     gluQuadricDrawStyle(quadObj, GLU_FILL);
    #     gluQuadricNormals(quadObj, GLU_SMOOTH);
    #     gluCylinder(quadObj, D, D, L - 4 * D, 32, 1);
    #     gluDeleteQuadric(quadObj);
    #
    #     quadObj = gluNewQuadric();
    #     gluQuadricDrawStyle(quadObj, GLU_FILL);
    #     gluQuadricNormals(quadObj, GLU_SMOOTH);
    #     gluDisk(quadObj, 0.0, D, 32, 1);
    #     gluDeleteQuadric(quadObj);
    #
    #     glPopMatrix();
    #
    #
    # def draw_axes(self, length):
    #
    #     glPushMatrix()
    #     glTranslate(-10, -10, -10)
    #
    #     glColor3f(1, 0, 0)
    #     self.arrow(10, 10, 10,
    #                length, 0, 0, 1)
    #     glColor3f(0, 1, 0)
    #     self.arrow(10, 10, 10,
    #                0, length, 0, 1)
    #
    #     glColor3f(0, 0, 1)
    #     self.arrow(10, 10, 10,
    #                0, 0, length, 1)
    #     glPopMatrix()
    #
    #     glColor3f(1, 1, 1)


    def draw_axes(self, length):
        glBegin(GL_LINES);
        glColor3f(1, 0, 0)
        glVertex3d(0, 0, 0);
        glVertex3d(length, 0, 0);

        glColor3f(0, 1, 0)
        glVertex3d(0, 0, 0);
        glVertex3d(0, length, 0);

        glColor3f(0, 0, 1)
        glVertex3d(0, 0, 0);
        glVertex3d(0, 0, length);
        glEnd()
        glColor3f(1, 1, 1)


    def draw_vertices(self):
        glPushMatrix()
        if self.translate:
            glTranslatef(*self.translate)

        if self.rotate:
            glRotatef(*self.rotate)

        self.draw_axes(50)

        if self.wireframe:
            glBegin(GL_LINE_LOOP)
        else:
            glBegin(GL_TRIANGLES)

        num, m, n = self.data.shape
        for i in range(num):
            glNormal3f(self.data[i, 0, 0], self.data[i, 0, 1], self.data[i, 0, 2])
            glVertex3f(self.data[i, 1, 0], self.data[i, 1, 1], self.data[i, 1, 2])
            glVertex3f(self.data[i, 2, 0], self.data[i, 2, 1], self.data[i, 2, 2])
            glVertex3f(self.data[i, 3, 0], self.data[i, 3, 1], self.data[i, 3, 2])
        glEnd()

        glPopMatrix()


    def draw(self):
        glCallList(self.list_number)
        #self.draw_vertices()

def BinarySTL(fname):
    with open(fname) as fp:
        Header = fp.read(80)
        nn = fp.read(4)
        Numtri = unpack('i', nn)[0]

        record_dtype = np.dtype([
            ("vertices", np.float32, (4, 3)),
            ("attr", '<i2', (1,)),
        ])

        data = np.fromfile(fp, dtype=record_dtype, count=Numtri)
        vertices = data['vertices']
        return STLFile(data=vertices)


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


from itertools import imap


def TextSTL(fname):
    def as_float_vec(s):
        l = filter(lambda x: x != "", s.strip().split(" "))
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
                facet, normal, ni, nj, nk = filter(lambda x: x != "", line.split(" "))

                normals = [float(ni), float(nj), float(nk)]

                for outer in lines:
                    if outer.startswith("endloop"):
                        break

                    if outer.startswith('outer loop'):
                        package = [normals,
                                   as_float_vec(lines.next()),
                                   as_float_vec(lines.next()),
                                   as_float_vec(lines.next())]
                        triangles.append(package)

                line = lines.next()
                if not line.startswith('endfacet'):
                    print("ERROR: endfacet")
                    
    n = len(triangles)
    ary = np.empty((n, 4, 3))
    for i, t in enumerate(triangles):
        ary[i, :, :] = t
    return STLFile(ary)



class STLWidget(QGLWidget):
    def __init__(self, stlfile, parent=None):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(500, 500)

        if isinstance(stlfile, (list, tuple)):
            self.stl = stlfile
        else:
            self.stl = (stlfile, )
        self.timer = time()
        self.rotation = {'x': 0, 'y': 0, 'z': 0}
        self.scale = 1

    #solid model with a light / shading
    def initializeGL(self):
        QGLWidget.initializeGL(self)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.width(), self.height())
        #procedure gluPerspective(fovy, aspect, zNear, zFar : glDouble);
        gluPerspective(70, 1.0 * self.width() / self.height(), 0.1, 1000.0)
        gluLookAt(100, 100, 100,
                  0, 0, 0,
                  0, 1, 0)

        glMatrixMode(GL_MODELVIEW)

        # glShadeModel(GL_SMOOTH)
        # glClearColor(0.0, 0.0, 0.0, 0.0)
        # glClearDepth(1.0)
        glEnable(GL_CULL_FACE)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, GLfloat_4(1., 1., 0., 0.))
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))

        #glLightfv(GL_LIGHT0, GL_AMBIENT, GLfloat_4(0.0, 1.0, 0.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(1.0, 1.0, 1.0, 0.0));
        #glLightModelfv(GL_LIGHT_MODEL_AMBIENT, GLfloat_4(0.2, 0.2, 0.2, 1.0))

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        for s in self.stl:
            s._gen_list()

        # glMatrixMode(GL_MODELVIEW)

    def resizeGL(self, width, height):
        QGLWidget.resize(self, width, height)

        glViewport(0, 0, self.width(), self.height())
        #        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, 1.0 * self.width() / self.height(), 0.1, 1000.0)
        gluLookAt(100, 100, 100,
                  0, 0, 0,
                  0, 1, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def glDraw(self):
        QGLWidget.glDraw(self)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        #        glTranslatef(0.0, -26.0, -100.0)

        fps = time() - self.timer
        self.renderText(20, 20, "Test! %d" % fps)

        glRotatef(self.rotation['x'], 1, 0, 0)
        glRotatef(self.rotation['y'], 0, 1, 0)
        glRotatef(self.rotation['z'], 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)

        #
        # glBegin(GL_QUADS)
        # glVertex2f(0, 0)
        # glVertex2f(10, 0)
        # glVertex2f(10, 10)
        # glVertex2f(0, 10)
        # glEnd()

        self.timer = time()
        self.drawfloor()
        for s in self.stl:
            s.draw()

    def wheelEvent(self, event):
        assert isinstance(event, QWheelEvent)
        scrolled = event.delta() / 360.0 / 0.33 / 10
        self.scale += scrolled
        print(self.scale, scrolled)
        self.update()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        assert isinstance(event, QMouseEvent)
        speed = 0.5
        dx = speed * (event.x() - self.lastPos.x())
        dy = speed * (event.y() - self.lastPos.y())

        if event.buttons() & (Qt.LeftButton & Qt.RightButton):
            self.rotate('x', dy)
        elif event.buttons() & Qt.LeftButton:
            self.rotate('y', dy)
        elif event.buttons() & Qt.RightButton:
            self.rotate('z', dy)

        #self.translate(event.pos().x(), event.pos().y())
        lastPos = event.pos()

    def drawfloor(self):
        y   = -5
        step = 25
        count = 40

        import math
        s, e = int(- math.ceil(count/2)), int(math.floor(count/2))

        glPushMatrix()
        glBegin(GL_QUADS)
        for i in range(s,e):
            for j in range(s,e):
                if (i+j)%2==0:
                    glColor3f(1,1,1)
                else:
                    glColor3f(0.3,0.3,0.3)

                glVertex3f(i*step, y, j*step);
                glVertex3f(i*step, y, (j+1)*step);
                glVertex3f((i+1)*step, y, (j+1)*step);
                glVertex3f((i+1)*step, y, j*step);
        glEnd()
        glPopMatrix()

    # def translate(self, screenX, screenY):
    #
    #     z = glReadPixelsf(screenX, screenY, 1, 1, GL_DEPTH_COMPONENT)
    #
    #     x = screenX / self.width()
    #     y = screenY / self.height()
    #
    #
    #     vec = np.array([x, y, z, 1])
    #
    #     projection = glGetFloatv( GL_PROJECTION_MATRIX)
    #     print projection
    #     print vec
    #
    #     print projection / vec
    #     #center = inverseProjection * vec
    #     #print center

    def rotate(self, axes, value):
        self.rotation[axes] += value
        self.update()

    def set_rotate(self, axes, value):
        self.rotation[axes] += value


class STLFrame(QMainWindow):
    def __init__(self, stlfile):
        QMainWindow.__init__(self)

        widget = STLWidget(stlfile)
        self.setCentralWidget(widget)

def main():
    def _float_vec(s):
        return map(float, s.split(" "))

    stack = {'translate' : None, 'rotate': None, 'wireframe': False}

    def construct(fname, C):
        o = C(fname)
        for k,v in stack.items():
            if v:
                setattr(o, k, v)
        return o

    import sys

    models = []
    i = iter(sys.argv[1:])
    for a in i:
        if a == '-a':
            models.append(construct(i.next(), TextSTL))

        if a == '-b':
            models.append(construct(i.next(), BinarySTL))

        if a == '-t':
            stack['translate'] = _float_vec(i.next())

        if a == '-r':
            stack['rotate'] = _float_vec(i.next())

        if a == '-w':
            stack['wireframe'] = not stack['wireframe']

    app = QApplication(sys.argv)
    print(models)
    window = STLFrame(models)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
