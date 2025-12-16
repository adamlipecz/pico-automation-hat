# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file LICENSE.rst or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-src")
  file(MAKE_DIRECTORY "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-src")
endif()
file(MAKE_DIRECTORY
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-build"
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix"
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/tmp"
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/src/picotool-populate-stamp"
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/src"
  "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/src/picotool-populate-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/src/picotool-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/Users/adamlipecz/Documents/GitHub/pico-automation-hat/firmware-cpp/build/_deps/picotool-subbuild/picotool-populate-prefix/src/picotool-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
