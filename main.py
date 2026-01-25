import pyopencl as cl
import array
from ctypes import c_float, c_int, c_double, c_uint, c_size_t
from OpenGL.GL import * #for future
import pygame
import pyopencl.cltypes as clt
import sys
import time
import math
import threading

#CONTROLS ARE WASD TO MOVE
#ARROW KEYS TO LOOK AROUND

plat = cl.get_platforms()[0]
dev  = plat.get_devices()[0]
ctx  = cl.Context([dev])
queue = cl.CommandQueue(ctx)


x = array.array('f')
y = array.array('f')
z = array.array('f')
rot = array.array('f')

posx = 0
posy = 0
posz = 0
posxrot = 0
posyrot = 0
poszrot = 0
screenwidth = 500
screenheight = 500
fovy = 90

def addVox(_x, _y, _z, _rot = 0):
    x.append(_x)
    y.append(_y)
    z.append(_z)
    rot.append(_rot)
#for i in range(30):
#    for j in range(30):
#        for m in range(30):
#            addVox(i, m, j+50)

addVox(1, 1, 1)
mf = cl.mem_flags

src = """
#define MYPI 3.1415926535897932384626433832795028841f
//I just copied a bunch from http://www.geom.uiuc.edu/~huberty/math5337/groupe/digits.html

inline float rad(float deg) {
    return deg * (MYPI / 180.0f);
}

inline float3 rot3d(float x, float y, float z, float xrot, float yrot, float zrot) {
    float xRot = xrot;          float yRot = yrot;          float zRot = zrot;
    float xrad = rad(xRot);     float yrad = rad(yRot);     float zrad = rad(zRot);
    float xcos = cos(xrad);     float xsin = sin(xrad); 
    float ycos = cos(yrad);     float ysin = sin(yrad);
    float zcos = cos(zrad);     float zsin = sin(zrad);

    //{ycos*xcos, zsin*ysin*xcos-zcos*xsin, zcos*ysin*xcos+zsin*xsin},
    //{ycos*xsin, zsin*ysin*xsin+zcos*xcos, zcos*ysin*xsin-zsin*xcos},
    //{-ysin, zsin*ycos, zcos*ycos}

    float3 newpoint;
    newpoint.x = x*ycos*xcos  +  y*(zsin*ysin*xcos-zcos*xsin)+  z*(zcos*ysin*xcos+zsin*xsin);
    newpoint.y = x*ycos*xsin  +  y*(zsin*ysin*xsin+zcos*xcos)+  z*(zcos*ysin*xsin-zsin*xcos);
    newpoint.z = -x*ysin      +  y*zsin*ycos                 +  z*zcos*ycos;
    return newpoint;
}

inline float3 newrot3d(float x, float y, float z, float xrot, float yrot, float zrot) {
    float xrad = rad(xrot);     float yrad = rad(yrot); //float zrad = rad(zrot);
    float cy = cos(yrad), sy = sin(yrad);
    float cx = cos(xrad), sx = sin(xrad);

    // yaw (y)
    float x1 =  x*cy + z*sy;
    float y1 =  y;
    float z1 = -x*sy + z*cy;

    // pitch (x)
    float x2 = x1;
    float y2 = y1*cx - z1*sx;
    float z2 = y1*sx + z1*cx;

    float3 newpoint;
    newpoint.x = x2;
    newpoint.y = y2;
    newpoint.z = z2;
    return newpoint;
}
__kernel void add_vec(
    __global const float *x,
    __global const float *y,
    __global const float *z,
    __global const float *rot,
    __global float *out,
    const int out_data_count,
    const float screen_w,
    const float screen_h,
    const float fov_y,
    const float cam_x,
    const float cam_y,
    const float cam_z,
    const float cam_rot_x,
    const float cam_rot_y,
    const float cam_rot_z
) {
    int gid = get_global_id(0);
    
    float cx = screen_w/2;
    float cy = screen_h/2;


    float radians = fov_y * (MYPI / 180.0f);
    float tan_calc = tan(radians / 2);
    float focal_len = cx / tan_calc;


    float xx = x[gid];
    float yy = y[gid];
    float zz = z[gid];

    // 8 points in a tri (triangle for those who are new) 3 values in a point (x, y, and z)
    float tris[8][3];

    float points[8][2];
    
    tris[0][0] = xx;         tris[0][1] = yy;         tris[0][2] = zz;
    tris[1][0] = xx + 1;     tris[1][1] = yy + 1;     tris[1][2] = zz;
    tris[2][0] = xx + 1;     tris[2][1] = yy;         tris[2][2] = zz;
    tris[3][0] = xx;         tris[3][1] = yy + 1;     tris[3][2] = zz;
    tris[4][0] = xx;         tris[4][1] = yy;         tris[4][2] = zz + 1;
    tris[5][0] = xx + 1;     tris[5][1] = yy + 1;     tris[5][2] = zz + 1;
    tris[6][0] = xx;         tris[6][1] = yy + 1;     tris[6][2] = zz + 1;
    tris[7][0] = xx + 1;     tris[7][1] = yy;         tris[7][2] = zz + 1;
    
    int dissapear = 8; //if this num gets to 0 then dont render it later
    for(int i = 0; i < 8; i++) {
        // I need to add local rotations here
        //if (rot[gid] != 0) {
        //  rotate(tri)
        //}
        //something like this where rotate will rotate on all 3 axis. Maybe use quaternion?

        tris[i][0] -= cam_x;
        tris[i][1] -= cam_y;
        tris[i][2] -= cam_z;



        float3 rotated_point3 = newrot3d(tris[i][0], tris[i][1], tris[i][2], cam_rot_x, cam_rot_y, cam_rot_z);
        tris[i][0] = rotated_point3.x;
        tris[i][1] = rotated_point3.y;
        tris[i][2] = rotated_point3.z;

        //now rotate after changing to world position rather than local position
        //skip for now just to get working

        if(tris[i][2] <= 0) {
            dissapear -=1;
            tris[i][2] = 0.1; //so we dont divide by 0 in a sec
        }
        points[i][0] = cx + focal_len * (tris[i][0] / tris[i][2]);
        if(points[i][0] > screen_w*2) { points[i][0] = screen_w*2; }
        if(points[i][0] < -screen_w) { points[i][0] = -screen_w; }
        points[i][1] = cy + focal_len * (tris[i][1] / tris[i][2]);
        if(points[i][1] > screen_h*2) { points[i][1] = screen_h*2; }
        if(points[i][1] < -screen_h) { points[i][1] = -screen_h; }

    }
    // I need to create a rotation function here now and apply it to everything

    int out_position = gid*16;
    int o = out_position;
    if (dissapear <= 0) {
        for(int i = 0; i < 16; i++) {
            out[o + i] = -1;
        }// just check to see if each rectangle is all -1 and dont draw if it is

        return;
    }

    out[o] =    points[0][0]; out[o+1] = points[0][1];
    out[o+2] =  points[1][0]; out[o+3] = points[1][1];
    out[o+4] =  points[2][0]; out[o+5] = points[2][1];
    out[o+6] =  points[3][0]; out[o+7] = points[3][1];
    out[o+8] =  points[4][0]; out[o+9] = points[4][1];
    out[o+10] = points[5][0]; out[o+11] = points[5][1];
    out[o+12] = points[6][0]; out[o+13] = points[6][1];
    out[o+14] = points[7][0]; out[o+15] = points[7][1];
}
"""


