import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# BRAINSFitUI
#

class BRAINSFitUI(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BRAINSFitUI" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# BRAINSFitUIWidget
#

class BRAINSFitUIWidget(ScriptedLoadableModuleWidget):

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.outputSelector.selectNodeUponCreation = False
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # scale factor for screen shots
    #
    self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
    self.screenshotScaleFactorSliderWidget.singleStep = 1.0
    self.screenshotScaleFactorSliderWidget.minimum = 1.0
    self.screenshotScaleFactorSliderWidget.maximum = 50.0
    self.screenshotScaleFactorSliderWidget.value = 1.0
    self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
    parametersFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = BRAINSFitUILogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,screenshotScaleFactor)


#
# BRAINSFitUILogic
#

class BRAINSFitUILogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """

  availablePhases = set([ 'useRigid',
       'useScaleVersor3D',
       'useScaleSkewVersor3D',
       'useAffine',
       'useBSpline',
       'useSyN',
       'useComposite',
       ])

  def register(self,fixedVolume,movingVolume,parameters={}):
    """
    Run BRAINSFit to register movingVolume in the space of fixedVolume.
    Parameters is and optional dictionary.
    Returns parameters with any defaults filled in.
    """

    self.delayDisplay('Running the BRAINSFit')

    # required parameters
    parameters["fixedVolume"] = fixedVolume.GetID()
    parameters["movingVolume"] = movingVolume.GetID()

    # type of transform is optional, default to linear
    keys = parameters.keys()
    if "useBSpline" in keys:
      if not 'bsplineTransform' in keys:
        transform = slicer.vtkMRMLBSplineTransformNode()
        slicer.mrmlScene.AddNode(transform)
        parameters['bsplineTransform'] = transform.GetID()
    else:
      if not 'linearTransform' in keys:
        transform = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transform)
        parameters['linearTransform'] = transform.GetID()

    # if no phase picked, default to rigid
    if not self.availablePhases.intersection(parameters):
      parameters['useRigid'] = True

    # if no output volume specified, clone the moving
    if not "outputVolume" in parameters.keys():
      outputName = movingVolume.GetName() + "-transformed"
      volumesLogic = slicer.modules.volumes.logic()
      outputVolume = volumesLogic.CloneVolume(slicer.mrmlScene, movingVolume, outputName)
      parameters['outputVolume'] = outputVolume.GetID()

    self.delayDisplay(parameters)

    cliNode = slicer.cli.run(slicer.modules.brainsfit, None, parameters, delete_temporary_files=False)
    waitCount = 0
    maxWait = 10000
    while cliNode.GetStatusString() != 'Completed' and waitCount < maxWait:
      self.delayDisplay( "Running BRAINSFit... %d seconds" % waitCount )
      waitCount += 1

    if waitCount == maxWait:
      raise Exception("Registration took too long to run!")

    self.delayDisplay( "Finished after %d seconds" % waitCount )
    return parameters


class BRAINSFitUITest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_BRAINSFitUI1()

  def test_BRAINSFitUI1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://joe.bwh.harvard.edu/tmp/3788-right-eye/fixed.nrrd', 'fixed.nrrd', slicer.util.loadVolume),
        ('http://joe.bwh.harvard.edu/tmp/3788-right-eye/moving.nrrd', 'moving.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    fixed = slicer.util.getNode(pattern="fixed")
    moving = slicer.util.getNode(pattern="moving")
    logic = BRAINSFitUILogic()
    
    # run with the default rigid configuration
    parameters = logic.register(fixed,moving)
    self.delayDisplay("Rigid result:\n"+str(parameters))

    # run with rigid plus bspline
    del parameters['linearTransform']
    parameters['useBSpline'] = True
    parameters['numberOfIterations'] = 3
    parameters = logic.register(fixed,moving,parameters)
    self.delayDisplay("BSpline result:\n"+str(parameters))

    bsplineNode = slicer.util.getNode(parameters['bsplineTransform'])
    generalTransform = bsplineNode.GetTransformFromParent()
    if generalTransform.GetClassName() != "vtkGeneralTransform":
      raise Exception("BSpline incorrect type!")
    else:
      bsplineTransform = generalTransform.GetConcatenatedTransform(0)
      coefficients = bsplineTransform.GetCoefficientData()
      if coefficients.GetDimensions() != (17, 13, 15):
        raise Exception("BSpline dimensions incorrect!")

    self.delayDisplay('Test passed!')
