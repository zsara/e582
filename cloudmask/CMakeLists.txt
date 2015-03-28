project(bitmap)
set(CMAKE_MODULE_PATH "/home/phil/cmake")
cmake_minimum_required(VERSION 2.6)
set(LIBRARY_OUTPUT_PATH  ${CMAKE_SOURCE_DIR}/testlib)
set(CMAKE_INSTALL_PREFIX /home/phil/lib/python)

include(UseCython)
find_package(PythonLibs REQUIRED)
find_package(NumPy REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH} ${NUMPY_INCLUDE_PATH})
cython_add_module(bitmap bitmask.cpp)

install(TARGETS bitmap LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX})
#set(plot_dir ${CMAKE_SOURCE_DIR}/figures)

#add_custom_target(test COMMAND python ${CMAKE_SOURCE_DIR}/test_hist.py ${plot_dir}
#                  DEPENDS COMMENT "execute doit.py and make plots")




