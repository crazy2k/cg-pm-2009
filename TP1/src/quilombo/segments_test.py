import time
import operator
from random import randint

from core.scenes import LineSegment
from algorithms import bresenham, dda

MAX_X = 800
MAX_Y = 600

TOTAL_SEGMENTS = 20
ITERATIONS_PER_SEGMENT = 10000

def average(sequence):
    sum = 0
    for e in sequence:
        sum = sum + e

    return float(sum)/len(sequence)

if __name__ == "__main__":

    dull_function = lambda self, x, y: None

    times_seg1 = []
    times_seg2 = []
    
    for x in range(TOTAL_SEGMENTS):
        x1, y1 = randint(0, MAX_X), randint(0, MAX_Y)
        x2, y2 = randint(0, MAX_X), randint(0, MAX_Y)

        seg1 = LineSegment((x1, y1), (x2, y2), bresenham.draw_segment)
        seg2 = LineSegment((x1, y1), (x2, y2), dda.draw_segment)

        b_seg1 = time.time()
        for i in range(ITERATIONS_PER_SEGMENT):
            seg1.draw(dull_function)
        a_seg1 = time.time()

        times_seg1.append(a_seg1 - b_seg1)

        b_seg2 = time.time()
        for i in range(ITERATIONS_PER_SEGMENT):
            seg2.draw(dull_function)
        a_seg2 = time.time()

        times_seg2.append(a_seg2 - b_seg2)

    average_bresenham = average(times_seg1)
    average_dda = average(times_seg2)

    print "Brasenham: ", average_bresenham
    print "DDA: ", average_dda
