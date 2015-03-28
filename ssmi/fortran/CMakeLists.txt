PROJECT(emiss)
set(CMAKE_MACOSX_RPATH 1)
# use, i.e. don't skip the full RPATH for the build tree
SET(CMAKE_SKIP_BUILD_RPATH  FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE) 

# the RPATH to be used when installing
SET(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}")
SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")

# don't add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
MESSAGE("here is CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")
MESSAGE("here is PROJECT_SOURCE_DIR: ${PROJECT_SOURCE_DIR}")
# the RPATH to be used when installing, but only if it's not a system directory
LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_PREFIX}/lib" isSystemDir)
IF("${isSystemDir}" STREQUAL "-1")
   SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
ENDIF("${isSystemDir}" STREQUAL "-1")


#set(CMAKE_C_COMPILER /usr/local/bin/gcc-4.9)
#set(CMAKE_CXX_COMPILER /usr/local/bin/g++-4.9)
#set(CMAKE_C_COMPILER gcc)
#set(CMAKE_CXX_COMPILER g++)
cmake_minimum_required(VERSION 2.8)
project(temp)
set(CMAKE_Fortran_COMPILER gfortran)
enable_language(Fortran)
FILE(GLOB files_fortran "*.f")
add_library(emiss SHARED ${files_fortran})
install(TARGETS emiss LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
