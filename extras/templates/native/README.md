# Native project starter

Copy this directory into your project as implementation/ and edit CMakeLists.txt. This is a planned PolyGlue integration example, not the implemented generator. It requires the generated polyglue-integration.cmake fragment defined in PROJECT.md section 20.4. No JSON dependency is required by PolyGlue; the optional example is disabled by default.

The project owns CMake target definitions, sources, headers, compile options, linkage, dependency versions and installation. The generated fragment supplies only bindings and required support. For a CMake distribution, extend the install rules with relocatable package exports and the actual transitive dependency closure; this starter stages the native library and public generated headers.

## System or CPM

Use a normal CMake preset or direct CMake command. For CPM, put a reviewed, pinned CPM.cmake at cmake/CPM.cmake and select POLYGLUE_DEPENDENCY_TOOL=cpm, EXAMPLE_WITH_JSON=ON and EXAMPLE_JSON_REVISION=<reviewed full Git commit SHA> in the preset. The JSON example uses the same nlohmann_json::nlohmann_json target as Conan. Select the matching 3.12.0 revision if comparing these examples; update versions deliberately using verified upstream releases.

## Conan

The recipe demonstrates CMakeDeps and CMakeToolchain. Prepare the toolchain with real project-owned host/build profiles and a reviewed lockfile before configuring CMake. Example paths (run from the project root):

```bash
conan install implementation --output-folder build/conan/linux-x86_64 --profile:build profiles/build --profile:host profiles/linux-x86_64 --lockfile locks/linux-x86_64.lock --settings:host build_type=Release
cmake -S implementation -B build/native/linux-x86_64 -DCMAKE_TOOLCHAIN_FILE="$PWD/build/conan/linux-x86_64/conan_toolchain.cmake" -DCMAKE_BUILD_TYPE=Release -DPOLYGLUE_DEPENDENCY_TOOL=conan -DEXAMPLE_WITH_JSON=ON -DPOLYGLUE_INTEGRATION_FILE=/absolute/path/to/polyglue-integration.cmake -DPOLYGLUE_LIBRARY_ID=example -DPOLYGLUE_ARTIFACT_NAME=Example
cmake --build build/native/linux-x86_64 --config Release
cmake --install build/native/linux-x86_64 --config Release --prefix "$PWD/build/stage/linux-x86_64"
```

The profiles, lockfile and generated integration path are project inputs; they are not fabricated by this template. Pass the library version and build number when packaging. Use a single compatible toolchain per slice. JNI, Apple framework and WASM starters use their own native CMake target types and official toolchain settings; do not use this desktop C/C++ starter unchanged for those formats.
