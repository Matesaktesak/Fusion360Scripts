#Author-Autodesk Inc. & Matyáš Levíček
#Description-Import spline from CSV file

# Original script by Autodesk has been edited to be friendlier to use.
# Most important changes:
# - When a sketch is open for editing, it gets used for the import
# - CSV is expected to be in milimeters

import adsk.core, adsk.fusion, traceback
import io

def run(context):
    ui = None
    title = 'Import Spline csv'
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get all components in the active design.
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('The DESIGN workspace must be active when running this script.', title)
            return
        
        ui.messageBox('Ensure CSV values are separated by commas and in units of mm')
        
        dlg = ui.createFileDialog()
        dlg.title = 'Open CSV File'
        dlg.filter = 'Comma Separated Values (*.csv);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
            return
        
        filename = dlg.filename
        with io.open(filename, 'r', encoding='utf-8-sig') as f:
            points = adsk.core.ObjectCollection.create()
            line = f.readline()
            data = []
            while line:
                pntStrArr = line.split(',')
                for pntStr in pntStrArr:
                    try:
                        data.append(float(pntStr))
                    except:
                        break
                # If given 2D point, add Z=0
                if len(data) == 2:
                    point = adsk.core.Point3D.create(data[0]/10, data[1]/10, 0)
                    points.add(point)
                if len(data) == 3 :
                    point = adsk.core.Point3D.create(data[0]/10, data[1]/10, data[2]/10)
                    points.add(point)
                line = f.readline()
                data.clear()            
        if points.count:
            sketch = getTargetSketch(app, design, filename.split('/')[-1])
            sketch.sketchCurves.sketchFittedSplines.add(points)
            ui.messageBox('Done: {points.count} points imported'.format(points=points), title)
        else:
            ui.messageBox('No valid points', title)            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def getTargetSketch(app, design, newName):
    # When a sketch is alredy open for editing, use it as target sketch.
    if isinstance(app.activeEditObject, adsk.fusion.Sketch):
        return app.activeEditObject
    # Otherwise, create a new sketch on the xy plane of the root component.
    else:
        root = design.rootComponent
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = 'Imported: {newName}'.format(newName=newName)
        return sketch
