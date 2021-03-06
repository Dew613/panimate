import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """

frames = 1
basename = "unnamed"

def first_pass( commands ):
    global frames
    global basename
    f = 0
    b = 0
    v = 0
    for command in commands:
        if command[0] == 'frames':
            f = 1
            frames = command[1]
        if command[0] == 'basename':
            b = 1
            basename = command[1]
        if command[0] == 'vary':
            v = 1
    if (f == 0) and (v == 1):
        print "Error: Vary was found but frames was not"
        exit()
    if (f == 1) and (b == 0):
        print "Warning: basename not found. Setting pic name to unnamed"



"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs = []
    for i in range(num_frames):
        knobs.append({}) 

    for command in commands:
        if command[0] == 'vary':
            if command[2] >= command[3] or command[3] >= num_frames:
                print("Invalid range for " + command[1])
                exit()
            val_start = command[4]*1.0
            val_end = command[5]
            fr_start = command[2]
            fr_end = command[3]
            inc = (val_end-val_start)/(fr_end-fr_start)
            count = val_start
            for i in range(fr_start, fr_end + 1):
                if command[1] in knobs[i]:
                    print( command[1] + "has overlapping frames" )
                    exit(1)

                knobs[i][command[1]] = count
                count += inc
                #print "count:" + str(count)
    return knobs


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    first_pass(commands)
    knobs = second_pass(commands, frames)

    for frame in range(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []    
        step = 0.1
        for command in commands:
            print command
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                try:
                    i = knobs[frame][args[3]]
                    tmp = make_translate(args[0]*i, args[1]*i, args[2]*i)
                except:
                    tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                try:
                    i = knobs[frame][args[3]]
                    tmp = make_scale(args[0]*i,args[1]*i, args[2]*i)
                except:
                    tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                try:
                    theta*=knobs[frame][args[2]]
                except:
                    theta = theta 
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'set':
                if args[0] in knobs[frame]:
                    knob[args[0]] = float(args[0])
            elif c == 'set_knobs':
                for x in knobs[frame]:
                    knobs[frame][x] = float(args[0])
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        picname = "anim/" +basename+ "%03d"%frame
        save_ppm(screen, picname)
        clear_screen(screen)
    make_animation(basename)