data_size = 16

prg = cl.Program(ctx, src).build()

xb = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=x)
yb = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=y)
zb = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=z)
rotb = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=rot)
n = len(x)
out = array.array('f', [0.0]*(n*data_size))
outb = cl.Buffer(ctx, mf.WRITE_ONLY, out.buffer_info()[1] * out.itemsize)
kern_add_vec = cl.Kernel(prg, 'add_vec')




def doCalc():

    
    out = array.array('f', [0.0]*(n*data_size))

    
    kern_add_vec(queue, (n,), None,
        xb, yb, zb, rotb, outb,
        clt.int(data_size),
        clt.float(screenwidth), clt.float(screenheight), clt.float(fovy),
        clt.float(posx), clt.float(posy), clt.float(posz),
        clt.float(posxrot), clt.float(posyrot), clt.float(poszrot)
    )
    
    cl.enqueue_copy(queue, out, outb).wait()

    out = out.tolist()


    
    return out  



o = doCalc()


screen = pygame.display.set_mode((screenwidth, screenheight))
pygame.display.set_caption("test")


white = (255, 255, 255)
blue = (0, 0, 255)

running = True
starting_time = time.time()
yspd = 0
spdmult = 0.5
rotmult = 2
frames = 0
frame_time = time.time()
clock = pygame.time.Clock()

