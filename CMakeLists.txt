cmake_minimum_required(VERSION 2.8.9)

project(SlicerBRAINS)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/pieper/SlicerBRAINS")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Steve Pieper (Isomics, Inc.)")
set(EXTENSION_DESCRIPTION "Slicer specific code for BRAINS")
set(EXTENSION_ICONURL "https://raw.github.com/pieper/SlicerBRAINS/master/SlicerBRAINS.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerBRAINS/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BRAINSFitUI)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
