import numpy as np
from typing import NamedTuple
import os
import json

class componentsSelection(NamedTuple):
    StartPoint: tuple
    EndPoint: tuple
    label: str = ''

class imageProperties():
    imageLocation = ''
    selectedAreas = []
    dragging = False
    defaultAreaPickerSize = 15
    

    def __init__(self, imageLocation):
        self.imageLocation = imageLocation

    def addArea(self, start_point, end_point, label=''):
        self.selectedAreas.append(componentsSelection(start_point, end_point, label))

    def returnAreaSelected(self):
        return self.selectedAreas

    def updateImageFile(self, imageLocation, graph):
        graph.erase()
        self.imageLocation = imageLocation
        graph.draw_image(self.imageLocation, location=(0,270))
        for rectangles in self.returnAreaSelected():
            graph.draw_rectangle(rectangles.StartPoint, rectangles.EndPoint, line_color='red')

    def saveFile(self, filename):
        data = {}

        data['config'] = []

        for idx, rectangles in enumerate(self.returnAreaSelected()):
            data['config'].append({
                'coordinate':{
                    'Label': idx,
                    'StartPoint':{
                        'x':    int(rectangles.StartPoint[0]),
                        'y':    int(rectangles.StartPoint[1])
                    },
                    'EndPoint': {
                        'x':    int(rectangles.EndPoint[0]),
                        'y':    int(rectangles.EndPoint[1])
                    }
                }
            })
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w+') as f:
            json.dump(data, f, indent=4)

    def loadFile(self, filename, graph):
        try:
            with open(r'C:\Users\gely\Desktop\Desenvolvimento\Python\PyImageEdit\products\IO103\IO103.json', 'r') as f:
                data = json.load(f)

            for coordinates in data['config']:
                start_point = end_point = None

                start_point = (coordinates['coordinate']['StartPoint']['x'], coordinates['coordinate']['StartPoint']['y'])
                end_point = (coordinates['coordinate']['EndPoint']['x'], coordinates['coordinate']['EndPoint']['y'])
                self.addArea(start_point, end_point)

            for rectangles in self.returnAreaSelected():
                    graph.draw_rectangle(rectangles.StartPoint, rectangles.EndPoint, line_color='red')

        except Exception as e:
            print("Não existem configurações para este PA.\n" + str(e))

    def drawImage(self, window, graph):
        start_point = end_point = prior_rect = None
        event, values = window.read()
        while not event.endswith('+UP'):
            
            x, y = values['-GRAPH-']
            event, values = window.read()
            
            if not self.dragging:
                start_point = (x, y)
                self.dragging = True
            else:
                end_point = (x, y)

            if prior_rect:
                graph.delete_figure(prior_rect)
            if None not in (start_point, end_point):
                prior_rect = graph.draw_rectangle(start_point, end_point, line_color='red')

        if event.endswith('+UP'):  # The drawing has ended because mouse up
            if start_point!=None and end_point!=None:
                graph.draw_image(self.imageLocation, location=(0,270))
                #Inversão de ordem do ponto inicial para que a referência inicial seja sempre o canto esquerdo superior
                if start_point[0]>end_point[0]:
                    hold = end_point[0]
                    end_point = (start_point[0], end_point[1])
                    start_point = (hold, start_point[1])
                if start_point[1]<end_point[1]:
                    hold = end_point[1]
                    end_point = (end_point[0], start_point[1])
                    start_point = (start_point[0], hold)

                sizeX = end_point[0]-start_point[0]
                sizeY = start_point[1] - end_point[1]
                if (sizeX >= self.defaultAreaPickerSize) and (sizeY >= self.defaultAreaPickerSize):
                    self.addArea(start_point, end_point)

                graph.delete_figure(prior_rect)
                info = window['info']
                info.update(value=f'grabbed rectangle from {start_point} to {end_point}')
                start_point, end_point = None, None  # enable grabbing a new rect

                for rectangles in self.returnAreaSelected():
                    graph.draw_rectangle(rectangles.StartPoint, rectangles.EndPoint, line_color='red')
            self.dragging = False

    def moveRectangle(self, window, graph, event, idx):
        points = self.returnAreaSelected()
        cursor = 'fleur'
        window.find_element('-GRAPH-').set_cursor(cursor)

        prior_rect = None

        if event == '-GRAPH-':  # if there's a "Graph" event, then it's a mouse 
            rectSizeX = points[idx].EndPoint[0]-points[idx].StartPoint[0]
            rectSizeY = points[idx].EndPoint[1]-points[idx].StartPoint[1]  
            while not event.endswith('+UP'):
                event, values = window.read(timeout=0)

                newInitialPos = values['-GRAPH-']
                newEndPos = tuple(np.add(points[idx].StartPoint, (rectSizeX, rectSizeY)))
                
                points[idx] = points[idx]._replace(StartPoint = newInitialPos)
                points[idx] = points[idx]._replace(EndPoint = newEndPos)
                
                if prior_rect:
                    graph.erase()
                    graph.draw_image(self.imageLocation, location=(0,270)) if self.imageLocation else None

                for drawrectangles in points:
                    prior_rect = graph.draw_rectangle(drawrectangles.StartPoint, drawrectangles.EndPoint, line_color='red')

    def eraseRectangle(self, window, graph, event, idx):
        
        cursor = 'fleur'
        window.find_element('-GRAPH-').set_cursor(cursor)

        prior_rect = None

        if event.endswith('CLICK+'):  # if there's a "Graph" event, then it's a mouse 
            self.deleteRectangle(idx)
            points = self.returnAreaSelected()
            
            graph.erase()
            graph.draw_image(self.imageLocation, location=(0,270)) if self.imageLocation else None

            for drawrectangles in points:
                prior_rect = graph.draw_rectangle(drawrectangles.StartPoint, drawrectangles.EndPoint, line_color='red')


    def resizeRectangle(self, window, idx, event, graph):
        points = self.returnAreaSelected()
        cursor = 'bottom_right_corner'
        window.find_element('-GRAPH-').set_cursor(cursor)

        prior_rect = None

        if event == '-GRAPH-':  # if there's a "Graph" event, then it's a mouse 
            while not event.endswith('+UP'):
                event, values = window.read()
                x, y = values['-GRAPH-']
                if (points[idx].StartPoint[0]+self.defaultAreaPickerSize < x) and (points[idx].StartPoint[1]-self.defaultAreaPickerSize > y):
                    points[idx] = points[idx]._replace(EndPoint = (x,y))

                if prior_rect:
                    graph.erase()
                    graph.draw_image(self.imageLocation, location=(0,270)) if self.imageLocation else None
                for drawrectangles in points:
                    prior_rect = graph.draw_rectangle(drawrectangles.StartPoint, drawrectangles.EndPoint, line_color='red')

    def deleteRectangle(self, idx):
        self.selectedAreas.pop(idx)