kernal_time = 0
draw_time = 0
w, a, s, d, space, lshift = False, False, False, False, False, False
up, down, left, right = False, False, False, False

last_time = time.perf_counter()
game_time = 1/60

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_w:
                w = True
            if event.key == pygame.K_s:
                s = True
            if event.key == pygame.K_d:
                d = True
            if event.key == pygame.K_a:
                a = True
            if event.key == pygame.K_SPACE:
                space = True
            if event.key == pygame.K_LSHIFT:
                lshift = True
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                w = False
            if event.key == pygame.K_s:
                s = False
            if event.key == pygame.K_d:
                d = False
            if event.key == pygame.K_a:
                a = False
            if event.key == pygame.K_SPACE:
                space = False
            if event.key == pygame.K_LSHIFT:
                lshift = False
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False
    rad = math.radians(posyrot)
    cos = math.cos(rad) *spdmult
    sin = math.sin(rad) *spdmult
    
    current_time = time.perf_counter()
    if current_time - last_time > game_time:
        last_time = current_time
        fb = w-s
        lr = d-a
        ud = space-lshift
        zspd = cos * fb + sin * lr
        xspd = cos * lr - sin * fb
        yspd = -ud * spdmult
        posx+=xspd
        posy+=yspd
        posz+=zspd

        posyrot+= (left-right) * rotmult
        posxrot-= (up-down) * rotmult

    ctime = time.time()
    o = doCalc()
    kernal_time += time.time() - ctime

    ctime = time.time()
    screen.fill(white)

    #getFromList
    def gfl(l, pos, ind):
        #print((l[pos + ind*2], l[pos + ind*2 + 1]))
        return (l[pos + ind*2], l[pos + ind*2 + 1])
    
    def drawPoly(_screen, _col, _pts, backfaceCulling = True, cull_ind1 = 0, cull_ind2 = 1, cull_ind3 = 2):
        if backfaceCulling:
            ax = _pts[cull_ind1][0]; ay = _pts[cull_ind1][1]
            bx = _pts[cull_ind2][0]; by = _pts[cull_ind2][1]
            cx = _pts[cull_ind3][0]; cy = _pts[cull_ind3][1]
            cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
            if(cross < 0):
                return
        pygame.draw.polygon(_screen, _col, _pts, 0)

    for i in range(int(len(o)/16)):
        pos = i * 16
        p0 = gfl(o, pos, 0)
        if(p0[0] == -1):
            continue
        p1 = gfl(o, pos, 1)
        p2 = gfl(o, pos, 2)
        p3 = gfl(o, pos, 3)
        p4 = gfl(o, pos, 4)
        p5 = gfl(o, pos, 5)
        p6 = gfl(o, pos, 6)
        p7 = gfl(o, pos, 7)
        do_backface_culling = True
        drawPoly(screen, blue, [p0,  p2, p1,p3],    do_backface_culling, 0, 1, 3)#front #0 1 3 for backface culling
        drawPoly(screen, blue, [p4,  p6, p5, p7],   do_backface_culling, 0, 1, 3)#back # 4 6 7 for backface culling
        drawPoly(screen, blue, [p7, p2, p1, p5],    do_backface_culling, 0, 3, 2)#right # 7 5 1 for backface culling
        drawPoly(screen, blue, [p0, p3, p6, p4],    do_backface_culling, 0, 1, 3)#left # 0 3 4 for backface culling
        drawPoly(screen, blue, [p3, p1, p5, p6],    do_backface_culling, 0, 1, 3)#bottom # 3 1 6 for backface culling
        drawPoly(screen, blue, [p4, p7, p2, p0],    do_backface_culling, 0, 2, 3)#top # 4 2 0 for backface culling
    pygame.display.flip()
    draw_time += time.time() - ctime
    #print("Time to draw: " + str(time.time()-ctime) + " seconds")

    ctime = time.time()
    frames+=1
    if(ctime - frame_time >= 1):
        print(f"fps: {frames}\nkernal time per second: {kernal_time}\ndraw time per second: {draw_time}")
        frames = 0
        frame_time = ctime
        kernal_time = 0
        draw_time = 0


    clock.tick(1000)

pygame.quit()
sys.exit()