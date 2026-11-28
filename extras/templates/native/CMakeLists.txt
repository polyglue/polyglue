cmake_minimum_required(VERSION 3.25)
project(Example LANGUAGES C CXX)

# Editable consumer project. The generator supplies the binding fragment, not
# the handwritten source list, dependency graph or compiler configuration.
include(GNUInstallDirs)

set(POLYGLUE_DEPENDENCY_TOOL "system" CACHE STRING "Native dependency tool")
set_property(CACHE POLYGLUE_DEPENDENCY_TOOL PROPERTY STRINGS system cpm conan)
set(_dependency_tools system cpm conan)
if(NOT POLYGLUE_DEPENDENCY_TOOL IN_LIST _dependency_tools)
    message(FATAL_ERROR "Unsupported dependency tool: ${POLYGLUE_DEPENDENCY_TOOL}")
endif()

set(EXAMPLE_LIBRARY_KIND "STATIC" CACHE STRING "Native library kind")
set_property(CACHE EXAMPLE_LIBRARY_KIND PROPERTY STRINGS STATIC SHARED)
set(_library_kinds STATIC SHARED)
if(NOT EXAMPLE_LIBRARY_KIND IN_LIST _library_kinds)
    message(FATAL_ERROR "Expected STATIC or SHARED")
endif()

option(EXAMPLE_WITH_JSON "Enable the optional illustrative JSON dependency" OFF)
option(EXAMPLE_BUILD_TESTS "Build consumer-owned tests" OFF)
set(EXAMPLE_CPM_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/CPM.cmake" CACHE FILEPATH "Pinned project-owned CPM script")
set(EXAMPLE_JSON_REVISION "" CACHE STRING "Reviewed immutable nlohmann/json commit SHA")

foreach(_required POLYGLUE_INTEGRATION_FILE POLYGLUE_LIBRARY_ID POLYGLUE_ARTIFACT_NAME)
    if(NOT DEFINED ${_required} OR "${${_required}}" STREQUAL "")
        message(FATAL_ERROR "Missing ${_required}; generate bindings and pass their integration file")
    endif()
endforeach()
if(NOT EXISTS "${POLYGLUE_INTEGRATION_FILE}")
    message(FATAL_ERROR "Generated integration file not found: ${POLYGLUE_INTEGRATION_FILE}")
endif()

add_library(example ${EXAMPLE_LIBRARY_KIND})
set_target_properties(example PROPERTIES
    OUTPUT_NAME "${POLYGLUE_ARTIFACT_NAME}"
    POSITION_INDEPENDENT_CODE ON
    C_VISIBILITY_PRESET hidden
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)
target_compile_features(example PUBLIC c_std_11 cxx_std_20)

# All native source and link declarations remain here, or in ordinary
# CMake files included explicitly by this project.
# target_sources(example PRIVATE src/repository.cpp)
# target_include_directories(example PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")
# add_subdirectory(modules/network)
# target_link_libraries(example PRIVATE network)

if(EXAMPLE_WITH_JSON)
    if(POLYGLUE_DEPENDENCY_TOOL STREQUAL "cpm")
        if(NOT EXISTS "${EXAMPLE_CPM_FILE}")
            message(FATAL_ERROR "Provide a pinned CPM.cmake at EXAMPLE_CPM_FILE")
        endif()
        string(LENGTH "${EXAMPLE_JSON_REVISION}" _revision_length)
        if(NOT _revision_length EQUAL 40 OR NOT EXAMPLE_JSON_REVISION MATCHES "^[0-9a-fA-F]+$")
            message(FATAL_ERROR "Provide the reviewed full nlohmann/json Git commit SHA")
        endif()
        include("${EXAMPLE_CPM_FILE}")
        CPMAddPackage(NAME nlohmann_json GITHUB_REPOSITORY nlohmann/json GIT_TAG "${EXAMPLE_JSON_REVISION}" OPTIONS "JSON_BuildTests OFF")
    else()
        # Conan installs its generated config files before this configure.
        # The system path uses the same ordinary CMake imported target.
        find_package(nlohmann_json 3.12.0 EXACT CONFIG REQUIRED)
    endif()
    target_link_libraries(example PRIVATE nlohmann_json::nlohmann_json)
endif()

include("${POLYGLUE_INTEGRATION_FILE}")
polyglue_attach_generated(example)

# Native version/build identity comes from the invoking library metadata.
# The generated integration owns its version metadata resource/header.
if(DEFINED POLYGLUE_LIBRARY_VERSION AND EXAMPLE_LIBRARY_KIND STREQUAL "SHARED")
    set_target_properties(example PROPERTIES VERSION "${POLYGLUE_LIBRARY_VERSION}")
endif()

if(MSVC)
    target_compile_options(example PRIVATE /W4)
else()
    target_compile_options(example PRIVATE -Wall -Wextra)
endif()

# The actual installed products, not guessed build output filenames, feed
# the packager. Add project-specific runtime dependency installation here.
install(TARGETS example
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)
if(DEFINED POLYGLUE_GENERATED_INCLUDE_DIR AND IS_DIRECTORY "${POLYGLUE_GENERATED_INCLUDE_DIR}")
    install(DIRECTORY "${POLYGLUE_GENERATED_INCLUDE_DIR}/" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
endif()

if(EXAMPLE_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
