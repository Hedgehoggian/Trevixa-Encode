cmake_minimum_required(VERSION 3.20)
project(trevixa_encode VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(trevixa-encode
    cpp/main.cpp
    cpp/api.cpp
)

target_include_directories(trevixa-encode PRIVATE cpp)

if(WIN32)
  target_compile_definitions(trevixa-encode PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
