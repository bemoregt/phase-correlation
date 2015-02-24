'''
Created on Dec 19, 2012

@author: bxs003
'''

import math
from time import time
from ctypes import *
from array import array
from copy import copy

from PIL import Image

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.extensions import *

from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *

from fft2d import phase_corrleation

ESCAPE = 27
ENTER = 13

window = None

# Texture IDs
moon_tex_id = -1

up_key_held = False
down_key_held = False
left_key_held = False
right_key_held = False

cam_pos = [0.0, 0.0, 0.0]

cam_pos_list = []
imgs = []

def load_texture(texture_path):
    im = Image.open(texture_path)
    ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
        
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    return ix, iy, tex_id

def cleanup():
    glDeleteTextures(1, moon_tex_id)

def init_gl(width, height):
    global moon_tex_id
    w, h, moon_tex_id = load_texture("../../imgs/tex.png")
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    
    #glFrontFace(GL_CW)
    #glShadeModel(GL_SMOOTH)
    #glEnable(GL_LIGHTING)
    #glEnable(GL_LIGHT0)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
def resize_gl(Width, Height):
    if Height == 0:
        Height = 1

    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
def update_cam():
    global cam_pos, up_key_held, down_key_held
    
    if up_key_held:
        cam_pos[1] += 0.001
    if down_key_held:
        cam_pos[1] -= 0.001
    if right_key_held:
        cam_pos[0] += 0.001
    if left_key_held:
        cam_pos[0] -= 0.001
        
    ref_pt = [0.0, 0.0, 0.0]
    ref_pt[0] = cam_pos[0]
    ref_pt[1] = cam_pos[1]
    ref_pt[2] = cam_pos[2] + -1.0
        
    # cam_pos, ref_pt, up_vec
    gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2], ref_pt[0], ref_pt[1], ref_pt[2], 0.0, 1.0, 0.0)
    
def draw_gl():
    global moon_tex_id, cam_pos, up_key_held
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_cam()
    
    draw_scene()
    
    glutSwapBuffers()
    
def draw_scene():
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    
    #math.sin(time())
    glTranslate(0.0, 0.0, -2.0)
    draw_textured_rectangle(1.0, 1.0, moon_tex_id)
    
    glTranslate(0.0, -1.0, 0.0)
    draw_textured_rectangle(1.0, 1.0, moon_tex_id)
    
    glTranslate(-1.0, 0.0, 0.0)
    draw_textured_rectangle(1.0, 1.0, moon_tex_id)
    
    glTranslate(0.0, 1.0, 0.0)
    draw_textured_rectangle(1.0, 1.0, moon_tex_id)
    
    glPopMatrix()
    
def draw_textured_rectangle(w, h, tex_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    
    glBegin(GL_TRIANGLES)
    glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0, 0.0);
    glTexCoord2f(1.0, 0.0); glVertex3f(w, 0.0, 0.0);
    glTexCoord2f(1.0, 1.0); glVertex3f(w, h, 0.0);
    
    glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0, 0.0);
    glTexCoord2f(1.0, 1.0); glVertex3f(w, h, 0.0);
    glTexCoord2f(0.0, 1.0); glVertex3f(0.0, h, 0.0);
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    
def draw_map():
    pass

def render_to_fbo():
    global imgs, cam_pos
    
    width = 768
    height = 768
    
    fbo = -1
    depth_rb = -1
    color_tex = -1
    
    color_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, color_tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, None)
    
    fbo = glGenFramebuffersEXT(1)
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo)
    
    # Attach 2D texture to this FBO
    glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, color_tex, 0)
    
    depth_rb = glGenRenderbuffersEXT(1)
    glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, depth_rb)
    glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT24, width, height)
    
    # Attach depth buffer to FBO
    glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, depth_rb)
    
    # Does the GPU support current FBO configuration?
    status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
    assert(status == GL_FRAMEBUFFER_COMPLETE_EXT)
    
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo)
    resize_gl(width, height)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_cam()
    draw_scene()
    
    pixels = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    ft_img = Image.frombuffer("RGBA", (width, height), pixels, 'raw', "RGBA", 0, 1)
    
    # Bind 0, which means render to back buffer, as a result, fbo is unbound
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
    resize_gl(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    
    glDeleteTextures([color_tex])
    glDeleteRenderbuffersEXT(1, [depth_rb])
    glDeleteFramebuffersEXT(1, [fbo])
    
    if len(imgs) >= 2:
        imgs.pop(0)
        cam_pos_list.pop(0)
        
    imgs.append(ft_img)
    cam_pos_list.append(copy(cam_pos))
    
    if len(imgs) == 2:
        a = time()
        dx, dy = phase_corrleation(imgs[0], imgs[1])
        corr_time = (time() - a)*1000
        
        if dx > width/2:
            dx = dx - width
        
        if dy > height/2:
            dy = dy - height
            
        dx_cam = cam_pos_list[1][0] - cam_pos_list[0][0]
        dy_cam = cam_pos_list[1][1] - cam_pos_list[0][1]
            
        print dx, dy
        print dx_cam, dy_cam
        if dx_cam != 0.0:
            print 'dx_cam/dx' + str(dx_cam/dx)
            
        if dy_cam != 0.0:
            print 'dy_cam/dy' + str(dy_cam/dy)
            
        print corr_time

def key_pressed(key, x, y):
    global window
    
    if ord(key) == ESCAPE:
        sys.exit()
    elif ord(key) == ENTER:
        render_to_fbo()
        
def special_key_release(key, x, y):
    global up_key_held, down_key_held, right_key_held, left_key_held
    
    if key == GLUT_KEY_UP:
        up_key_held = False
    elif key == GLUT_KEY_DOWN:
        down_key_held = False
    elif key == GLUT_KEY_RIGHT:
        right_key_held = False
    elif key == GLUT_KEY_LEFT:
        left_key_held = False

def special_key_press(key, x, y):
    global up_key_held, down_key_held, right_key_held, left_key_held
    
    if key == GLUT_KEY_UP:
        up_key_held = True
    elif key == GLUT_KEY_DOWN:
        down_key_held = True
    elif key == GLUT_KEY_RIGHT:
        right_key_held = True
    elif key == GLUT_KEY_LEFT:
        left_key_held = True

def main():
    global window, moon_tex_id
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("GLwindow")
    glutDisplayFunc(draw_gl)
    glutIdleFunc(draw_gl)
    glutReshapeFunc(resize_gl)
    
    # Key Press Callbacks
    glutIgnoreKeyRepeat(1)
    glutKeyboardFunc(key_pressed)
    glutSpecialFunc(special_key_press)
    glutSpecialUpFunc(special_key_release)
    
    init_gl(640, 480)

    # Begin Main Loop
    glutMainLoop()

if __name__ == '__main__':
    print "Hit ESC key to quit."
    main()