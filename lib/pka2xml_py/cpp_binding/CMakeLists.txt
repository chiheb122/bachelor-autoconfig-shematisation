cmake_minimum_required(VERSION 3.12)
project(pka2core)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)
include_directories(include /usr/local/include)
link_directories(/usr/local/lib)

add_library(pka2core MODULE
    bindings.cpp
)

target_link_libraries(pka2core
    PRIVATE
    pybind11::module
    /usr/local/lib/libcryptopp.a
)
