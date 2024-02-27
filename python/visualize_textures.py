from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
import json
import sys

# Global variables for rotation
rot_x = 0.0
rot_y = 0.0
last_x = 0.0
last_y = 0, 0
scale = 0.1  # 1.0  # Initial scale
is_wireframe = False
current_index = 0
texture_offset = 0
texture_index = 0
items = 965

textures = []

# 965 - BFT turret?
# 975 -987 - BFT weapons?
# 991 - BFT tank tread covers?
# 1006-1039 - VTOL aircraft
# 1040 - 1053 - Helicopter
# 1063 - 1091      - BFT Tank turret?
# 1092 - Vehicle
# 1103 - Person


def loadTextures():
    global textures
    with open("textures.json", "r") as file:
        textureFiles = json.load(file)
    textures = glGenTextures(len(textureFiles))

    print("Loading " + str(len(textureFiles)) + " textures...")
    failed_texture_loads = 0
    for i, textureFile in enumerate(textureFiles):
        filename = "textures/" + textureFile + ".png"
        # Check if file exists first:
        if not os.path.exists(filename):
            print("File " + filename + " does not exist; using default red")
            failed_texture_loads += 1
            filename = "textures/notfound.png"

        image = Image.open(filename)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        ix = image.size[0]
        iy = image.size[1]
        image = np.array(list(image.getdata()), np.uint8)

        glBindTexture(GL_TEXTURE_2D, textures[i])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if image.shape[-1] == 4:  # Checking for RGBA
            imgFormat = GL_RGBA
        else:
            imgFormat = GL_RGB

        glTexImage2D(
            GL_TEXTURE_2D, 0, imgFormat, ix, iy, 0, imgFormat, GL_UNSIGNED_BYTE, image
        )
    print("Textures loaded.")
    if failed_texture_loads > 0:
        print("Failed to load " + str(failed_texture_loads) + " textures.")


def loadModel():
    global items
    with open("meshes.json", "r") as file:
        data = json.load(file)
    items = len(data)
    return data


def initGL(width, height):
    loadTextures()
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.5, 0.5, 0.5, 1.0)  # Set to a grey color, for example
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def drawModel(data):
    global texture_offset, texture_index
    item = data[current_index]
    vertices = item["vertices"]
    polygons = item["polygons"]
    for polygon in polygons:
        texture_index = texture_offset + polygon["material_index"]
        if texture_index >= len(textures):
            texture_index = len(textures) - 1

        if texture_index < 0:
            texture_index = 0

        glBindTexture(GL_TEXTURE_2D, textures[texture_index])
        glBegin(GL_POLYGON)  # Changed from GL_TRIANGLES for generality
        for idx, coord in zip(polygon["vertex_indices"], polygon["uv_coords"]):
            glTexCoord2f(coord["u"], coord["v"])
            vertex = vertices[idx]
            glVertex3f(vertex["x"], vertex["y"], vertex["z"])
        glEnd()


def drawScene():
    global rot_x, rot_y, scale, is_wireframe

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)
    glScalef(scale, scale, scale)  # Apply scaling
    glRotatef(rot_x, 1.0, 0.0, 0.0)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    if is_wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 0.0, 0.0)  # Set color to red
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor3f(1.0, 1.0, 1.0)

    data = loadModel()
    try:
        drawModel(data)
    except:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        print("Error drawing model")

    glutSwapBuffers()


def drawSimpleScene():
    global rot_x, rot_y, scale, is_wireframe

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)
    glScalef(scale, scale, scale)  # Apply scaling
    glRotatef(rot_x, 1.0, 0.0, 0.0)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    if is_wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 0.0, 0.0)  # Set color to red
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor3f(1.0, 1.0, 1.0)
        glBindTexture(GL_TEXTURE_2D, textures[0])

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(1.0, 1.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0, 1.0, 0.0)
    glEnd()

    glutSwapBuffers()


def mouseMove(x, y):
    global last_x, last_y, rot_x, rot_y
    dx, dy = x - last_x, y - last_y
    last_x, last_y = x, y
    rot_x += dy * 0.5
    rot_y += dx * 0.5
    glutPostRedisplay()


def mouseButton(button, state, x, y):
    global last_x, last_y, scale
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        last_x, last_y = x, y

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        global is_wireframe
        is_wireframe = not is_wireframe
        glutPostRedisplay()

    elif button == 3 or button == 4:  # Mouse wheel event
        if state == GLUT_UP:
            return  # GLUT_UP is not used here, just a safeguard
        if button == 3:  # Scroll up
            scale *= 1.1
        elif button == 4:  # Scroll down
            scale /= 1.1
        glutPostRedisplay()  # Request to redraw the scene with the new scale


def keyPress(key, x, y):
    global current_index, scale, items, texture_offset, texture_index
    if key == GLUT_KEY_LEFT:
        current_index = max(0, current_index - 1)  # Ensure index doesn't go below 0
        scale = 0.1
        glutPostRedisplay()  # Redraw with the new item
    elif key == GLUT_KEY_RIGHT:
        current_index = min(
            items - 1, current_index + 1
        )  # Ensure index doesn't exceed data length
        scale = 0.1
        glutPostRedisplay()  # Redraw with the new item
    elif key == GLUT_KEY_UP:
        if texture_index < len(textures) - 1:
            texture_offset += 1

        glutPostRedisplay()
    elif key == GLUT_KEY_DOWN:
        if texture_index > 0:
            texture_offset -= 1
        glutPostRedisplay()

    new_title = (
        "Recoil Map Object Viewer - Item "
        + str(current_index)
        + " of "
        + str(items)
        + " (texture index "
        + str(texture_index)
        + " of "
        + str(len(textures))
        + ")"
    )
    glutSetWindowTitle(new_title)


def main():
    print("Initializing...")
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Recoil Map Object Viewer")
    print("Initialized.")
    glutDisplayFunc(drawScene)
    glutMotionFunc(mouseMove)
    glutSpecialFunc(keyPress)

    glutMouseFunc(mouseButton)
    initGL(640, 480)
    glutMainLoop()
    print("Done.")


if __name__ == "__main__":
    main()
