import PySimpleGUI as sg
import numpy as np

"""
    Demo - Drag a rectangle to draw it
    This demo shows how to use a Graph Element to (optionally) display an image and then use the
    mouse to "drag a rectangle".  This is sometimes called a rubber band and is an operation you
    see in things like editors
"""

from app.Controllers.imageController import imageProperties as imgC

image_file = r'C:\Users\gely\Desktop\Desenvolvimento\Python\SimplePyImg\savedResults\Default_1.png'  # image is optional

imageProps = imgC(image_file)

layout = [
    [
        sg.Graph(
        canvas_size=(480, 270),
        graph_bottom_left=(0, 0),
        graph_top_right=(480, 270),
        key="-GRAPH-",
        change_submits=True,  # mouse click events
        drag_submits=True,
        enable_events=True,
        background_color='lightblue'
        ), 
    ],
    [
        sg.Text(
            key='info',
            size=(60, 1)
        )
    ]
]

window = sg.Window("draw rect on image", layout, finalize=True)

# get the graph element for ease of use later
graph = window["-GRAPH-"]  # type: sg.Graph

graph.bind('<Enter>', '+MOUSE OVER+')
graph.bind('<Leave>', '+MOUSE AWAY+')
graph.bind('<Motion>', '+MOVED+')
graph.bind('<Button-2>', '+MIDDLE CLICK+')

graph.draw_image(image_file, location=(0,270)) if image_file else None
dragging = False
start_point = end_point = prior_rect = None
points = []

cursor = "arrow"

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break  # exit

    if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
        imageProps.drawImage(window, graph)


    if event.endswith('+MOVED+'):
        if(imageProps.returnAreaSelected()):
            points = imageProps.returnAreaSelected()
            x, y = values["-GRAPH-"]
            for idx, rectangles in enumerate(points):
                
                lowerLimit = tuple(np.subtract(rectangles.StartPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))
                upperLimit = tuple(np.add(rectangles.StartPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))

                lowerLimitResize = tuple(np.subtract(rectangles.EndPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))
                upperLimitResize = tuple(np.add(rectangles.EndPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))         
                
                while x <= upperLimit[0] and x >= lowerLimit[0] and y <= upperLimit[1] and y >= lowerLimit[1]:
                    event, values = window.read()
                    x, y = values["-GRAPH-"]
                    lowerLimit = tuple(np.subtract(rectangles.StartPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))
                    upperLimit = tuple(np.add(rectangles.StartPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))

                    imageProps.moveRectangle(window, graph, event, idx)
                    imageProps.eraseRectangle(window, graph, event, idx)

                while x <= upperLimitResize[0] and x >= lowerLimitResize[0] and y <= upperLimitResize[1] and y >= lowerLimitResize[1]:
                    event, values = window.read()
                    x, y = values["-GRAPH-"]
                    lowerLimitResize = tuple(np.subtract(rectangles.EndPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))
                    upperLimitResize = tuple(np.add(rectangles.EndPoint, (imageProps.defaultAreaPickerSize,imageProps.defaultAreaPickerSize)))

                    imageProps.resizeRectangle(window, idx, event, graph)
                
                cursor = "arrow"
                window.find_element("-GRAPH-").set_cursor(cursor)

    else:
        pass
        print("unhandled event", event, values)