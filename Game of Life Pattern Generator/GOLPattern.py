import cv2
import numpy as np
import imutils
import sys

# Set Image Parameters Such as Image Width & Height
image_width = 1000
image_height = 1000

# Set Grid Parameters Such as Gridth Width
gridth_width = 20

# Generate Grid Image
grid_image = np.zeros((image_width, image_height))
blank_image = np.zeros((image_width, image_height))

counter_width = 0
counter_height = 0

while counter_width <= image_width:
    cv2.line(grid_image, (counter_width, 0), (counter_width, image_height), (255, 255, 255))
    counter_width+=gridth_width

while counter_height <= image_height:
    cv2.line(grid_image, (0, counter_height), (image_width, counter_height), (255, 255, 255))
    counter_height+=gridth_width

# Process Image to Segment Grids
global inv
ret, inv = cv2.threshold(grid_image, 127, 255, cv2.THRESH_BINARY_INV)

# Find Contours
inv = cv2.erode(inv, np.ones((5, 5)))
contours = cv2.findContours(inv.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours)

# Function to Get Initial Grid Pattern from User
str = ""
cv2.namedWindow('Select Cells to Initialize Grid & Press Esc')

def fill_box(event,x,y,flags,param):
    global mouseX,mouseY    
    if event == cv2.EVENT_LBUTTONDOWN:
        
        for contour in contours[::-1]:
            if cv2.pointPolygonTest(contour, (x, y), True) >0:
                cv2.fillPoly(inv, pts=[contour], color=(0,0,0))
    
        mouseX,mouseY = x,y

cv2.setMouseCallback('Select Cells to Initialize Grid & Press Esc',fill_box)

while True:
    c = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
    
    while(1):
        cv2.imshow('Select Cells to Initialize Grid & Press Esc', inv)
        
        k = cv2.waitKey(51) & 0xFF
        if k == 27:
            break
    
    if c == '\n':
        break
    str += c

# Get Cell Status Whether Live or Dead
def get_status(inv, anchor_row_idx, anchor_col_idx):
        
    contour_idx = int(anchor_row_idx*(image_width/gridth_width) + anchor_col_idx)
    
    avg_gray = int(np.average(inv[contours[::-1][contour_idx][0][0][1]:contours[::-1][contour_idx][1][0][1],contours[::-1][contour_idx][0][0][0]:contours[::-1][contour_idx][3][0][0]]))
    
    is_live = 0
    if avg_gray==0:
        is_live = 1    

    return is_live

cv2.imshow("Game of Life Pattern", inv)

# Generate Game of Life Pattern
while(True):
    
    pattern = np.copy(inv)
    for row_index in range(1, int(image_height/gridth_width)-1):
        for col_index in range(1, int(image_width/gridth_width)-1):

            # Get Neighbouring Indices
            top_left_row, top_left_col   = row_index-1, col_index-1
            top_row, top_col             = row_index-1, col_index
            top_right_row, top_right_col = row_index-1, col_index+1
            left_row, left_col           = row_index  , col_index-1
            
            right_row, right_col               = row_index  , col_index+1
            bottom_left_row, bottom_left_col   = row_index+1, col_index-1
            bottom_row, bottom_col             = row_index+1, col_index
            bottom_right_row, bottom_right_col = row_index+1, col_index+1

            # Count the Number of Live Cells
            alive_neighbours = get_status(inv, top_left_row, top_left_col) +  get_status(inv, top_row, top_col)    + get_status(inv, top_right_row, top_right_col)
            alive_neighbours+= get_status(inv, left_row, left_col)         + get_status(inv, right_row, right_col) + get_status(inv, bottom_left_row, bottom_left_col)
            alive_neighbours+= get_status(inv, bottom_row, bottom_col)     + get_status(inv, bottom_right_row, bottom_right_col)

            # If Live Cell
            if get_status(inv, row_index, col_index)==1:
                if alive_neighbours<2 or alive_neighbours>3:
                    cv2.fillPoly(pattern, pts=[contours[::-1][row_index*int(image_width/gridth_width)+col_index]], color=(255, 255, 255))

            else:
                if alive_neighbours==3:
                    cv2.fillPoly(pattern, pts=[contours[::-1][row_index*int(image_width/gridth_width)+col_index]], color=(0, 0, 0))
            
    cv2.imshow("Game of Life Pattern", pattern)
    inv = np.copy(pattern)
    cv2.waitKey(1)