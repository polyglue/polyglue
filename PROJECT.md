# PolyGlue — Project specification

> **Status:** planned, not implemented. This document is the source of truth for implementation and review. Examples specify intended behavior; they are not evidence of an existing implementation.

## Contents

- [1. Product and scope](#1-product-and-scope)
- [2. Supported languages and platforms](#2-supported-languages-and-platforms)
- [3. Developer workflow and distribution](#3-developer-workflow-and-distribution)
- [4. IDL language](#4-idl-language)
- [5. Type system](#5-type-system)
- [6. Modules and dependencies](#6-modules-and-dependencies)
- [7. Module-first configuration](#7-module-first-configuration)
- [8. Naming and file formatting](#8-naming-and-file-formatting)
- [9. Annotations and platform attributes](#9-annotations-and-platform-attributes)
- [10. Output layout and import resolution](#10-output-layout-and-import-resolution)
- [11. Compiler and templates](#11-compiler-and-templates)
  - [Template override system](#115-template-override-system-mandatory)
- [12. Native runtime and ABI](#12-native-runtime-and-abi)
- [13. Memory and buffers](#13-memory-and-buffers)
- [14. Asynchronous operations callbacks and streams](#14-asynchronous-operations-callbacks-and-streams)
- [15. Interfaces and service discovery](#15-interfaces-and-service-discovery)
- [16. Language-specific integration](#16-language-specific-integration)
- [17. Example applications](#17-example-applications)
- [18. Test specification](#18-test-specification)
- [19. GitHub Actions](#19-github-actions)
- [20. Repository documentation and branding](#20-repository-documentation-and-branding)
  - [Native build system and CMake organization](#204-native-build-system-and-cmake-organization)
  - [Python build orchestration and artifact pipeline](#205-python-build-orchestration-and-artifact-pipeline)
  - [Binary and package outputs by target](#206-binary-and-package-outputs-by-target)
- [21. Implementation phases and reviews](#21-implementation-phases-and-reviews)
- [22. Release acceptance checklist](#22-release-acceptance-checklist)

## 1. Product and scope

**One definition. Multiple languages. Native interoperability.**

PolyGlue is a cross-platform interface compiler and source-code generator, written in Python with Jinja2 templates. Its primary product is generated, idiomatic, strongly typed source code that allows languages to consume and implement interfaces in either direction.

### 1.1 Required outcomes

- One IDL can describe data models, repositories, services, callbacks, factories and asynchronous operations.
- A module can import data models and interfaces defined or generated in another module.
- A developer can implement a contract in Kotlin and consume it from Flutter, C++ or another available runtime; the same contract can also be implemented in Dart or Swift.
- Native calls can share memory without copying when supported, and make copying explicit when necessary.
- Every module can choose independent output directories, packages, namespaces, prefixes, naming conventions, annotations and build integration.
- The generator and native support libraries live in one repository and are released and tested together.
- An optional registry allows runtime service discovery and replacement. Ordinary interface references work without it.

### 1.2 Non-goals and decisions

| Topic | Decision |
| --- | --- |
| Existing IDL compatibility | None; design an independent language |
| Protocol Buffers | Out of scope |
| Network RPC | Out of scope; no mandatory transport or serialization |
| Provider as built-in IDL type | Omit; interfaces and callbacks implement factories |
| Future syntax | Use `async` in IDL; futures are runtime/target representations |
| Result / Outcome | Use `Result<T, E>` for typed business errors |
| Global service locator | Optional, never required to invoke an interface |
| Python in production | Only when Python is a selected application runtime |
| External formatters | Optional; generated source is readable by default |
| Universal cross-runtime sync dispatch | Do not promise where thread or isolate constraints make it unsafe |

Use original implementations. Preserve required third-party notices when dependencies are used; do not copy existing generator or runtime source. Prefer fewer dependencies and a small, well-tested runtime. No unverified feature claims.

## 2. Supported languages and platforms

### 2.1 Language targets

Every language must be able to act as a consumer and as an implementation provider where its runtime permits the operation.

| Target | Boundary | Async surface |
| --- | --- | --- |
| C | Versioned C ABI | Completion function and opaque operation handle |
| C++ | C++20 interface / C ABI adapter | Awaitable / future |
| Java | JNI | CompletableFuture |
| Kotlin | JNI / JVM | suspend function |
| Objective-C | Objective-C++ | Completion block |
| Swift | Native Apple adapter | async throws |
| Python | CPython adapter | awaitable / async def |
| Dart | Dart FFI or web adapter | Future |
| Flutter | Dart bindings plus native plugin | Future |
| C# | .NET interop | Task |
| JavaScript | WebAssembly / JS adapter | Promise |
| TypeScript | JS implementation plus type declarations | Promise |

Flutter is an integration target, not a separate language. JavaScript and TypeScript may share implementation artifacts. Java and Kotlin can share JVM models to avoid duplicate classes. Swift and Objective-C can share imported types or use distinct namespaced wrappers; never generate conflicting definitions.

### 2.2 Platform matrix

| Platform | Required primary targets | Evidence |
| --- | --- | --- |
| Linux | C, C++, Java, Kotlin, Python, Dart, Flutter, C# | Native execution |
| Windows | C, C++, Java, Kotlin, Python, Dart, Flutter, C# | Native execution |
| macOS | C, C++, Objective-C, Swift, Java, Kotlin, Python, Dart, Flutter, C# | Native execution |
| Android | C, C++, Java, Kotlin, Dart, Flutter | Emulator and device smoke where required |
| Android XR | C, C++, Java, Kotlin | SDK build and compatible emulator/device |
| iOS / iPadOS | C, C++, Objective-C, Swift, Dart, Flutter | Simulator and device smoke where required |
| tvOS | C, C++, Objective-C, Swift | SDK build and simulator |
| watchOS | C, C++, Objective-C, Swift | SDK build and simulator |
| visionOS | C, C++, Objective-C, Swift | SDK build and visionOS simulator/device |
| Mac Catalyst | C, C++, Objective-C, Swift | SDK build and execution |
| WebAssembly | C/C++, JS, TS, Dart/Flutter Web where supported | Node and browser execution |

The table is a required coverage plan, not verified support. Each combination requires a capability entry and actual evidence. Native visionOS support is independent of Flutter; native Flutter visionOS is conditional on upstream SDK/engine support. Flutter Web uses JS/WASM adapters rather than dart:ffi. Additional runtime combinations require explicit tests.

Build-only, emulator/simulator and physical-device evidence must be reported separately. An unavailable runner is a blocker, not a pass.

## 3. Developer workflow and distribution

### 3.1 Project usage

The CLI is named `polyglue`. The main config is `polyglue.yaml`; modules use `module.yaml`. IDL files use `.idl`.

```bash
polyglue generate
polyglue generate --module domain
polyglue generate --module repository --target swift
polyglue generate --config modules/domain/module.yaml
polyglue validate
polyglue config show --module repository --target objc
polyglue list targets
polyglue --version
```

When a selected module depends on another module, resolve its source or prebuilt manifest automatically. Only generate the selected target and its required source dependencies. Validation must happen before writes. The config inspection command prints the effective merged settings, resolved paths and their origins.

### 3.2 Official and local generator

After release:

```bash
uvx polyglue@1.0.0 generate
pip install polyglue
polyglue generate
```

From source:

```bash
git clone https://github.com/polyglue/polyglue.git
cd polyglue
uv sync
uv run polyglue generate --config examples/polyglue.yaml
uv tool install --editable .
```

A consumer may pin an official version or run a modified local checkout without changing the IDL. The package must work offline after installation; wheel and sdist include the grammar, built-in templates and runtime source resources.

Python API:

```python
from polyglue import Compiler

compiler = Compiler.from_file("polyglue.yaml")
compiler.validate()
compiler.generate()
```

Use a standalone installed CLI as the baseline. A bundled executable without a separately installed Python is optional after the wheel works. Do not publish packages before all required release gates and owner authorization.

### 3.3 Tooling

Python 3.12+, uv, pyproject.toml, uv.lock, Lark, Jinja2, safe YAML loading, typed dataclasses, argparse, pytest, Hypothesis and Ruff. Native support: C++20, C ABI, CMake and standard toolchains. Avoid duplicate configuration or CLI frameworks, mandatory formatters, generators requiring Scala/JVM and unnecessary build systems.

### 3.4 Build, test and packaging commands

One installed Python CLI is the entry point for generation and native build orchestration. A repository-local invocation uses the same code as the installed CLI; do not maintain a second independent task runner.

| Command | Responsibility |
| --- | --- |
| polyglue doctor | Discover host, installed SDKs, compilers and tool versions; show missing requirements for the selected target |
| polyglue generate | Generate source files and configured integration metadata; no native SDK required |
| polyglue build | Resolve the selected build plan, generate inputs if needed, configure and build the requested artifact |
| polyglue test | Run actual target-specific tests and conformance cases, optionally with sanitizer configuration |
| polyglue package | Build and assemble the requested final distributable, validate it and write an artifact manifest |
| polyglue run | Run the selected example where the current host or device allows execution |
| polyglue clean | Remove only PolyGlue-owned build outputs for the selected scope |
| polyglue config show | Inspect the effective configuration and its origin |
| polyglue templates list | Show template IDs, target, source and render-model version |
| polyglue templates export | Export selected built-in templates for local customization |
| polyglue templates check | Validate a template override set against its declared target and context contract |

Illustrative CLI (commands to implement and test, not available yet):

```bash
uv run polyglue doctor --target kotlin --platform android
uv run polyglue generate --module repository --target kotlin
uv run polyglue build --product mobile --platform android --configuration release
uv run polyglue package --product mobile --format aar
uv run polyglue package --product apple --format xcframework
uv run polyglue package --product apple --format swiftpm
uv run polyglue package --product desktop --format cmake
uv run polyglue test --target cpp --sanitizer address
uv run polyglue test --target cpp --sanitizer thread
uv run polyglue run --target flutter --platform android
```

Use explicit module/target selection for source generation and explicit product selection for multi-module binary artifacts. Resolve missing or ambiguous product/format/SDK combinations before modifying outputs. Build/test/package may require native SDKs; generate/validate must remain offline Python-only. Support an explicit incremental mode with input fingerprint verification, an explicit clean build, a dry-run build plan, bounded parallelism, nonzero exit on failure/signal, and a machine-readable result option. Never report success just because an external command returned zero: verify expected artifacts and test results.

## 4. IDL language

### 4.1 Domain and repository example

`modules/domain/idl/user.idl`:

```text
module domain;

/// Represents a registered user.
record User {
    id: int64;
    name: string;
    email: optional<string>;
    loggedIn: bool = false;
}

enum UserStatus {
    Active = 1,
    Inactive = 2,
    Blocked = 3
}
```

`modules/repository/idl/user_repository.idl`:

```text
module repository;

import domain.User;
import domain.UserStatus;

interface UserRepository {
    async findById(id: int64): optional<User>;
    async findAll(): list<User>;
    async findByStatus(status: UserStatus): list<User>;
    async save(user: User): User;
    async saveAll(users: list<User>): list<User>;
    async count(): int64;
    async exists(id: int64): bool;
    async delete(id: int64): bool;
    async deleteAll(): void;
}
```

This is a core acceptance fixture. Each target must implement and consume these contracts across module and language boundaries. No JSON conversion or manually written bridge in the example.

### 4.2 Language constructs

| Construct | Semantics |
| --- | --- |
| module | Logical namespace, shared by multiple IDL files |
| import | Compile-time symbol reference, independent of physical output |
| record | Value semantics; immutable by default, configurable where safe |
| enum / flags | Stable integer representation, named values and bit masks |
| variant | Tagged union with explicit alternatives |
| interface | Object identity, methods and cross-language references |
| callback | Typed callable with a defined invocation and lifetime policy |
| async | Asynchronous operation independent of return type |
| const | Typed constant |
| static / factory | Explicitly bound factory or static method, not implicit global lookup |
| public / private | Export visibility |
| generic parameters | Concrete instantiation and ABI specialization |
| documentation | Structured comments copied to target documentation |
| annotations | Typed semantic or backend-specific metadata |

Support interface inheritance with cycle detection; reject recursive value layouts without an indirection. Validate constant ranges, defaults, method signatures, overload collisions and reserved IDL identifiers. Define grammar and diagnostic source spans before publishing the syntax.

### 4.3 Imports and aliases

```text
import domain.User;
import domain.{User, UserStatus};
import domain as model;
import domain.User as DomainUser;
import domain.*;
```

These are alternative forms, not intended to be combined redundantly. A wildcard import must resolve unambiguously. No dependence on C++ headers or Swift module names in IDL. Fully qualified logical identifiers can disambiguate types.

### 4.4 User-defined generics

```text
module common;

record Page<T> {
    items: list<T>;
    page: int32;
    pageSize: int32;
    total: int64;
    hasNext: bool;
}
```

```text
module repository;

import common.Page;
import domain.User;

interface PagedUserRepository {
    async findPage(page: int32, pageSize: int32): Page<User>;
}
```

Generic source types are instantiated consistently. C uses concrete generated types such as PageUser; generic-capable targets may expose native generics when equivalent. Separately generated modules must agree on specialization identity and ABI. Reject open generics at a concrete binary boundary.

## 5. Type system

### 5.1 Types to implement and test

| Group | IDL types |
| --- | --- |
| Scalar | bool, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64 |
| Text / binary | string, bytes |
| Collections | list<T>, set<T>, map<K,V>, array<T> |
| Optional / variant | optional<T>, variant |
| Named | record, enum, flags, interface |
| Special memory | DataView, MutableDataView, DataRef |
| Errors | Result<T,E> |
| Time and identity | timestamp, duration, uuid |
| Behavior | callback, async method, Stream<T> |
| Lifetime / control | WeakRef<T>, CancellationToken |
| External | Explicitly declared type with per-target adapter |

`void` is a return-only type (including Result success with no payload). `array<T>` is optimized for contiguous primitives; it must not silently become boxed storage when zero-copy is promised.

### 5.2 Return mapping examples

These are semantic API mappings; an async declaration wraps the corresponding type in the target's async mechanism.

| IDL | C++ | Kotlin | Swift | Dart |
| --- | --- | --- | --- | --- |
| User | User | User | User | User |
| optional<User> | std::optional<User> | User? | User? | User? |
| list<User> | std::vector<User> | List<User> | [User] | List<User> |
| int64 | int64_t | Long | Int64 | int (native) |
| bool | bool | Boolean | Bool | bool |
| void | void | Unit | Void | void |

For JavaScript and TypeScript, use bigint when exact 64-bit integer representation is required. Dart Web needs an explicitly validated exact-integer representation, not unchecked JS Number conversion. Java unsigned types require a documented exact mapping. C and Objective-C require explicit boxing/tagged representations for optionals, variants and generic collections.

### 5.3 Value and error rules

- Unicode strings use a specified UTF-8 boundary. Define invalid Unicode handling and test non-ASCII, supplementary characters, embedded nulls and empty strings.
- Integer values must not silently truncate. Define floating-point NaN, infinity and signed zero semantics.
- Specify collection equality, hashing, supported map keys, duplicate entries, ordering and nesting limits.
- Distinguish null, absent, empty and zero; enums and flags have a documented unknown-value policy.
- Define timestamp and duration units and UUID byte order; test exact round trips.
- Result<T,E> represents business success or failure; runtime/ABI failures use a separate status. No cross-ABI exception unwinding.
- External types require declared import paths, ABI representation, marshaller, ownership and tests for each target. No unsupported target fallback.

Example:

```text
enum LoginError {
    InvalidCredentials = 1,
    AccountDisabled = 2
}

interface Auth {
    async login(username: string, password: string): Result<User, LoginError>;
}
```

C++ can use a project Result implementation compatible with C++20 (std::expected only when available); Swift uses Result when the error meets Swift requirements, other targets use a native or generated tagged result. Business errors do not become unexpected exceptions.

### 5.4 Complete type mapping contract

The tables below define the intended public surface, not binary layout. Generated helper types are acceptable where the host language cannot represent the contract exactly. A representation is not supported until conversion, round-trip, ownership and negative tests pass in both directions. For an unsupported representation or combination, issue a diagnostic before writing files.

#### Numeric and text types

| IDL | C | C++ | Java | Kotlin | Objective-C | Swift |
| --- | --- | --- | --- | --- | --- | --- |
| bool | uint8_t (0/1) | bool | boolean | Boolean | BOOL | Bool |
| int8 | int8_t | int8_t | byte | Byte | int8_t | Int8 |
| int16 | int16_t | int16_t | short | Short | int16_t | Int16 |
| int32 | int32_t | int32_t | int | Int | int32_t | Int32 |
| int64 | int64_t | int64_t | long | Long | int64_t | Int64 |
| uint8 | uint8_t | uint8_t | short, checked | UByte | uint8_t | UInt8 |
| uint16 | uint16_t | uint16_t | int, checked | UShort | uint16_t | UInt16 |
| uint32 | uint32_t | uint32_t | long, checked | UInt | uint32_t | UInt32 |
| uint64 | uint64_t | uint64_t | BigInteger, checked | ULong | uint64_t | UInt64 |
| float32 | float | float | float | Float | float | Float |
| float64 | double | double | double | Double | double | Double |
| string | owned/scoped UTF-8 descriptor | std::string | String | String | NSString | String |
| bytes | owned byte descriptor | vector<uint8_t> | byte[] | ByteArray | NSData (copy) | Data (copy) |
| void | void/status | void | void / Void | Unit | void | Void |

| IDL | Python | Dart native | Dart Web | C# | JavaScript | TypeScript |
| --- | --- | --- | --- | --- | --- | --- |
| bool | bool | bool | bool | bool | boolean | boolean |
| int8/16/32 | int, checked | int, checked | int, checked | sbyte/short/int | number, checked | number |
| int64 | int, checked | int | BigInt | long | bigint | bigint |
| uint8/16/32 | int, checked | int, checked | int, checked | byte/ushort/uint | number, checked | number |
| uint64 | int, checked | BigInt | BigInt | ulong | bigint | bigint |
| float32 | float, f32 conversion | double, f32 conversion | double, f32 conversion | float | number, f32 conversion | number |
| float64 | float | double | double | double | number | number |
| string | str | String | String | string | string | string |
| bytes | bytes | Uint8List (copy) | Uint8List (copy) | byte[] | Uint8Array (copy) | Uint8Array |
| void | None | void | void | void | undefined | void |

Rules: all integral conversions validate range and type (Python bool is not accepted as an integer by accident); JS number inputs must be finite integers for integer types. Java unsigned widening preserves mathematical values, while Kotlin/JNI unsigned inline representations use deliberate bit conversions. Shared Java/Kotlin models require a checked conversion layer when their public unsigned representations differ. Dart native int64 and uint64 are not interchangeable: uint64 uses BigInt. Float32 rounding occurs at the boundary, and tests define NaN, infinity and negative zero behavior. Preserve embedded NUL with explicit lengths; reject invalid UTF-8 and unpaired surrogates rather than silently replacing them. C ABI bool is a fixed-width byte, not a compiler-dependent C++ bool layout.

#### Composite, temporal and special types

| IDL | C | C++ | Java / Kotlin | Objective-C / Swift |
| --- | --- | --- | --- | --- |
| record | Generated owned value/handle | struct | Generated immutable model | NSObject model / struct or imported model |
| enum / flags | Fixed-width value + constants | enum class / flags helper | Generated enum / flags wrapper preserving numeric contract | NS_ENUM / NS_OPTIONS; Swift enum / OptionSet |
| variant | Tagged union + destroy | std::variant | Generated sealed/tagged type | Tagged object / enum with associated values |
| list<T> | Typed descriptor or handle | vector<T> | List<T> | NSArray / [T] |
| set<T> | Typed descriptor or handle | set/hash set according to equality policy | Set<T> | NSSet / Set<T> |
| map<K,V> | Typed descriptor or handle | map/hash map | Map<K,V> | NSDictionary / Dictionary<K,V> |
| array<T> | Typed contiguous descriptor for primitives | vector<T> or dedicated array wrapper | Primitive array where exact | Typed contiguous buffer or generated array wrapper |
| optional<T> | Explicit presence tag + payload | optional<T> | Boxed nullable reference or explicit Optional wrapper | Nullable boxed value or explicit optional / Optional<T> |
| Result<T,E> | Tagged result + cleanup | PolyGlue Result | Generated Result class/sealed type | Tagged object / Swift Result or generated enum |
| interface | Typed opaque reference | shared owning interface reference | Interface and proxy | Protocol and proxy |
| callback | Function table + context | Callable wrapper | Functional interface / lambda | Block / closure |
| Stream<T> | Subscription handle | Async stream | Flow-compatible publisher / Kotlin Flow | Subscription block / AsyncSequence |
| WeakRef<T> | Weak handle | Weak interface reference | Generated weak handle | Generated weak handle |
| CancellationToken | Shared token handle | Token wrapper | Token wrapper | Token wrapper |
| timestamp | int64_t UTC microseconds | chrono-based checked wrapper | Instant or exact wrapper | Exact wrapper / Date conversion |
| duration | int64_t nanoseconds | chrono duration | Duration or exact wrapper | Exact wrapper / Duration conversion |
| uuid | 16-byte value | UUID value wrapper | UUID | NSUUID / UUID |
| external | Declared ABI + adapter | Declared type | Declared type | Declared type |
| DataView / MutableDataView / DataRef | See section 13 | See section 13 | See section 13 | See section 13 |

| IDL | Python | Dart / Flutter | C# | JavaScript / TypeScript |
| --- | --- | --- | --- | --- |
| record | frozen dataclass | immutable class | record or generated immutable class | immutable model / readonly interface plus runtime implementation |
| enum / flags | Enum / IntFlag or checked wrapper | enum / flags wrapper | enum / flags wrapper | frozen constants + checked numeric type |
| variant | Tagged dataclass union | sealed class | discriminated record hierarchy | Tagged object / discriminated union |
| list<T> | list[T] | List<T> | IReadOnlyList<T> | Array / ReadonlyArray<T> |
| set<T> | set[T] | Set<T> | IReadOnlySet<T> | Set<T> |
| map<K,V> | dict[K,V] | Map<K,V> | IReadOnlyDictionary<K,V> | Map<K,V> |
| array<T> | typed buffer for primitives | typed_data where exact | T[] / Memory<T> | TypedArray where exact |
| optional<T> | T or None | T? | Nullable<T> or nullable reference | T or null |
| Result<T,E> | Tagged result | sealed Result | Generated Result | Tagged object / discriminated union |
| interface | ABC / protocol + proxy | abstract interface class + proxy | interface + proxy | runtime object / interface + proxy |
| callback | Callable | typedef / function | delegate | Function / typed function |
| Stream<T> | AsyncIterator | Stream | IAsyncEnumerable<T> | AsyncIterable<T> |
| WeakRef<T> | generated weak handle | generated weak handle | generated weak handle | generated weak handle |
| CancellationToken | token wrapper | token wrapper | CancellationToken adapter | AbortSignal adapter |
| timestamp | exact wrapper / datetime conversion | exact microseconds / DateTime conversion | exact wrapper / DateTimeOffset conversion | bigint microseconds / Date conversion |
| duration | exact wrapper / timedelta conversion | exact nanoseconds / Duration conversion | exact wrapper / TimeSpan conversion | bigint nanoseconds |
| uuid | uuid.UUID | checked UUID value | Guid with canonical byte ordering | checked UUID value |
| external | Declared adapter | Declared adapter | Declared adapter | Declared adapter |
| DataView / MutableDataView / DataRef | See section 13 | See section 13 | See section 13 | See section 13 |

Nested optional values cannot collapse distinct absence states; either use a tagged wrapper or reject the unsupported nesting explicitly. Set/map keys must have portable equality and hashing. For 1.0 restrict keys to bool, integer, string, enum and UUID unless a portable equality policy has been proven. Do not use object identity for value keys. Primitive array mappings that cannot retain exact contiguous representation must use an exact wrapper or reject a zero-copy request. Time conversion into lower-precision host types is explicit; the exact canonical representation must survive round trips. UUID bytes use network order, including .NET conversion.

### 5.5 Per-type acceptance

Generate shared fixtures with a stable case identifier for each scalar, composite and advanced type, and legal nested combinations. Run each valid fixture as argument, return value, record field, collection element and async result where its lifetime allows it. Test both native-to-managed and managed-to-native implementations; then the supported non-C++ pairs. Reject forbidden borrowed-view escapes, invalid ranges, unknown tags and unsupported external mappings. No backend may mark a type supported just because it can generate a declaration.

## 6. Modules and dependencies

### 6.1 Example application layout

```text
my-project/
├── polyglue.yaml
├── modules/
│   ├── domain/
│   │   ├── module.yaml
│   │   └── idl/
│   │       ├── user.idl
│   │       └── product.idl
│   ├── repository/
│   │   ├── module.yaml
│   │   └── idl/
│   │       ├── user_repository.idl
│   │       └── product_repository.idl
│   └── network/
│       ├── module.yaml
│       └── idl/
│           └── http_client.idl
├── native/
├── android/
├── apple/
├── python/
├── dotnet/
├── flutter/
└── web/
```

A module is the fundamental unit of compilation, dependency resolution, generation and distribution. A project is a convenient collection of modules and shared defaults, not a mandatory monolithic input.

### 6.2 Independent dependencies

```yaml
dependencies:
  domain:
    path: ../shared-domain/module.yaml
    mode: source
  networking:
    path: ../shared-networking/polyglue-manifest.json
    mode: prebuilt
```

| Mode | Behavior |
| --- | --- |
| source | Resolve IDL and generate required target dependencies |
| prebuilt | Reuse validated generated artifacts and contract metadata without regenerating |

A prebuilt manifest includes enough canonical contract information to resolve imported symbols (not just hashes), plus public include/import locations and ABI compatibility information. Validate actual artifacts, dependency closure and versions. Do not duplicate imported types.

Use module logical identity independent of physical directory, output names and version. Version changes must not silently change the identity of a compatible type. Distinguish semantic identity, contract fingerprint and target ABI fingerprint.

### 6.3 Manifest

```json
{
  "schema_version": 1,
  "generator_version": "1.0.0",
  "runtime_abi_version": 1,
  "module": {
    "id": "domain",
    "version": "1.0.0"
  },
  "symbols": {
    "domain.User": {
      "kind": "record",
      "targets": {
        "cpp": {
          "name": "app::domain::User",
          "file": "include/app/domain/user.hpp",
          "import": "app/domain/user.hpp"
        },
        "dart": {
          "name": "User",
          "package": "app_domain",
          "file": "lib/src/user.dart",
          "import": "package:app_domain/app_domain.dart"
        }
      }
    }
  }
}
```

Illustrative excerpt; the full schema must include canonical type definitions, real fingerprints, dependency versions, architecture-specific ABI information, effective naming/layout metadata, generated-file ownership and content hashes. Validate the manifest schema and reject missing required information. Never emit fake fingerprints.

### 6.4 Acceptance tests

- Generate domain and repository together and separately, using source and prebuilt dependencies.
- Import a type by alias, grouped import and wildcard; detect ambiguity.
- Change a domain output path, prefix or package and regenerate repository imports correctly.
- Reject incompatible duplicates, missing targets, invalid cycles, incompatible manifests and unavailable generated artifacts.
- Confirm that identical logical symbols have stable identity regardless of casing or path.

## 7. Module-first configuration

### 7.1 Precedence and semantics

From lowest to highest priority:

1. Built-in generator defaults.
2. Project-wide defaults.
3. Module-wide defaults.
4. Target settings inside that module.
5. Declaration annotations for supported properties.

Project defaults may include target-specific defaults. Merge mappings recursively; scalar and list values replace inherited values unless explicitly documented otherwise. Missing values inherit; null is only valid for nullable options. Unknown keys, conflicting options and invalid types fail validation. Relative paths resolve from the file that originally declares them, even after inheritance. Source roots and authorized output roots are distinct; external output paths are allowed when explicitly configured, but traversal outside the configured output root and unintended symlink writes are forbidden.

### 7.2 Global configuration

`polyglue.yaml`:

```yaml
project:
  name: application
  version: "1.0.0"

modules:
  - modules/domain/module.yaml
  - modules/repository/module.yaml
  - modules/network/module.yaml

defaults:
  generation:
    encoding: utf-8
    line_endings: lf
    generated_warning: true
    deterministic: true
  targets:
    cpp:
      standard: 20
      naming:
        types: PascalCase
        methods: camelCase
        fields: camelCase
        files: snake_case
    objc:
      arc: true
      nullability: true
      swift_names:
        enabled: true
    swift:
      native_async: true
      strict_concurrency: true
    dart:
      naming:
        types: PascalCase
        methods: camelCase
        files: snake_case
```

Global defaults must not enable undeclared targets automatically. Each module explicitly selects its outputs.

### 7.3 Domain module configuration

`modules/domain/module.yaml`:

```yaml
module:
  name: domain
  version: "1.0.0"

sources:
  - idl/**/*.idl

targets:
  c:
    output: ../../native/domain/c
    prefix: app_domain_
  cpp:
    output: ../../native/domain/cpp
    namespace: app::domain
    include_prefix: app/domain
    header_extension: hpp
    source_extension: cpp
  java:
    output: ../../android/generated/domain/java
    package: com.app.domain
  kotlin:
    output: ../../android/generated/domain/kotlin
    package: com.app.domain
    model_source: java
  objc:
    output: ../../apple/Domain/ObjC
    prefix: DOM
    module: AppDomainObjC
  swift:
    output: ../../apple/Domain/Swift
    module: AppDomain
    model_source: objc
  dart:
    output: ../../flutter/packages/domain
    package: app_domain
    mode: package
  python:
    output: ../../python/domain
    package: app_domain
  csharp:
    output: ../../dotnet/Domain
    namespace: App.Domain
    assembly: App.Domain
  javascript:
    output: ../../web/domain
    module: "@app/domain"
  typescript:
    output: ../../web/domain
    module: "@app/domain"
    implementation_source: javascript
  wasm:
    output: ../../native/domain/wasm
```

The illustrative model_source/implementation_source settings express intentional artifact sharing. The backend must validate them, emit only the required artifacts, and provide the equivalent native APIs. If independent Java and Kotlin classes are required, configure distinct packages. If independent Swift models are needed, use non-conflicting modules/names. JavaScript and TypeScript outputs may share a package only when their planned filenames and export contracts do not conflict.

### 7.4 Repository module configuration

`modules/repository/module.yaml`:

```yaml
module:
  name: repository
  version: "1.0.0"

sources:
  - idl/**/*.idl

dependencies:
  domain:
    path: ../domain/module.yaml
    mode: source

targets:
  c:
    output: ../../native/repository/c
    prefix: app_repo_
  cpp:
    output: ../../native/repository/cpp
    namespace: app::repository
    include_prefix: app/repository
  java:
    output: ../../android/generated/repository/java
    package: com.app.repository
  kotlin:
    output: ../../android/generated/repository/kotlin
    package: com.app.repository
    model_source: java
  objc:
    output: ../../apple/Repository/ObjC
    prefix: REP
    module: AppRepositoryObjC
  swift:
    output: ../../apple/Repository/Swift
    module: AppRepository
  dart:
    output: ../../flutter/packages/repository
    package: app_repository
    mode: package
  flutter:
    output: ../../flutter/plugins/repository
    package: app_repository_plugin
  python:
    output: ../../python/repository
    package: app_repository
  csharp:
    output: ../../dotnet/Repository
    namespace: App.Repository
    assembly: App.Repository
  javascript:
    output: ../../web/repository
    module: "@app/repository"
  typescript:
    output: ../../web/repository
    module: "@app/repository"
    implementation_source: javascript
  wasm:
    output: ../../native/repository/wasm
```

### 7.5 Network module configuration

`modules/network/module.yaml`:

```yaml
module:
  name: network
  version: "1.0.0"

sources:
  - idl/**/*.idl

targets:
  c:
    output: ../../native/network/c
    prefix: app_net_
  cpp:
    output: ../../native/network/cpp
    namespace: app::network
    include_prefix: app/network
  java:
    output: ../../android/generated/network/java
    package: com.app.network
  kotlin:
    output: ../../android/generated/network/kotlin
    package: com.app.network
    model_source: java
  objc:
    output: ../../apple/Network/ObjC
    prefix: NET
    module: AppNetworkObjC
  swift:
    output: ../../apple/Network/Swift
    module: AppNetwork
  dart:
    output: ../../flutter/packages/network
    package: app_network
    mode: package
  flutter:
    output: ../../flutter/plugins/network
    package: app_network_plugin
  python:
    output: ../../python/network
    package: app_network
  csharp:
    output: ../../dotnet/Network
    namespace: App.Network
    assembly: App.Network
  javascript:
    output: ../../web/network
    module: "@app/network"
  typescript:
    output: ../../web/network
    module: "@app/network"
    implementation_source: javascript
  wasm:
    output: ../../native/network/wasm
```

None of these choices is imposed on domain or repository.

### 7.6 Configuration schema coverage

| Category | Required options |
| --- | --- |
| Sources | IDL roots/globs, dependencies, external manifests |
| Paths | Output root, headers, sources, public/private paths, runtime location |
| Naming | Per-category case, prefix, suffix, acronym policy |
| Namespace | C++, C# |
| Package | Java, Kotlin, Python, Dart, Flutter |
| Module | Swift, Objective-C, JS/TS |
| Assembly | C# |
| Imports | Public import path, include prefix, strategy, module maps, exports |
| Templates | Override directory and fallback policy |
| Formatting | Indentation, line endings, final newline, brace style where supported |
| Annotations | Defaults, automatic attributes, target-specific overrides |
| Visibility | Exported/public/private/internal symbols |
| Availability | Platforms, SDK minimums and capability checks |
| Build | Sources or package mode; platform build settings |
| Runtime | Shared runtime integration and supported version |
| ABI | Version and binary contract checks |
| Documentation | Comments and generated API docs |
| Headers | License, copyright, generated warning, version and source metadata |

Define a machine-readable schema with examples and reject unknown options. Do not invent settings without implementing their semantics. Test inherited defaults, module-only generation, target-specific overrides and invalid combinations.

### 7.7 Build and product configuration

A module remains the unit of code generation. A product is an explicit aggregation of already-defined modules for linking, packaging and distribution. A product is not another IDL namespace and never overrides a module's public names or type identity. This is necessary when domain, repository and network belong to one AAR or XCFramework, or when a reusable module is shipped independently.

Module-level build settings configure integration, not global compiler installation:

```yaml
targets:
  cpp:
    output: ../../native/repository/cpp
    namespace: app::repository
    include_prefix: app/repository
    mode: package
    build:
      library_name: app_repository
      linkage: static
      public_headers: include
      private_sources: src
      implementation_sources:
        - ../../native/implementations/repository.cpp
      dependencies:
        - app_domain
  kotlin:
    output: ../../android/generated/repository/kotlin
    package: com.app.repository
    model_source: java
    build:
      android_namespace: com.app.repository
      consumer_rules: ../../android/consumer-rules.pro
```

Illustrative project-level products in polyglue.yaml (in addition to modules and defaults from section 7.2):

```yaml
build:
  root: build/polyglue
  artifacts: dist
  configuration: release
  dependency_provider: cmake

products:
  mobile:
    modules: [domain, repository, network]
    targets: [c, cpp, java, kotlin]
    artifact:
      format: aar
      name: app_bridge
      version: "1.0.0"
    platforms:
      android:
        min_sdk: 26
        abis: [arm64-v8a, armeabi-v7a, x86_64]

  apple:
    modules: [domain, repository, network]
    targets: [c, cpp, objc, swift]
    artifact:
      format: xcframework
      name: AppBridge
      version: "1.0.0"
    platforms:
      ios:
        minimum_version: "17.0"
        device_architectures: [arm64]
        simulator_architectures: [arm64, x86_64]
      macos:
        minimum_version: "14.0"
        architectures: [arm64, x86_64]
      visionos:
        minimum_version: "1.0"
        device_architectures: [arm64]
        simulator_architectures: [arm64]

  desktop:
    modules: [domain, repository, network]
    targets: [c, cpp]
    artifact:
      format: cmake
      name: AppBridge
      version: "1.0.0"
    platforms:
      linux:
        architectures: [x86_64, arm64]
      windows:
        architectures: [x86_64, arm64]
      macos:
        architectures: [arm64, x86_64]
```

SDK floors and architectures above are illustrative choices, not a verified toolchain matrix. The tool checks whether the installed SDK can build each requested slice; it must not silently remove an unavailable slice. Product manifests declare the exact module closure, native implementation sources, runtime linkage, requested output format and target/architecture matrix. Product packaging can select source or prebuilt modules, with strict compatibility validation. Separate product output roots prevent cross-product contamination. A source-only project never has to declare products.

Dependency names in native build configuration refer to explicitly declared CMake targets, not arbitrary flags. IDL dependencies and native build dependencies are distinct. Module output paths, native implementation source paths, SDK settings, extra includes and link libraries are schema-validated. Accept additional CMake integration via an explicit, trusted consumer CMake target or source list; no arbitrary shell execution from IDL.

## 8. Naming and file formatting

### 8.1 Naming categories and defaults

| Target | Types | Methods | Fields | Files |
| --- | --- | --- | --- | --- |
| C | snake_case | snake_case | snake_case | snake_case |
| C++ | PascalCase | snake_case | snake_case | snake_case |
| Java / Kotlin | PascalCase | camelCase | camelCase | PascalCase |
| Swift | PascalCase | camelCase | camelCase | PascalCase |
| Objective-C | prefixed PascalCase | camelCase | camelCase | PascalCase |
| Python | PascalCase | snake_case | snake_case | snake_case |
| Dart / Flutter | PascalCase | camelCase | camelCase | snake_case |
| C# | PascalCase | PascalCase | PascalCase | PascalCase |
| JS / TS | PascalCase | camelCase | camelCase | kebab-case |

These are defaults, not mandatory language standards. Support PascalCase, camelCase, snake_case, SCREAMING_SNAKE_CASE, kebab-case, lowercase, UPPERCASE and dot-separated paths where legal. Configure types, records, interfaces, methods, async methods, fields, parameters, constants, enum values, files, namespaces, packages, private fields and proxy names independently.

### 8.2 Prefixes and suffixes per module and category

Within domain:

```yaml
targets:
  objc:
    prefix: DOM
    naming:
      records:
        prefix: DOM
        case: PascalCase
      interfaces:
        prefix: DOM
        suffix: Protocol
        case: PascalCase
      enums:
        prefix: DOM
        case: PascalCase
      proxies:
        prefix: DOM
        suffix: Proxy
      files:
        case: PascalCase
    swift_names:
      enabled: true
      remove_prefix: true
      remove_suffix: true
```

Repository can independently use REP and an interface suffix such as Protocol. With that optional override applied in repository as well:

| IDL | Objective-C | Swift public name |
| --- | --- | --- |
| domain.User | DOMUser | User |
| domain.UserStatus | DOMUserStatus | UserStatus |
| repository.UserRepository | REPUserRepositoryProtocol | UserRepository |

A category-specific prefix replaces the target-wide prefix; it is not concatenated twice. For source filenames derive names from the final emitted symbol unless explicitly configured otherwise. An imported type always uses the defining module's resolved name, never the consuming module's prefix.

C# configuration example:

```yaml
targets:
  csharp:
    naming:
      types: PascalCase
      interfaces:
        case: PascalCase
        prefix: I
      methods: PascalCase
      parameters: camelCase
      async_methods:
        suffix: Async
```

### 8.3 Acronyms, reserved words and collisions

```yaml
naming:
  acronyms:
    - HTTP
    - URL
    - UUID
    - ID
    - GPU
    - XML
    - JSON
    - API
    - RGBA
    - IPv6
```

Define normalization and preservation policies per target. Test HTTPClient, XMLParser, getUserID, GPUTexture2D, URLRequest and IPv6Address. Expected normalized examples: httpClient / http_client, getUserId / get_user_id, gpuTexture2D / gpu_texture_2d.

Handle reserved words through legal escaping where appropriate (Swift/Kotlin backticks, C# @identifier) or configured suffixes. Detect collisions after all conversions, including user_id vs userId, generated proxies vs user types, Unicode/case-folded filenames, Java/Kotlin duplicate JVM types and reserved Windows filenames. Fail with both source locations. Never silently rename public symbols to resolve an ambiguity.

### 8.4 Formatting and headers

```yaml
targets:
  cpp:
    formatting:
      indent: 4
      indent_style: spaces
      line_length: 100
      brace_style: allman
      line_endings: lf
      final_newline: true
    file_header:
      copyright: "Copyright (c) 2026 Example"
      license: MIT
      generated_warning: true
      include_generator_version: true
      include_source_path: true
      include_timestamp: false
```

Generate deterministic UTF-8 text, ordered and deduplicated imports, appropriate documentation comments and no timestamps by default. Default formatting must be readable without external tools. Optional formatters: clang-format, google-java-format, ktlint, swift-format, Ruff, dart format, dotnet format, Prettier. Only advertise options a backend actually honors. Test custom formatting, output byte reproducibility and unchanged-file preservation.

## 9. Annotations and platform attributes

### 9.1 Universal annotations

```text
@deprecated("Use UserProfile instead")
record User {
    @readonly
    id: int64;
    name: string;
}

interface Camera {
    @thread("main")
    async start(): void;
}
```

Universal annotations carry defined semantic meaning. An executor/thread annotation must affect dispatch, not just comments. Readonly semantics must be enforced by generated APIs and runtime where required. Availability and ownership constraints cannot be overridden by an unsafe target-specific annotation.

### 9.2 Language-specific annotations

```text
@objc.name("DOMUser")
@swift.name("User")
@csharp.name("UserModel")
record User {
    @swift.name("userID")
    @kotlin.name("userId")
    id: int64;
}
```

```text
@platform.apple(ios: "17.0", macos: "14.0", visionos: "1.0")
interface SpatialRenderer {
    @swift.main_actor
    @objc.selector("initializeWithCompletion:")
    async initialize(): void;
}
```

Annotations are allowed on modules, records, interfaces, enums, enum members, fields, methods, parameters, callbacks and constants where their registered schema permits. Validate argument count/type, duplicates, placement, conflicts and target availability. An unknown annotation is an error even if its namespace is not selected. Known annotations for non-selected targets may be validated and ignored for rendering.

### 9.3 Apple interop details

| Mechanism | Purpose |
| --- | --- |
| @objc / @objcMembers / @nonobjc | Objective-C exposure from Swift |
| NS_SWIFT_NAME / CF_SWIFT_NAME | Explicit names imported into Swift |
| NS_REFINED_FOR_SWIFT | Wrapper refinement |
| NS_SWIFT_UNAVAILABLE | Prevent import where appropriate |
| NS_SWIFT_ASYNC / NS_SWIFT_ASYNC_NAME | Async import customization |
| NS_SWIFT_SENDABLE / @MainActor | Concurrency metadata only when valid |
| @available | OS and SDK availability, including visionOS |
| NS_ASSUME_NONNULL_BEGIN / _Nullable / _Nonnull | Nullability |
| NS_ENUM / NS_OPTIONS | Swift-friendly enum and flags |
| NS_DESIGNATED_INITIALIZER / NS_UNAVAILABLE | Initialization contract |
| @discardableResult | Intentional result-discard support |

Automatically infer safe attributes from IDL when possible; annotations override naming or supported metadata, not safety rules.

Illustrative Objective-C output for a reduced User record (id, name and optional email):

```objc
#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

NS_SWIFT_NAME(User)
@interface DOMUser : NSObject
@property(nonatomic, readonly) int64_t userId;
@property(nonatomic, copy, readonly) NSString *name;
@property(nonatomic, copy, readonly, nullable) NSString *email;

- (instancetype)initWithUserId:(int64_t)userId
                          name:(NSString *)name
                         email:(nullable NSString *)email
    NS_DESIGNATED_INITIALIZER
    NS_SWIFT_NAME(init(id:name:email:));
- (instancetype)init NS_UNAVAILABLE;
@end

NS_ASSUME_NONNULL_END
```

Swift consumption:

```swift
let user = User(id: 10, name: "John", email: nil)
```

For a repository async method, generate a compatible Objective-C completion API and NS_SWIFT_ASYNC_NAME when supported by the selected SDK; otherwise generate an explicit Swift async wrapper. Test both nullability and the difference between a valid absent optional result and a runtime failure. Compile actual Swift imports, not just macro strings. Test selector conflicts and exposure restrictions (not every Swift type is representable in Objective-C).

### 9.4 Other backend attributes

| Target | Examples |
| --- | --- |
| Kotlin | JvmName, JvmStatic, JvmOverloads where valid |
| Java | Nullable, NonNull, Deprecated |
| C/C++ | symbol visibility, calling convention, nodiscard, deprecated, noexcept when guaranteed |
| C# | StructLayout, LibraryImport, MarshalAs |
| Python | typing, property, staticmethod |
| Dart | Native / pragma where appropriate, immutable |
| TypeScript | readonly, JSDoc deprecated |
| WASM | Export and visibility controls |

Backend catalog defines exact supported annotations and transformations. Do not allow arbitrary raw code injection as the default annotation mechanism.

## 10. Output layout and import resolution

### 10.1 Logical versus physical identity

| Concept | Example |
| --- | --- |
| IDL symbol | domain.User |
| C++ symbol | app::domain::User |
| C++ public include | app/domain/user.hpp |
| Java/Kotlin type | com.app.domain.User |
| Objective-C type | DOMUser |
| Swift module/type | AppDomain.User |
| Dart public import | package:app_domain/app_domain.dart |
| Python import | app_domain.User |
| C# namespace/type | App.Domain.User |

Plan all generated symbols before rendering any file. The repository refers to the defining domain module's planned artifacts, including prebuilt manifests, not a guessed relative path.

### 10.2 Expected cross-module output

For the repository contract in section 4:

**C**

```c
#include <app/domain/user.h>
#include <polyglue/runtime.h>

/* Illustrative names; final signatures follow the versioned C ABI. */
typedef struct app_repo_user_repository app_repo_user_repository;
```

**C++**

```cpp
#include <app/domain/user.hpp>
#include <polyglue/future.hpp>
#include <cstdint>
#include <optional>
#include <vector>

namespace app::repository {
class UserRepository {
public:
    virtual ~UserRepository() = default;
    virtual polyglue::Future<std::vector<app::domain::User>> findAll() = 0;
    virtual polyglue::Future<std::optional<app::domain::User>>
        findById(int64_t id) = 0;
};
}
```

**Kotlin**

```kotlin
package com.app.repository

import com.app.domain.User

interface UserRepository {
    suspend fun findAll(): List<User>
    suspend fun findById(id: Long): User?
}
```

**Java**

```java
package com.app.repository;

import com.app.domain.User;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public interface UserRepository {
    CompletableFuture<List<User>> findAll();
}
```

Java/Kotlin examples illustrate alternative standalone API surfaces; if both are selected for one JVM, choose a shared contract and non-conflicting wrapper names. Do not compile these two same-name interface examples together.

**Objective-C**

```objc
@import Foundation;
@import AppDomainObjC;

NS_SWIFT_NAME(UserRepository)
@protocol REPUserRepository
- (void)findAllWithCompletion:
    (void (^)(NSArray<DOMUser *> * _Nullable,
              NSError * _Nullable))completion;
@end
```

**Swift**

```swift
import AppDomain

public protocol UserRepository {
    func findAll() async throws -> [User]
    func findById(id: Int64) async throws -> User?
}
```

**Dart**

```dart
import 'package:app_domain/app_domain.dart';

abstract interface class UserRepository {
  Future<List<User>> findAll();
  Future<User?> findById(int id);
}
```

**Python**

```python
from abc import ABC, abstractmethod
from app_domain import User


class UserRepository(ABC):
    @abstractmethod
    async def find_all(self) -> list[User]: ...
```

**C#**

```csharp
using App.Domain;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace App.Repository;

public interface IUserRepository
{
    Task<List<User>> FindAllAsync();
}
```

**TypeScript**

```typescript
import type { User } from "@app/domain";

export interface UserRepository {
    findAll(): Promise<User[]>;
    findById(id: bigint): Promise<User | null>;
}
```

These excerpts show public contract shape; generated proxies, C ABI declarations, converters, initialization and all remaining methods are required separately.

### 10.3 Generated directory examples

```text
native/domain/cpp/
├── include/app/domain/user.hpp
└── src/user.cpp

native/repository/cpp/
├── include/app/repository/user_repository.hpp
└── src/user_repository.cpp

android/generated/domain/java/
└── com/app/domain/User.java

android/generated/repository/kotlin/
└── com/app/repository/UserRepository.kt

apple/Domain/
├── ObjC/
│   ├── include/DOMUser.h
│   └── module.modulemap
└── Swift/
    └── Sources/AppDomain/

apple/Repository/Swift/
└── Sources/AppRepository/UserRepository.swift

flutter/packages/domain/
├── pubspec.yaml
└── lib/
    ├── app_domain.dart
    └── src/user.dart

flutter/packages/repository/
├── pubspec.yaml
└── lib/
    ├── app_repository.dart
    └── src/user_repository.dart

python/domain/
└── app_domain/
    ├── __init__.py
    └── user.py

dotnet/Domain/
├── App.Domain.csproj
└── User.cs

web/domain/
├── package.json
└── src/user.js
```

These trees illustrate public artifacts, not exhaustive bridge sources. The domain package must expose User through its public entry point. The repository package declares the dependency in its package/build manifest in package mode.

### 10.4 Target artifact rules

| Backend | Layout / imports / package files |
| --- | --- |
| C | Public .h, sources, include guards, C names and calling convention |
| C++ | include/ and src/, namespace, includes/forward declarations, CMake |
| Java/Kotlin/JNI | Package directory tree, JVM type ownership, JNI names, Gradle |
| Swift | Sources/<target>, module imports only between distinct modules, Package.swift |
| Objective-C | Prefixed public headers, umbrella header/module.modulemap, .mm sources |
| Python | Package tree, __init__.py, public exports, pyproject.toml |
| Dart | lib/src, public library exports, pubspec.yaml |
| Flutter | Plugin metadata, Dart package and platform adapters |
| C# | Namespace, project/assembly references, .csproj |
| JS/TS | ES module exports/imports, package.json, .d.ts and tsconfig as appropriate |
| WASM | Emscripten build configuration, exports and JS loader |

Provide sources mode (integrate into existing build) and package mode (standalone buildable package). Paths, filenames, extensions and public import strings are separately configurable. Do not overwrite consumer-owned build files. Test both modes, separate source roots and external dependencies, same-module Swift imports, Python circular imports, C++ forward declarations and package export validity.

## 11. Compiler and templates

### 11.1 Pipeline

```text
Project and module configuration
              |
     Source discovery / parser
              |
         AST + source spans
              |
    Symbol table / semantic resolver
              |
        Canonical typed IR
              |
    Target naming and output planner
              |
     Import / dependency resolver
              |
     Target-specific render models
              |
          Jinja2 templates
              |
      Validated output file plan
              |
     Atomic writes + manifest
```

### 11.2 Responsibilities

| System | Responsibility |
| --- | --- |
| Project / Module | Inputs and independent generation units |
| Configuration | Schema, inheritance and effective settings |
| Type / Symbol | Canonical identities and validated type graph |
| Dependency | Source and prebuilt graph resolution |
| Naming | Case, prefixes, suffixes, acronyms, escaping |
| Layout | Physical paths and public artifact names |
| Imports | Includes/imports/forward declarations/export maps |
| Annotation | Semantic and target-specific attributes |
| Backend | Type mapping, capabilities, render models, marshalling |
| Template | Presentation only |
| Diagnostic | Actionable errors and source spans |
| Manifest | Contract metadata and generated-file ownership |
| ABI / Runtime | Native interoperability and lifetime |
| Service | Optional lookup and replacement |
| Testing | Conformance and regression evidence |

### 11.3 Backend shape

```python
from typing import Protocol


class LanguageBackend(Protocol):
    def plan_outputs(self, module, context): ...
    def resolve_symbol(self, symbol, context): ...
    def resolve_type(self, type_ref, context): ...
    def resolve_import(self, source, dependency, context): ...
    def build_render_models(self, module, context): ...
```

The protocol is illustrative; freeze actual interfaces with tests. Keep the implementation small and share only genuinely common logic. Each backend owns naming, types, imports, layout, annotations, marshalling and templates. Plugins via Python entry points are explicit trusted opt-in, not necessary for built-in targets.

Template example:

```jinja2
package {{ package }}

{% for dependency in imports %}
import {{ dependency }}
{% endfor %}

interface {{ interface.name }} {
{% for method in interface.methods %}
    {{ method.declaration }}
{% endfor %}
}
```

Template override:

```yaml
targets:
  cpp:
    templates:
      directory: ./custom/templates/cpp
      fallback_to_builtin: true
```

Use StrictUndefined. All imports/types/names are resolved in Python before rendering. Custom template selection and resource paths must be validated. Templates and plugins are trusted developer code; never load them implicitly from untrusted IDL.

### 11.4 Generation guarantees

Validate the whole output plan before writing. Reject overlapping files, collisions on case-insensitive systems, invalid path components and symlink escapes. Write changed files atomically; if a multi-file write fails, report partial state and do not publish a success manifest. Do not rewrite identical files or delete user-authored files. Only remove obsolete manifest-owned generated files when explicitly requested. Test failure recovery, deterministic generation and standalone installation.

### 11.5 Template override system (mandatory)

Template override support is a first-class public feature, not a fork-only customization. All files generated from templates must have stable, documented template IDs: public models, enums, variants, interfaces, callbacks, proxies, provider adapters, ABI glue, marshallers, module exports, package metadata, CMake integration, Gradle files, SwiftPM files, Dart/Flutter integration, .NET project files and JS/TS exports. Runtime source files are separately versioned handwritten code, not implicitly replaced by a template.

A default built-in template catalog is packaged with the Python wheel. Each entry declares target, ID, output kind, render-model schema version, required variables and related partials. IDs are independent of target filenames, module prefixes and physical output directories. Names below define a proposed initial catalog convention:

```text
templates/
├── common/
│   └── file_header.j2
├── cpp/
│   ├── record.hpp.j2
│   ├── interface.hpp.j2
│   ├── proxy.cpp.j2
│   ├── provider.cpp.j2
│   └── CMakeLists.txt.j2
├── kotlin/
│   ├── record.kt.j2
│   ├── interface.kt.j2
│   └── build.gradle.kts.j2
├── objc/
│   ├── record.h.j2
│   └── module.modulemap.j2
└── swift/
    ├── interface.swift.j2
    └── Package.swift.j2
```

Actual catalog covers all targets; do not create redundant placeholder templates. Reusable macros and partials are allowed when they simplify rendering.

#### 11.5.1 Directory override and individual override

```yaml
defaults:
  targets:
    cpp:
      templates:
        directory: ./templates/cpp
        fallback_to_builtin: true
```

```yaml
# modules/repository/module.yaml
targets:
  cpp:
    templates:
      directory: ./templates/cpp
      overrides:
        interface.hpp.j2: ./templates/special/repository_interface.j2
        CMakeLists.txt.j2: ./templates/special/repository_cmake.j2
      fallback_to_builtin: true
```

Only matching template IDs are overridden; all other files use the next permitted layer. A module-specific directory need not duplicate the complete built-in tree. Resolve lookup per ID: explicit mapping in module target, module target directory, module-wide inherited mapping/directory, project target defaults, project-wide defaults, then built-in catalog. Explicit mapping takes precedence over directory lookup at the same layer. Preserve path origin at each layer rather than flattening inherited directories into one. A configured fallback_to_builtin: false disallows use of the built-in catalog for that target's effective set; missing required templates fail before any outputs are written. A missing explicitly mapped file always fails, even if fallback is enabled. Validate unknown IDs and conflicting overrides.

#### 11.5.2 Custom template workflow

```bash
polyglue templates list --target cpp
polyglue templates export --target cpp --output ./templates/cpp
polyglue templates check --module repository --target cpp
polyglue config show --module repository --target cpp
polyglue generate --module repository --target cpp
```

Export does not overwrite existing custom files without explicit authorization. The check command renders against real validated IR fixtures or the selected project; show syntax errors, missing variables, incompatible schema versions, unknown IDs and the originating config/template path. Report effective template source and content hash in the generation manifest, including transitive include/import/extends dependencies. Changes invalidate incremental build and generation fingerprints.

#### 11.5.3 Render context and safety

Publish a versioned render-model contract with examples for every public template. Backend code supplies names, includes/imports, type declarations, annotations, ownership and ABI-specific render metadata; Jinja2 is presentation, not a second semantic compiler. StrictUndefined, deterministic rendering, documented filters/macros and no implicit environment or timestamp dependence. Use a restricted filesystem loader with explicit roots, normalized relative IDs and no traversal/symlink escape. Templates may reference catalog partials through a documented namespace or allowed relative ID; prevent accidental recursive inclusion and report its chain.

Custom templates are trusted local developer input, not a security sandbox. A template cannot declare a new output path, change the validated file plan or bypass capability/ABI validation. Runtime source replacement requires an explicit separate runtime integration and compatibility checks. A custom template that changes ABI-visible code must be validated by downstream compilation and ABI checks; do not certify arbitrary overrides based on rendering alone.

#### 11.5.4 Acceptance tests

- Single-file override retains all other built-ins; partial override and multiple modules with different overrides.
- Project/module precedence, correct relative paths, strict missing template behavior, duplicate/unknown ID and fallback disabled.
- Override of nested partials and generated build files; stable manifest fingerprints and invalidation when content changes.
- Syntax error, undefined variables, context schema mismatch, traversal, recursive inclusion and deterministic rerender.
- Generated outputs compile and run in each target, including an actual package consumer using customized source/build templates.
- Wheel installation includes the same template catalog, export/check commands and behavior as a source checkout.

## 12. Native runtime and ABI

The support runtime implements only shared interoperability mechanics, while generated adapters provide contract-specific behavior.

Required ABI rules:

- Versioned C ABI with fixed-width primitives, explicit alignment, size/version headers and documented calling conventions.
- Stable logical type IDs distinct from contract fingerprints and target-specific ABI fingerprints.
- Validate architecture, ABI version, handle origin, kind and generation before invocation.
- Explicit ownership for every argument and return, allocator/deallocator pairing and checked length/offset arithmetic.
- No C++ STL layout, foreign object memory layout or exception crossing the ABI directly.
- One compatible shared runtime per context; detect unintended duplicate instances.
- Explicit close/dispose and safe finalizer fallback. Never rely on finalizers alone.
- Define identity, strong and weak references, refcount overflow, cycles and thread-affine destruction.

Buffer-specific rules are in section 13; asynchronous lifecycle rules are in section 14.

### 12.1 Typed function tables

A generated interface adapter holds a typed table of functions, an opaque context and lifetime operations. Foreign objects are never interpreted directly by another language. As an illustrative C ABI shape:

```c
typedef struct {
    uint32_t abi_version;
    uint32_t struct_size;
    void *context;
    void (*retain)(void *context);
    void (*release)(void *context);
    void (*request)(
        void *context,
        const pg_http_request *input,
        pg_http_completion completion,
        void *completion_context
    );
} pg_http_client_vtable;
```

The final ABI must define calling convention, status propagation, context validity, ownership of input/output, cancellation and completion lifetime before implementation. This is a conceptual table, not a finalized header.

A JNI adapter's context owns a global Java object reference; a Swift adapter owns an ARC-managed object; a Dart adapter owns an isolate-bound registration. The generated native adapter invokes the correct runtime's method. Direct references and registry lookups reuse the same mechanism.

### 12.2 Runtime lifecycle

One runtime instance per explicitly shared context. Multiple libraries must link to the same intended context. Use opaque generation-checked handles; validate handle kind, generation, origin and ABI. Pair allocators and deleters. No managed object pointer, C++ STL layout or exception crosses the C ABI directly.

Do not hold internal locks during foreign calls, callbacks, scheduling or destruction. Define shutdown ordering, pending-operation drain/cancellation, registration invalidation and thread-affine release. Test reentrancy, nested cross-language calls, duplicate runtime instances, stale handles, allocator mismatch, refcount overflow, weak references and shutdown races.

## 13. Memory and buffers

### 13.1 Contracts

| Type | Ownership | Copy policy | Allowed lifetime |
| --- | --- | --- | --- |
| bytes | Independent value | Explicit copy | Independent |
| DataView | Borrowed read-only | No implicit copy | Scoped synchronous access |
| MutableDataView | Exclusive borrowed write | No implicit copy | Scoped synchronous access |
| DataRef | Shared owned buffer | No implicit copy | Until last owning reference is released |

```text
interface ImageProcessor {
    process(data: DataView): DataRef;
    processInPlace(data: MutableDataView): void;
    async processAsync(data: DataRef): DataRef;
}
```

Borrowed views may not escape the validated synchronous scope. Reject borrowed returns, storage in escaping records/collections and async arguments when no safe lifetime can be established. Managed wrappers must provide checked scoped access; unsafe raw pointer escapes are explicitly outside safe guarantees. Mutable views require exclusive access.

DataRef retains the true owner, including for subranges; last release executes the correct deleter once on an appropriate executor. Default shared access is read-only. Explicit conversion to bytes copies; unsupported shared memory conversions must fail or request an explicit copy rather than silently copying.

### 13.2 Target representation examples

| Target | Borrowed / shared representation |
| --- | --- |
| C | Pointer + length scoped view; opaque owning handle |
| C++ | span-like view; RAII reference |
| Java/Kotlin | Scoped direct ByteBuffer wrapper; retained owner |
| Swift | Scoped UnsafeRawBufferPointer access; owner object |
| Obj-C | Scoped NSData-compatible access; retained wrapper |
| Python | Scoped buffer access / memoryview with correct exporter lifetime |
| Dart | Checked native view and owned FFI reference |
| C# | Span-like scoped access; SafeHandle/owner for shared data |
| JS/TS/WASM | Checked view of linear memory; lease or reacquire after memory growth |

A typed array in a JS heap is not automatically shared with WASM. Direct JVM buffers, GC pinning, Python buffer exporters, Dart finalizers and camera/GPU surfaces require specific lifetimes. Do not claim zero-copy when memory placement or runtime capabilities prevent it.

### 13.3 Test evidence

Test empty and large buffers, invalid lengths, overflow, slices, misalignment where typed access applies, concurrent release, source destruction while DataRef remains alive, use after view scope, double release, aliasing, mutable borrow conflicts, allocator matching and thread-affine deleters. Verify identity and exact contents across compatible boundaries. Instrument bytes copied, allocations/deallocations, handles and outstanding operations; instrumentation must not claim visibility into all third-party runtime allocations.

## 14. Asynchronous operations callbacks and streams

### 14.1 Async and futures

```text
interface HttpClient {
    async request(input: HttpRequest): HttpResponse;
}
```

Async declares a potentially pending operation. Future/Task/Promise represent its result in a target runtime; await waits without inherently creating a thread. No mandatory Future syntax in IDL.

```cpp
auto response = co_await client->request(request);
```

```kotlin
val response = client.request(request)
```

```swift
let response = try await client.request(request)
```

```dart
final response = await client.request(request);
```

```csharp
var response = await client.RequestAsync(request);
```

```python
response = await client.request(request)
```

### 14.2 Callback contract

```text
callback Progress(received: int64, total: int64): void;

interface Downloader {
    async download(
        url: string,
        progress: Progress,
        cancellation: CancellationToken
    ): DataRef;
}
```

Callbacks are typed, can cross languages, and have documented scoped/retained/one-shot lifetimes. Specify executor, ordering, error handling and whether completion is synchronous or asynchronous. Synchronous callbacks returning values cannot be promised from arbitrary foreign threads into Dart isolates or other event-loop-bound runtimes.

### 14.3 Streams

```text
interface Camera {
    async start(): void;
    async stop(): void;
    frames(): Stream<CameraFrame>;
}
```

Map to idiomatic async streams (Dart Stream, Kotlin Flow, Swift AsyncSequence, .NET IAsyncEnumerable, Python async iterator, JS AsyncIterable, C/C++ subscription). Define subscription ownership, bounded queue, backpressure, drop policy, ordered events, cancellation, terminal event and buffer retention. No unbounded camera frame queue.

### 14.4 Operation state and threading

Each operation has one terminal transition: success, failure or cancellation. Handle inline completion before the initiating call returns, completion races, cancellation after completion, late/duplicate responses, errors and teardown. Retain arguments and provider until no execution can use them; cancellation is cooperative and does not imply a running foreign operation has stopped.

Use existing target executors/event loops; no per-call thread. JNI attaches correctly, Swift respects actors, Python respects interpreter/GIL and event loop, .NET roots delegates, Dart dispatches to the correct isolate, JS/WASM respects event-loop and memory constraints. Reject unsafe synchronous crossings. Verify callbacks after detach, reentrant calls, no deadlocks, no stranded futures, no leaked references and stable stream termination.

## 15. Interfaces and service discovery

### 15.1 Ordinary object references come first

Any interface may be created, passed as an argument, returned or injected independently of service registration.

```text
interface HttpClient {
    async request(input: HttpRequest): HttpResponse;
}

interface Application {
    async configure(client: HttpClient): void;
}

callback HttpClientFactory(): HttpClient;
```

No special Provider type is needed. A factory can also be declared as an interface or async callback when appropriate. Generated references preserve the implementation's identity and lifetime according to the ABI.

### 15.2 Optional registry API

Proposed Kotlin registration:

```kotlin
val registry = ServiceRegistry.global
val registration = registry.register(
    HttpClient.TYPE,
    AndroidHttpClient()
)
```

Dart resolution:

```dart
final registry = ServiceRegistry.global;
final client = registry.get(HttpClient.type);
final response = await client.request(request);
```

Swift:

```swift
let client = try ServiceRegistry.global.get(HttpClient.self)
let response = try await client.request(request)
```

C++:

```cpp
auto client = ServiceRegistry::global().get<HttpClient>();
auto response = co_await client->request(request);
```

C#:

```csharp
var client = ServiceRegistry.Global.Get<IHttpClient>();
var response = await client.RequestAsync(request);
```

Python:

```python
client = ServiceRegistry.global_instance().get(HttpClient)
response = await client.request(request)
```

C, Java, Objective-C and JS/TS expose equivalent typed descriptors or generated typed accessors. The API is illustrative and must be proven with C/C++ and managed runtimes before freezing.

### 15.3 How lookup actually works

1. The generator assigns a deterministic logical type identifier to network.HttpClient and emits the same descriptor in every selected target.
2. The registering language creates a generated adapter containing its object reference and typed function table.
3. The shared runtime validates interface identity, ABI fingerprint and runtime context, retains the adapter, and stores a registration token.
4. A consumer calls get using its generated descriptor. The shared runtime finds the compatible registration and takes a strong snapshot.
5. The consumer's generated adapter constructs a typed proxy around the snapshot. Invocations use its function table rather than method-name strings.
6. The provider's adapter schedules or executes the actual method on its runtime. Completion returns through the consumer's generated adapter.

No reflection or network is required. Multiple registrations can coexist. Use explicit scoped registries, optional global convenience and optional parent fallback. A context must be shared intentionally; an unrelated runtime cannot see its providers.

### 15.4 Replacement semantics

| Operation | Behavior |
| --- | --- |
| get(type) | Fixed snapshot, holds current provider |
| proxy(type) | Dynamic proxy, resolves provider for each new invocation |
| register(type, implementation) | Explicit duplicate/replacement policy |
| scoped override | Optional stack; removing override restores previous provider |
| unregister(token) | Removes only that registration |
| missing provider | Typed runtime failure |

Default duplicate registration is an error unless explicit replace/override policy is specified. Do not silently retry a failed call against another provider. Existing operations and stream subscriptions retain their selected provider; new dynamic calls use the current provider. Removing a registration does not invalidate an otherwise valid fixed reference. Runtime shutdown cancels/drains operations before releasing adapters.

Tests: both get/proxy modes; replacement and fallback; multiple instances; nested contexts; ABI mismatch; concurrent registration, lookup, removal and invocation; stale registration tokens; runtime reload; callback reentrancy; final release outside locks.

## 16. Language-specific integration

### 16.1 Flutter calling Kotlin or Swift

The Dart application imports generated typed bindings. A Flutter plugin initializes the shared native runtime and platform adapters. Kotlin or Swift registers an implementation or passes an interface reference to Dart. The C/C++ support runtime routes the typed function table; it does not implement the business logic.

```text
Flutter/Dart -> FFI -> C ABI -> JNI -> Kotlin provider
Flutter/Dart -> FFI -> C ABI -> Apple adapter -> Swift provider
Kotlin/Swift/C++ -> native adapter -> Dart isolate -> Dart provider
Flutter Web -> JS interop -> WASM/JS provider
```

No MethodChannel dependency for the primary native ABI calls. Flutter platform/plugin lifecycle mechanisms may still be used for loading, registration or platform-specific facilities where justified. A Dart implementation is a real provider, not just a client. Async return paths must respect isolate affinity.

Example Dart registration:

```dart
class DartHttpClient implements HttpClient {
  @override
  Future<HttpResponse> request(HttpRequest input) async {
    return executeDartRequest(input);
  }
}

final registration = ServiceRegistry.global.register(
  HttpClient.type,
  DartHttpClient(),
);
```

The implementation function above is illustrative; examples must supply a real implementation.

### 16.2 Concrete provider-to-consumer example

A handwritten Kotlin repository implements the generated interface. It may use a database or the deterministic sample fixture:

```kotlin
class AndroidUserRepository(
    private val database: UserDatabase
) : UserRepository {
    override suspend fun findById(id: Long): User? =
        database.findById(id)

    override suspend fun findAll(): List<User> =
        database.findAll()

    override suspend fun count(): Long =
        database.count()

    override suspend fun exists(id: Long): Boolean =
        database.exists(id)

    // Implement all remaining generated methods in the runnable sample.
}
```

Register the implementation in the shared Android runtime during plugin initialization:

```kotlin
val registration = ServiceRegistry.global.register(
    UserRepository.TYPE,
    AndroidUserRepository(database)
)
```

Dart consumes the same contract and the imported domain model:

```dart
final repository = ServiceRegistry.global.get(UserRepository.type);
final users = await repository.findAll();
final user = await repository.findById(10);
final count = await repository.count();
final exists = await repository.exists(10);

for (final user in users) {
  print(user.name);
}
```

The same Dart code can consume a Swift provider on Apple platforms. Alternatively, inject the repository reference directly instead of registering it. In reverse, Kotlin or Swift may consume a Dart provider, using an asynchronous invocation when crossing isolate/thread boundaries. All examples must run with generated adapters; snippets alone do not satisfy acceptance.

### 16.3 Per-target integration review

| Target | Mandatory concerns |
| --- | --- |
| C/C++ | C ABI visibility, fixed layout, RAII, compiler portability |
| Java/Kotlin | JNI reference lifetime, exceptions, attach/detach, coroutine/Future bridge |
| Objective-C/Swift | ARC, selectors, module maps, nullability, actors, async import |
| Python | CPython references, buffer protocol, interpreter and event loop |
| Dart/Flutter | FFI, callback lifetime, isolates, restart, plugin registration, web separation |
| C# | P/Invoke or LibraryImport, safe handles, GC/delegate lifetime, Task cancellation |
| JS/TS/WASM | BigInt, typed arrays, memory growth, JS roots, ESM exports, Promise |
| Apple platforms | SDK availability, build and simulator/device execution including visionOS |
| Android / XR | NDK/JNI packaging, ABI variants, emulator and lifecycle |

Compile and execute actual generated APIs in each claimed target. Platform-dependent limitations must be documented and enforced by the generator.

### 16.4 Common backend acceptance contract

Every backend below must deliver the following together, not as disconnected generators:

- Public idiomatic model, enum, flags, variant, interface, callback, result and async APIs; generated consumer proxy and provider adapter; exact type mappings from sections 5 and 13.
- Module-specific output configuration, public import path, package/module/namespace, filenames, prefixes, naming categories, annotations, sources mode and package mode. Resolve dependency artifacts from the defining module.
- Versioned ABI integration, initialization and shutdown, strong/weak handles, explicit cleanup, error translation, async completion, cancellation, callbacks, streams and optional service registry. No generated API may bypass its documented ownership/thread contract.
- Golden source tests, native compiler/type-checker tests, real provider and consumer execution, separate module/prebuilt dependency tests, both-direction type conformance, lifetime/copy tests and actual sample application tests.
- The corresponding CI job and language guide must show commands that work from a clean checkout. The toolchain invocations below are implementation requirements, not commands already available in the repository.

For each target, generate a capability manifest listing types, sync/async directions, platform, runtime, scheduler restrictions, zero-copy eligibility, build mode and verified test IDs. Reject unsupported combinations rather than silently emitting broken code.

### 16.5 C backend

**Artifacts and configuration:** public .h files, generated C or C-compatible bridge source, separate private headers, typed handles and vtables, include guards, export/calling convention macros, optional CMake target. Module-specific prefix (app_domain_, app_repo_, etc.), include prefix, header/source paths, extensions and snake_case naming. Public headers compile as C11 and when included from C++; no C++ types leak through.

**Types and memory:** fixed-width integers and explicit UTF-8 pointer/length descriptors. Generated tagged optionals, results and variants; typed collection descriptors; opaque interface/weak/operation/subscription handles. Explicit init/destroy for owning values and recursive cleanup on partial conversion failure. Borrowed buffers are scoped; DataRef is retained/released through the ABI. Caller never frees memory allocated by another allocator.

**Provider and consumer:** generated typed function table and context, functions to create/retain/release interface handles, invoke methods and register/resolve services. Async methods return a status/operation handle and accept typed completion callbacks with user context. Define callback argument ownership and completion exactly once; expose cancellation and subscription disposal. No exceptions cross C entry points.

```c
/* Illustrative generated API shape. */
pg_status app_repo_user_repository_count_async(
    app_repo_user_repository *repository,
    pg_int64_completion completion,
    void *context,
    pg_operation **operation);
```

**CI:** c.yml runs C11 compilation with GCC/Clang and supported MSVC C mode on Linux/Windows/macOS. Build C and C++ header consumers; run C-to-C++ and reverse, C provider called by managed targets, all type fixtures, allocator-failure injection, invalid handles, ABI layout tests, ASan/UBSan/LSan where available, separate TSan stress. Test Windows DLL export/import and calling conventions. Example CLI executes HTTP through a foreign provider, grayscale fixture and fake login.

### 16.6 C++ backend

**Artifacts and configuration:** .hpp/.cpp files, namespace, header/include prefix, public/private layout, configurable case and suffixes, forward declarations, CMake targets and optional installed package config. Use C++20 baseline; do not require std::expected or C++23 for public headers. Support nodiscard/deprecated and safe noexcept annotations.

**Types and memory:** records with value semantics, enums/flags, optional, variant, vector/collections, generated Result, typed references and RAII wrappers. Move ownership when contract permits; reference counting must not copy buffers. DataView span-like scoped access; MutableDataView exclusive borrow; DataRef retainable owner. Weak references must not resurrect disposed objects.

**Provider and consumer:** generated abstract interface, proxy and native provider adapter; C++ implementations use ordinary virtual methods and can be passed directly without registry. Async return uses a PolyGlue awaitable/future with co_await, callback completion and cancellation, without imposing a thread per call. Document executor behavior and destructor safety. Registry get<T> snapshots a provider; dynamic proxy resolves on invocation.

```cpp
auto repo = registry.get<UserRepository>();
auto users = co_await repo->findAll();
```

**CI:** cpp.yml builds CMake/CTest on GCC, Clang and MSVC; shared/static consumer builds, installed headers, multiple translation units, visibility and ABI checks, debug/release, RAII, exception translation, coroutine completion/cancel races, weak reference and destruction tests. Run native sanitizers independently and verify reentrant calls. Example CLI with actual foreign provider and native image processor.

### 16.7 Java backend

**Artifacts and configuration:** public classes/interfaces, proxy and provider adapter classes, JNI bridge source/header, package and Java file naming, optional Gradle Java library. Every public top-level class uses its required filename. Support nullability/deprecation attributes with explicit dependency policy; never add an annotation library implicitly. Share JVM models with Kotlin only through an explicit artifact-ownership strategy.

**Types and memory:** primitive and boxed representations follow section 5; unsigned values widen or use checked BigInteger. JNI strings convert UTF-16 to canonical UTF-8 and back, not modified UTF-8 shortcuts that lose NUL/supplementary characters. JNI global references retain providers, local frames bound references, weak globals only for explicit weak semantics. Use direct buffers only when valid native memory and owner lifetime are established; do not expose an unrestricted direct ByteBuffer as a safe borrowed view.

**Provider and consumer:** generated Java interface uses CompletableFuture for async, functional interfaces for callbacks, typed stream subscription and a publisher adapter where useful. JNI retains callbacks/provider objects, attaches foreign threads, checks and clears/translates Java exceptions, and releases references on a valid JVM thread. Never cache JNIEnv across threads. No JVM initialization or destruction while active adapters remain. Cancellation of CompletableFuture must propagate to the native operation when configured; provider completion still controls resource lifetime.

```java
UserRepository repo = registry.get(UserRepository.TYPE);
CompletableFuture<List<User>> users = repo.findAll();
```

**CI:** java.yml builds Java/JNI on Linux, macOS and Windows with pinned JDK/Gradle, runs -Xcheck:jni, Java↔C++, Java↔Kotlin shared artifact cases, forced GC, exception conversion, global/local reference balance, direct buffer lifetime, callback from native thread, duplicate completion, JVM teardown and exact unsigned/Unicode round trips. Sample desktop CLI or simple UI.

### 16.8 Kotlin backend

**Artifacts and configuration:** Kotlin classes/interfaces and adapters, .kt files, package, JVM module and optional Gradle/Kotlin library. For Android emit appropriate Android library/JNI packaging integration, not a mandatory application rewrite. When Java is also selected, either generate one shared model set with distinct API wrapper names or use separate packages; validate JNI signatures after Kotlin name mangling. Support JvmName/JvmStatic/JvmOverloads only where legal and needed.

**Types and memory:** Kotlin signed and unsigned types, nullable types and explicit tagged nesting, immutable data models, Kotlin collections, sealed Result/variant. Primitive arrays with exact conversion. Shared Java models may require safe value conversions; do not duplicate class identities. Use JNI lifetime rules from Java; DataRef keeps the owner and any direct memory valid across suspension.

**Provider and consumer:** suspend methods, cancellation-aware continuations and Flow for streams. Bridge Java CompletableFuture when sharing API artifacts; cancellation and exceptions map to native terminal states without resuming a continuation twice. Use structured concurrency or supplied CoroutineScope/dispatcher; no GlobalScope or blocking event loops. Android UI/system APIs dispatch to the main looper only when required. Kotlin providers can be registered or injected and invoked by Dart or C++.

```kotlin
val registration = registry.register(UserRepository.TYPE, repositoryImpl)
val users = registry.get(UserRepository.TYPE).findAll()
```

**CI:** kotlin-desktop.yml exercises JVM on desktop and Kotlin↔Java/C++; kotlin-android.yml builds Android Gradle project, packages ABI-specific .so, runs instrumented tests/emulator and Flutter↔Kotlin integration in both directions. Test coroutine cancellation, thread dispatch, activity recreation, provider detach, JNI references, camera buffer release and exact unsigned mapping. Test Android XR separately when device/emulator is available.

### 16.9 Objective-C backend

**Artifacts and configuration:** prefixed public headers, Objective-C++ .mm implementation, umbrella header/module.modulemap and optional framework/SwiftPM-compatible Clang target. Use module-specific DOM/REP prefixes, selectors, naming and NS_SWIFT_NAME metadata; resolve dependency module imports or header imports. No duplicate type names when Swift wrappers coexist.

**Types and memory:** NSObject model objects, protocols for interfaces, NS_ENUM/NS_OPTIONS, Foundation collections/strings and explicit boxing for scalar optional/nested variants. Nullability distinguishes absent value from runtime error. ARC retains object providers and blocks; use explicit bridge ownership operations for opaque contexts, avoid retain cycles and balance autorelease pools on foreign threads. DataRef is a retained owner wrapper; NSData use alone does not prove zero-copy. Borrowed view wrappers must enforce scope.

**Provider and consumer:** typed generated protocols and proxy classes, copied completion blocks, typed callbacks and subscription cancellation. Use NSError or explicit status for runtime failures, Result for business failures; no NSException crosses the ABI. Annotate importable completion APIs for Swift where valid; generate explicit Swift wrappers for ambiguous optional/error cases. Test callback block lifetime, reentrancy and dispatch queues.

```objc
@import AppDomainObjC;

id<REPUserRepository> repo = [registry userRepository];
[repo findAllWithCompletion:^(NSArray<DOMUser *> *users, NSError *error) {
    /* Handle completion. */
}];
```

**CI:** objc.yml compiles Objective-C and Objective-C++ on macOS with ARC, tests Obj-C↔C++, Obj-C↔Swift, import macros, nullability, enum/flags, selector conflicts, autorelease/weak lifetime, callback block disposal, actual Swift compiler import. Platform SDK builds and execution covered by apple-platforms.yml. Sample native app or CLI; verify foreign HTTP, login and media processor.

### 16.10 Swift backend

**Artifacts and configuration:** .swift contracts, models or re-exports, proxies and adapters, Package.swift or source integration, module/target, visibility, prefix/case, imports and availability. Swift module names are not directory names. When using imported Objective-C models, provide one canonical model type; when generating native Swift models, use explicit conversion or separate modules and avoid ambiguous unqualified imports.

**Types and memory:** Swift value types where appropriate, protocols and generated proxies, optional, enum/OptionSet, tagged variants and Result when Error constraints are satisfied. Exact numeric/time mappings; controlled UnsafeRawBufferPointer access for DataView, owned DataRef reference and explicit Data copying. ARC and Unmanaged bridge ownership must be balanced. Never label arbitrary object types Sendable or use unchecked Sendable without a documented proof and tests.

**Provider and consumer:** async throws, checked continuation adapter with exactly-once resume and cancellation propagation, typed closures, AsyncSequence stream, explicit executor/actor policy. MainActor is enforced for UI APIs. Swift implementations register or pass protocol references and may be called from Kotlin/C++/Dart where valid. Do not block an actor waiting for a callback scheduled on that actor.

```swift
let repo = try registry.get(UserRepository.self)
let users = try await repo.findAll()
```

**CI:** swift.yml runs SwiftPM or Xcode tests on macOS with strict concurrency diagnostics, Swift↔C++, Swift↔Objective-C and Swift↔Dart integration on applicable platforms. Test ARC/weak refs, continuations, cancellation/actor dispatch, selector/import name consistency, module dependencies and availability annotations. apple-platforms.yml builds each Apple SDK and runs platform-appropriate tests; record visionOS/tvOS/watchOS/Catalyst evidence individually. Sample native UI where applicable.

### 16.11 Python backend

**Artifacts and configuration:** Python package with public exports, .py/.pyi as appropriate, generated proxy/provider wrapper and CPython bridge or stable supported adapter, optional pyproject.toml/build integration. Package name, output tree, source vs wheel package mode, snake_case, annotations and imports. Python generator dependencies are not automatically runtime dependencies of generated Python bindings.

**Types and memory:** frozen dataclasses by default, Enum/IntFlag, typed collections and Result/variant, strict numeric range checks, Unicode and bytes. Handle cycles and interpreter shutdown; own every new/borrowed PyObject reference correctly. For DataRef, keep Py_buffer/exporter alive until final release, release on correct interpreter/thread. A Python memoryview that escapes a borrowed scope cannot be treated as safely invalidated; use a checked scoped wrapper or explicit owned conversion.

**Provider and consumer:** async def/awaitable, asyncio event loop capture, thread-safe scheduling from native threads, callback roots, async iterator and cancellation. Acquire correct interpreter thread state before invoking Python; respect GIL or supported free-threaded build policy. Never call Python after finalization. Record supported CPython versions and whether subinterpreters/free-threaded builds are supported; reject unsupported modes.

```python
repo = registry.get(UserRepository)
users = await repo.find_all()
```

**CI:** python.yml tests installed generated bindings on Linux/macOS/Windows, native↔Python and Python↔other coexisting runtimes, CPython debug/refcount checks, forced GC, buffer export lifetime, async cancellation, native worker callback scheduling and interpreter shutdown in subprocesses. Wheel/sdist package tests verify import from outside source tree. Example CLI or simple app with real cross-language HTTP/login/grayscale.

### 16.12 Dart backend

**Artifacts and configuration:** Dart package, public barrel export, lib/src models/interfaces/proxies, FFI binding declarations and native assets loading configuration; separate web implementation and conditional imports. Package/output, naming, annotations and optional pubspec. A pure Dart target must not require Flutter SDK. No dart:ffi imports in web build.

**Types and memory:** native int for signed 64-bit, BigInt for uint64 and exact Web 64-bit; typed data arrays when exact; immutable models, sealed variants and Result. Native memory uses checked handles and explicit dispose plus NativeFinalizer where safe. Never keep raw borrowed TypedData views beyond synchronous lifetime; DataRef retains native storage through async. NativeFinalizer cannot serve as the only deterministic lifecycle mechanism.

**Provider and consumer:** Future/Completer, typed functions, Stream and cancellation. NativeCallable.listener or supported message dispatch handles callbacks from arbitrary threads asynchronously; isolate-local calls require the correct thread/isolate. No synchronous foreign-thread Dart return. Root registered providers in their owning isolate; on detach/hot restart invalidate registrations, drain/cancel operations and ensure no callback into a closed NativeCallable. Completion arguments remain valid until isolate consumes them.

```dart
final repo = registry.get(UserRepository.type);
final users = await repo.findAll();
```

**CI:** dart.yml runs dart analyze, format checks where configured, dart test on Linux/macOS/Windows, native library load/architecture tests, Dart↔C++, callback from worker thread, multiple isolates, isolate shutdown and forced restart, DataRef finalizer/explicit disposal and copy tracking. Dart Web runs actual JS/WASM integration in browser. Sample CLI, not a Flutter-only demo.

### 16.13 Flutter integration target

**Artifacts and configuration:** reuse generated Dart contracts, emit plugin with pubspec, lib, Android Gradle/JNI, iOS/macOS Apple integration, Windows/Linux CMake and web adapter as appropriate. Support existing native projects in sources mode and buildable plugin in package mode. Plugin owns runtime initialization/attachment tokens, not all application service instances. Expose a single public Dart API with target-appropriate adapters.

```text
app_repository_plugin/
├── pubspec.yaml
├── lib/
│   └── app_repository_plugin.dart
├── android/
├── ios/
├── macos/
├── windows/
├── linux/
├── web/
├── test/
└── integration_test/
```

**Providers and lifecycle:** Kotlin/Java and Swift/Obj-C implementations are real providers, not MethodChannel stubs. Calls go through generated FFI/native adapters and shared service context. Native implementations can call Dart providers asynchronously. Handle plugin detach, multiple Flutter engines, isolates, activity recreation, background/foreground, hot restart and disposal independently. Web uses the JS/WASM implementation. Reuse DataRef for camera frames, with explicit mapping/copy for non-shareable memory.

**CI:** flutter.yml has distinct jobs for Android emulator, iOS simulator, macOS, Windows, Linux and Web. Run flutter analyze/test plus integration_test and actual native plugin build/run. Verify Android Kotlin provider and Apple Swift provider using the same Dart consumer, reverse native→Dart callback/provider, module import/layout, lifecycle and restart. Desktop runners test C++ provider; web tests JS/WASM provider. Required UI contains HTTPBin, login form and camera/grayscale preview. Deterministic fixtures do not replace actual device camera validation. Native visionOS Flutter is not claimed without upstream support and evidence.

### 16.14 C# backend

**Artifacts and configuration:** .cs models, interfaces, proxies, native adapter declarations, namespace and assembly, project references, optional .csproj. PascalCase types/methods, I interface prefix and Async suffix configurable. Use generated P/Invoke/LibraryImport declarations appropriate to supported .NET version and platform; validate calling convention, StructLayout and field sizes. Do not assume C# bool/string layout is the C ABI layout.

**Types and memory:** exact signed/unsigned primitives, immutable record models, nullable or tagged optionals, generated Result/variant and read-only collections. Use SafeHandle or equivalent for owning references and explicit IDisposable; retain delegates/GCHandle for provider callbacks and release only after native operations drain. Span/ReadOnlySpan scoped borrowed access; DataRef owner enables async use. GC pinning or copies are explicit; no pointer to movable managed memory after pin scope.

**Provider and consumer:** Task<T>/Task for async, typed delegates, IAsyncEnumerable and CancellationToken adapter. Use completion sources with asynchronous continuation scheduling where needed; exactly-once completion; map cancellation without prematurely releasing active native resources. Use stable unmanaged entrypoints or rooted delegates; exceptions never cross native ABI. Managed provider registration works from C++/Dart where the .NET host is available; do not assume arbitrary embedding. Specify supported .NET hosting and NativeAOT modes separately.

```csharp
using var registration = registry.Register<IUserRepository>(implementation);
var repo = registry.Get<IUserRepository>();
var users = await repo.FindAllAsync();
```

**CI:** csharp.yml runs dotnet build/test on Windows/Linux/macOS with pinned SDK, C#↔C/C++, GC stress and forced collection, delegate lifetime, SafeHandle explicit/finalizer cleanup, struct size/offset assertions, cancellation and native thread callbacks. Test package/project reference and platform native-library resolution. Sample console or simple UI with all three scenarios.

### 16.15 JavaScript backend

**Artifacts and configuration:** ESM runtime .js modules, loader, package.json exports, public entry point and generated proxies/providers; configurable module/package, relative/public import policy, names, layout and file extension. Browser and Node runtime integration are separate capabilities. No reliance on TypeScript compiler at application runtime when JS is selected.

**Types and memory:** checked Number for small integers, BigInt for exact 64-bit, string UTF-16 validation, Uint8Array for copied bytes, Map/Set, tagged result and variants, runtime value validation because JS is dynamic. WeakRef/FinalizationRegistry cannot guarantee timely cleanup; use explicit dispose. DataRef and views refer to compatible native/WASM memory only; arbitrary JS heap cannot be assumed shareable.

**Provider and consumer:** Promise, typed callable shape at runtime, AsyncIterable, AbortSignal adapter and generated provider registration. Maintain rooted JS references while native handles are alive; prevent calls after module teardown. Handle synchronous reentrancy and asynchronous microtask completion. Use worker/message dispatch only with explicit transfer/sharing contract; no cross-worker raw pointers.

```javascript
const repo = registry.get(UserRepository.type);
const users = await repo.findAll();
```

**CI:** javascript.yml runs Node tests and browser integration, generated ESM import/exports, JS↔WASM and reverse provider, Promise resolution/rejection, BigInt boundary, Unicode, callback roots, GC/explicit disposal, memory growth, worker constraints and package installation. Browser example includes HTTP, login form and camera via getUserMedia where permission exists; Node CLI uses deterministic image fixture.

### 16.16 TypeScript backend

**Artifacts and configuration:** generated .ts or .d.ts declarations plus matching JS runtime, package.json exports/types, tsconfig, per-module public type imports and type-only imports. When sharing JavaScript output, generate declaration artifacts once and verify no duplicate runtime classes or export collisions. Strict mode, no implicit any in public contracts, target/module resolution explicit.

**Types and memory:** exact mappings match JavaScript runtime; interfaces/read-only models, tagged unions, bigint, typed arrays and explicit nullable/optional states. TypeScript declarations do not substitute runtime validation. Model the owner/borrow API without claiming the TS type checker can enforce lifetime of escaped views.

**Provider and consumer:** strongly typed interfaces, Promise<T>, AsyncIterable<T>, callback signatures, AbortSignal and typed registry descriptors. Generated declarations match actual runtime exports and implementation signatures; verify both valid and invalid type-check fixtures.

```typescript
const repo: UserRepository = registry.get(UserRepository.type);
const users: User[] = await repo.findAll();
```

**CI:** typescript.yml runs strict tsc type-check, negative compile fixtures, package consumer tests and actual emitted/runtime JS tests in Node/browser. Run all common types and provider directions, not just compilation. Verify JS and TS shared artifact mode, separate module import resolution, bigint and Result/variant discriminants. Provide typed browser sample and Node harness.

### 16.17 WebAssembly backend

WebAssembly is a transport/execution target, not another IDL language.

**Artifacts and configuration:** generated C/C++ WASM adapter, exported functions, Emscripten build integration, JS module loader and TypeScript declarations. Configure output, include prefix, module/package name, environment (browser/Node), memory growth/thread mode and public exports. Avoid unnecessary Embind or other dependencies when typed C ABI plus generated JS suffices.

**Types and memory:** fixed WASM ABI, validate pointer/length and linear memory bounds. Use exact i64/BigInt conversion. Views of WebAssembly.Memory may become detached/stale after growth; pin or prohibit growth while a borrow is active, or reacquire using checked owner/offset. Never expose stale cached views as valid. Shared DataRef may keep a linear-memory allocation alive; it cannot prevent arbitrary JS buffer detach unless policy enforces it. Separate shared memory/threads support and cross-origin isolation requirements from baseline single-thread mode.

**Provider and consumer:** JS/TS can implement interfaces consumed from WASM and vice versa, with Promise-based async bridge and rooted JS callbacks. No blocking browser main thread to emulate synchronous async completion. Threaded mode only when browser/runtime configuration allows it; cancellation and teardown release both native and JS references.

**CI:** wasm.yml builds with pinned Emscripten, runs Node and headless browser tests, memory growth, out-of-bounds checks, JS/WASM bidirectional types, BigInt, DataView/DataRef/copy counts, Promise completion/cancel, module destruction/reinitialization, workers when supported. Verify no native ABI pointer is reused as a cross-instance handle. Flutter Web tests run against actual WASM/JS adapter.

### 16.18 Platform integration specifics

| Platform | Build / execution requirement | Lifecycle and sample-specific requirement |
| --- | --- | --- |
| Linux | GCC/Clang, shared libraries, native runtimes | Loader path, headless fixture, optional camera device |
| Windows | MSVC and supported Clang, DLL imports/exports | CRT allocator pairing, architecture, native library discovery |
| macOS | Clang, Xcode, SwiftPM, supported desktop runtimes | ARC, signing where required, camera permission, native UI |
| Android | NDK/Gradle, ARM64 and emulator ABI, instrumented test | JNI, app lifecycle, permissions, CameraX or compatible capture |
| Android XR | Android XR SDK-compatible build and emulator/device | XR lifecycle, available sensors/camera permission; no false hardware claim |
| iOS/iPadOS | Xcode simulator/device target, framework or library integration | ARC, main actor, app lifecycle, permission and actual camera on device |
| tvOS | SDK build and simulator execution | Remote/input and available media/camera capability; use image fixture when no camera |
| watchOS | SDK build and simulator execution | Watch app lifecycle, constrained resources, no unsupported camera claim |
| visionOS | visionOS SDK build and simulator execution; device where hardware required | Native Swift/Obj-C/C++ bridge, actor/lifecycle, camera entitlement/access constraints; use fixtures where access unavailable |
| Mac Catalyst | Catalyst SDK build and native execution | Distinguish from macOS target; availability and lifecycle |
| Web | Browser and Node where supported | Browser permissions, CORS, event loop, WASM memory constraints; Node fixture |

Physical device tests are not replaceable by a simulator for device-only features. Record hardware access as blocked when unavailable. Do not require a physical camera for platforms without appropriate APIs; the grayscale computation and buffer transfer remain mandatory with fixtures. All supported platform targets must build and execute at least their applicable conformance cases.

## 17. Example applications

### 17.1 Shared modules

```text
examples/
├── polyglue.yaml
├── modules/
│   ├── domain/
│   ├── repository/
│   ├── auth/
│   ├── network/
│   └── media/
├── c/
├── cpp/
├── java/
├── kotlin/
├── objc/
├── swift/
├── python/
├── dart/
├── flutter/
├── csharp/
├── javascript/
└── typescript/
```

Every target must have runnable provider and consumer examples. Use simple UI on relevant platforms and CLI equivalents on headless targets. All bridges must come from the generator; handwritten business logic is expected.

### 17.2 HTTPBin

```text
record HttpRequest {
    url: string;
    method: string;
    headers: map<string, string>;
    body: optional<DataRef>;
}

record HttpResponse {
    status: int32;
    headers: map<string, string>;
    body: DataRef;
}

interface HttpClient {
    async request(input: HttpRequest): HttpResponse;
}
```

Send a real HTTPS request to https://httpbin.org/get or /post using a provider in a different runtime. Display status, headers and body; test error, timeout, cancellation and async completion. Deterministic CI uses a local HTTP fixture with the same contract; a separate live smoke checks the actual public service. Do not make deterministic tests rely on public network availability.

### 17.3 Camera and grayscale

```text
enum PixelFormat {
    RGBA8 = 1,
    BGRA8 = 2,
    RGB8 = 3
}

record CameraFrame {
    width: int32;
    height: int32;
    stride: int32;
    timestamp: int64;
    format: PixelFormat;
    data: DataRef;
}

interface Camera {
    async start(): void;
    async stop(): void;
    frames(): Stream<CameraFrame>;
}

interface ImageProcessor {
    process(data: DataView): DataRef;
    processInPlace(data: MutableDataView): void;
    async grayscale(frame: CameraFrame): CameraFrame;
}
```

Capture a real camera image on supported devices, pass a retained CPU-accessible frame to a provider implemented in another language, convert to grayscale and display the result. Define pixel layout, stride, orientation, alpha preservation, format conversion and buffer lifetime. Reject unsupported pixel formats or explicitly convert.

CI uses deterministic known-pixel fixtures, padded strides, odd sizes and invalid inputs, and verifies exact grayscale output plus copy instrumentation. Hardware camera tests and fixture tests are separate evidence. Do not claim real camera coverage solely from a fixture.

### 17.4 Fake login and repository

A minimal login form or CLI submits fictional username/password values, calls an Auth implementation in another runtime, and receives a populated User with id, name, email and loggedIn. Invalid credentials return a typed LoginError. Never log passwords. Include the domain/repository async list, optional, integer, bool and void methods from section 4.

### 17.5 Cross-language application acceptance

Every language has a documented cross-language caller and implementation case, with repeatable commands. Include Flutter Android to Kotlin, Apple to Swift, native to Dart callback/provider, JVM to C++, Python to C++, C# to C++, JS to WASM and their supported reverse directions. Test switching providers without modifying the consumer. Exercise callbacks, cancellation, shared memory and shutdown. The conformance suite, not just UI demos, covers the full type and pair matrix.

## 18. Test specification

### 18.1 Shared conformance suite

All backends consume the same IDL fixtures and named test cases. Generate fresh bindings, compile them, execute real implementations and compare actual results. Maintain a machine-readable matrix indexed by type, direction, platform, runtime, operation and case ID; every claimed combination has evidence or an explicit unsupported reason.

| Category | Required cases |
| --- | --- |
| Scalars | All widths, signed/unsigned limits, bool, float edge cases |
| Strings | Empty, Unicode, embedded null, invalid encoding |
| Collections | Empty/large/nested, duplicates, map keys, arrays |
| Named types | Records, enums, flags, variants, constants, defaults, generic instantiations |
| Optional / Result | Missing, present, success, error, void success, nested values |
| External types | Adapter conversion, invalid input, lifetime |
| Interfaces | Identity, multiple objects, inheritance, factory, both directions |
| Async | Every valid return category, inline and delayed completion, error, cancel |
| Callbacks | Scoped, retained, one-shot, thread affinity, return values where supported |
| Streams | Ordering, backpressure, cancellation, terminal state, slow consumer |
| Modules | Source/prebuilt, import aliases, independent paths, dependency graph |
| Naming / annotations | Golden source plus actual compiler checks |
| Buffers | DataView, MutableDataView, DataRef, bytes, alias/copy/lifetime rules |
| Registry | Lookup, fixed/dynamic references, override, fallback, concurrent teardown |

Exercise legal nested compositions (e.g. optional<list<User>>, list<optional<User>>, Result<Page<User>, Error>) and reject forbidden combinations. Add boundary and randomized tests. Every backend pair that can coexist must run both directions, not just separate language-to-C tests.

### 18.2 Memory safety and concurrency

| Risk | Evidence |
| --- | --- |
| Use-after-free/return/scope, double-free, overflow | ASan and negative lifecycle tests |
| Leaks | LSan or platform equivalent, allocation balance, GC/ARC tests |
| Undefined behavior | UBSan |
| Uninitialized memory | MSan where toolchain is instrumented |
| Race conditions | TSan in separate compatible builds; deterministic race tests |
| Deadlocks | Lock-order tests, reentrant callbacks, barriers, watchdog timeouts |
| JNI misuse | CheckJNI, reference tracking, attach/detach tests |
| Managed lifetimes | Python debug build, Swift strict concurrency/ARC, .NET GC stress, Dart isolate tests |
| ABI | Layout, calling convention, version mismatch, stale/foreign handles |
| Copies | Pointer identity where valid, copy counters, explicit copy conversions |
| Async teardown | Completion/cancel/shutdown races, duplicate completion, late callbacks |
| Robustness | Fuzz parser, semantic resolver and ABI/converters; bounded malicious inputs |
| Performance | Latency, throughput, allocation and copy baselines |

Use instrumented builds, repeated initialization, concurrent retains/releases, forced collections, randomized seeds, explicit failure injection and subprocess isolation for deliberate faults. Confirm sanitizer harnesses detect faults. Tests must not depend on sleeps to orchestrate races; use barriers and bounded timeouts. Instrumented counters must return to expected baselines after teardown.

### 18.3 Compiler and generation tests

Unit parser/AST/IR/config tests, semantic errors and source spans, snapshots/golden files, annotation validation, custom templates, import/path/naming collisions, deterministic output, no-op regeneration, safe cleanup, module dependency tests, source/package compilation and wheel/sdist installation. Test invalid YAML and IDL, escaping, path traversal, unsupported targets and partial write failures.

### 18.4 Completion evidence

No finite test suite proves that all possible defects are absent. The acceptance standard is complete explicit conformance coverage, reproducible test evidence and zero known blocking defects. Never hide a failing or skipped required test. Every defect receives a regression test before it is closed.

## 19. GitHub Actions

### 19.1 Workflows and independent checks

| Workflow / job | Required execution |
| --- | --- |
| generator | Ruff, Python unit/property tests, grammar, config, generation |
| c | Generated C consumer/provider; GCC/Clang/MSVC where applicable |
| cpp | Generated C++ consumer/provider; CMake/CTest and compiler matrix |
| java | JVM/JNI bidirectional conformance, CheckJNI |
| kotlin-desktop | JVM desktop and coroutine interop |
| kotlin-android | Android emulator, JNI integration, sample app |
| objc | Objective-C++ and Swift import tests |
| swift | Native macOS Swift tests, actors, ARC |
| apple-platforms | iOS, iPadOS, tvOS, watchOS, visionOS, Catalyst SDK builds and available execution |
| python | Generated CPython bindings, async, refcount/buffer tests |
| dart | Native FFI and isolate tests |
| flutter | Android, iOS, macOS, Windows, Linux, Web integration matrix |
| csharp | .NET native interop and GC stress |
| javascript | Node/browser and JS provider tests |
| typescript | Type checking plus actual generated runtime execution |
| wasm | Emscripten compilation, browser and Node conformance |
| android-xr | SDK and compatible emulator/device evidence |
| interop | Supported language-pair matrix, both directions |
| sanitizers | ASan/LSan/UBSan, TSan separately, MSan where valid |
| fuzz-stress | Fuzz, stress, lifetime and concurrency regression |
| docs | Links, snippets and example validation |
| packaging | Wheel/sdist install, resource availability, CLI from clean environment; independent native and ecosystem package consumer matrix |
| httpbin-live | External HTTP smoke with separate network failure reporting |

Use workflow names/filenames consistently (e.g. .github/workflows/c.yml). Only add README badges for real workflows. Each job regenerates its inputs and fails if required tests did not execute. Do not replace real test jobs with echo commands, empty matrices or allow-failure.

### 19.2 CI rules

PR and main runs execute mandatory checks. Expensive fuzzing and extended platform coverage also run nightly and before release; release gates require all mandatory evidence on the exact candidate SHA. Pin reviewed toolchains and action revisions, use least permissions, safe caches, timeouts and reproducible build environments. No secrets in untrusted PR jobs.

Collect JUnit/CTest reports, sanitizer output, coverage, copy counts, platform/test matrix, build logs and benchmark data as artifacts. Confirm jobs actually ran, inspect failures, fix root causes, rerun and record the SHA. Platform/runner unavailability remains an explicit blocker. Do not claim a passing run from a queued workflow or successful compilation alone.

### 19.3 Target coverage and evidence gates

Each target-specific workflow owns its toolchain setup, generation command, build, actual test execution, and artifact publication. Shared reusable workflows may reduce duplication but must preserve distinct named checks for each language. A test report lists expected case IDs and observed results; fail when an expected case was not executed. A missing SDK, simulator or runtime is blocked, not silently skipped.

| Target | Primary test tools | Required output |
| --- | --- | --- |
| C | CMake/CTest, C11 compiler | C provider/consumer executable and C ABI checks |
| C++ | CMake/CTest, compiler matrix | Native executable, RAII and coroutine results |
| Java | Gradle/JUnit, JNI checker | JVM provider/consumer and reference checks |
| Kotlin desktop | Gradle/JUnit, coroutine tests | JVM bridge and cancellation results |
| Kotlin Android | Gradle connected/instrumented tests | Emulator APK execution and JNI results |
| Objective-C | Xcode/CTest/XCTest as appropriate | ARC/block and Swift import tests |
| Swift | SwiftPM/XCTest | Swift provider/consumer and concurrency results |
| Python | pytest, debug interpreter where available | Native bridge, GC/refcount and event loop results |
| Dart | dart analyze/test | FFI/isolate and buffer lifecycle tests |
| Flutter | flutter analyze/test/integration_test | Separate Android/iOS/desktop/web execution reports |
| C# | dotnet build/test | Managed/native interop and GC/delegate tests |
| JavaScript | Node test runner and browser harness | JS and WASM provider execution |
| TypeScript | tsc and runtime test runner | Type fixtures plus actual runtime tests |
| WASM | Emscripten, Node and browser harness | WASM module execution and memory tests |

Document exact commands and pinned toolchains once implemented; do not claim that illustrative commands already work. CI release evidence must include compiler/SDK versions, target architecture, runner OS, git SHA, generated module manifest fingerprints, case IDs, sanitizer status, sample execution and known unsupported capabilities. Track first-class platform checks independently for visionOS, tvOS, watchOS, Catalyst, Android XR and others. For camera use hardware evidence separately from deterministic fixture tests.

### 19.4 Review checklist per backend

- [ ] Every mapped primitive, composite and special type generates valid idiomatic code and round-trips.
- [ ] Public interface, provider, proxy, factory, callback, async, stream and registry APIs work in both directions.
- [ ] Module dependencies, independent output paths, prefixes, cases, imports and annotations compile.
- [ ] Source and package modes, installed package imports and native loading are proven.
- [ ] Native/managed lifetimes, shutdown, error translation, cancellation and thread affinity are proven.
- [ ] DataView and MutableDataView scope rules, DataRef ownership, zero-copy conditions and explicit copies are proven.
- [ ] Shared conformance, target-specific regressions, sample apps and platform-specific execution are green.
- [ ] Capability matrix and documentation match executed cases; no unsupported feature is advertised.

### 19.5 Package-level CI gates

Every language workflow must call the same Python orchestration commands used locally. Add independent artifact checks for CMake installation, AAR/JAR, XCFramework/SwiftPM, wheel, Dart/Flutter, NuGet and npm/WASM. Build requested release slices, inspect format and architecture, install into a separate consumer with no source-tree fallback and run representative conformance, async, ownership and sample scenarios. Full conformance runs on generated code and again on packaged artifacts wherever required. Test both clean and incremental builds, corrupted/missing artifacts, unavailable SDKs, incorrect architecture, stale manifests, failed commands and sanitizer contamination. Verify debug-symbol matching and release optimization/stripping where applicable. Upload actual distributable and reports tied to commit SHA. Do not publish externally from ordinary CI. On main, preserve complete runs; PR cancellation may cancel superseded revisions but never mark them passing.

## 20. Repository documentation and branding

### 20.1 Repository layout

```text
polyglue/
├── PROJECT.md
├── README.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── CMakeLists.txt
├── CMakePresets.json
├── LICENSE
├── src/polyglue/
│   ├── cli/
│   ├── config/
│   ├── parser/
│   ├── semantic/
│   ├── ir/
│   ├── diagnostics/
│   ├── backends/
│   ├── templates/
│   └── build/
├── support/
│   ├── core/
│   ├── c/
│   ├── cpp/
│   ├── jni/
│   ├── java/
│   ├── kotlin/
│   ├── objc/
│   ├── swift/
│   ├── python/
│   ├── dart/
│   ├── flutter/
│   ├── dotnet/
│   └── wasm/
├── tests/
│   ├── compiler/
│   ├── conformance/
│   ├── interoperability/
│   ├── memory/
│   ├── concurrency/
│   └── fuzz/
├── examples/
├── benchmarks/
├── docs/
├── scripts/
├── cmake/
├── extras/images/logo.svg
└── .github/workflows/
```

Keep directories meaningful; do not create empty scaffolding just to match the tree. Choose the license with owner authorization.

### 20.2 README and logo

README in English, following the existing project style: centered original SVG logo and short tagline, actual CI badges, Project, Workflow, How to use, Supported languages and platforms, Documentation, License. Include working IDL and generated-API examples; mark planned features clearly. Logo: clean, modern, recognizable vector mark suggesting multiple languages joining through a bridge/glue; works on light/dark backgrounds and small sizes, no external image dependencies.

### 20.3 AGENTS.md and documentation

AGENTS.md directs contributors to PROJECT.md, requires original source, English code/docs, small dependencies, test-driven development, deep reviews and honest reporting of capability status. No bypassing the generated adapters or disabling tests to pass CI. Provide repeatable development commands and update documentation with behavior changes.

Documentation files cover getting started, IDL grammar and type system, modules/configuration, naming, annotations, layout/imports, external types, runtime/ABI, memory/ownership, async/callbacks/streams, optional registry, all language/platform integrations, application examples, test matrix, contribution, troubleshooting and releases. Validate snippets and links against actual implementation.

### 20.4 Native build system and CMake organization

CMake is the authoritative native build system for C, C++, JNI, Objective-C/Objective-C++, native FFI support, and WASM. SwiftPM, Gradle, Xcode, Flutter, .NET and Python packaging remain the native ecosystem entry points where appropriate; Python orchestrates them and CMake builds their native components. Do not force pure managed-language or frontend sources through CMake.

Use target-based modern CMake with a documented minimum version chosen from the supported SDK/toolchain matrix, initially 3.25 or newer. C++20 and C11 are the language baselines. Use CMakePresets.json for reproducible common development configurations and CMakeUserPresets.json (ignored) for local customizations. Cross-compilers, sysroots, target architecture and SDK selection are explicit and validated at configure time.

Required layout (create files only when their functionality is implemented):

```text
polyglue/
├── CMakeLists.txt
├── CMakePresets.json
├── cmake/
│   ├── Options.cmake
│   ├── Dependencies.cmake
│   ├── CompilerWarnings.cmake
│   ├── Sanitizers.cmake
│   ├── Install.cmake
│   ├── PolyGlueConfig.cmake.in
│   ├── dependencies/
│   │   └── testing.cmake
│   └── toolchains/
│       └── README.md
├── support/
│   ├── core/
│   │   ├── CMakeLists.txt
│   │   ├── include/polyglue/
│   │   └── src/
│   ├── c/
│   │   ├── CMakeLists.txt
│   │   ├── include/polyglue/
│   │   └── src/
│   ├── cpp/
│   │   ├── CMakeLists.txt
│   │   └── include/polyglue/
│   ├── jni/
│   │   ├── CMakeLists.txt
│   │   ├── include/polyglue/
│   │   └── src/
│   ├── objc/
│   │   ├── CMakeLists.txt
│   │   ├── include/
│   │   └── src/
│   └── wasm/
│       ├── CMakeLists.txt
│       └── src/
├── tests/
│   ├── CMakeLists.txt
│   ├── conformance/
│   ├── native/
│   └── consumers/
├── examples/
│   ├── modules/
│   ├── c/
│   │   └── CMakeLists.txt
│   └── cpp/
│       └── CMakeLists.txt
├── build/                # ignored
└── dist/                 # ignored
```

Additional language support directories remain in the repository layout from section 20.1. Add a local CMakeLists.txt only where native compilation is needed. Prefer a single source list per component, explicit files rather than implicit recursive globbing, and small focused modules. Use official SDK toolchain files for Android NDK and Emscripten; use explicit Apple SDK/sysroot, architecture and deployment target settings. Do not duplicate vendor toolchain implementations or ship a custom Apple toolchain unless a demonstrated requirement justifies it.

#### 20.4.1 Targets and options

Stable exported CMake target names:

| Target | Responsibility |
| --- | --- |
| PolyGlue::runtime | Common C ABI and native support runtime |
| PolyGlue::cpp | Public C++ wrappers/headers; links runtime |
| PolyGlue::jni | Optional JNI support, linked only where needed |
| PolyGlue::objc | Optional Apple adapter, linked only where needed |
| PolyGlue::<module> | Generated module integration target where appropriate |

Use ordinary build targets with namespace aliases and exported install names. Generated module targets must have deterministic conflict-free names across products. Export exactly the public symbols required by the ABI and adapters; keep private symbols hidden. One shared runtime context per product even when several modules are linked. Static libraries are permitted, but composing static archives into multiple shared libraries must not create independent unintended runtime instances. Tests must detect this scenario. Use PIC for static objects linked into a shared library; do not leak build paths, warning flags or internal dependencies to consumers.

```cmake
# Proposed public options; exact defaults are part of the implementation contract.
option(POLYGLUE_BUILD_TESTS "Build native tests" OFF)
option(POLYGLUE_BUILD_EXAMPLES "Build examples" OFF)
option(POLYGLUE_BUILD_JNI "Build JNI adapter" OFF)
option(POLYGLUE_BUILD_OBJC "Build Apple adapter" OFF)
option(POLYGLUE_ENABLE_INSTALL "Enable install and export rules" ON)

set(POLYGLUE_LINKAGE "static" CACHE STRING "static or shared")
set_property(CACHE POLYGLUE_LINKAGE PROPERTY STRINGS static shared)

set(POLYGLUE_SANITIZER "none" CACHE STRING "Native instrumentation")
set_property(CACHE POLYGLUE_SANITIZER PROPERTY STRINGS
    none address thread undefined memory)
```

Validate every option and incompatible combination at configure time. Use target-scoped compile features, includes, definitions, link options and warnings. Only set default build type/output directories for the top-level project; do not overwrite parent project settings when used with add_subdirectory or FetchContent. Account for single-configuration and multi-configuration generators. Enable C, CXX, OBJC, OBJCXX or Swift only when required. Do not apply C/C++ flags to Swift or managed-language builds. Propagate ABI-affecting definitions through the public target, and keep private warnings private. MSVC, Clang and GCC receive compatible flags.

Sanitizer modes build and link every relevant native component with compatible instrumentation; TSan and ASan run separately. LSan is enabled with a supported ASan configuration or standalone where appropriate. MSan requires instrumented dependencies and a compatible toolchain. Never silently ignore a requested sanitizer. Validate actual instrumented binaries and execute a fault-detection probe in an isolated test harness. Avoid mixing sanitizer and production artifacts.

#### 20.4.2 Native dependency management

Keep core runtime dependency-free apart from the standard library and mandatory platform SDKs wherever practical. No JSON serializer, HTTP client, camera library or UI framework in core. A single canonical dependency declaration and CMake target graph controls dependency versions, options and link visibility.

- Default strategy: use standard CMake find_package for explicitly supplied packages and pinned FetchContent for necessary source dependencies (initially tests only if core remains dependency-free).
- Support preinstalled dependency targets, local source overrides and an offline cache; fail explicitly if a required dependency is unavailable in offline mode.
- Pin exact revisions or archive hashes; record dependency versions, licenses, source hashes and build options in artifact metadata.
- Separate test-only dependencies, such as a native test framework if justified, from public installed targets. Do not install or link them into production libraries.
- Do not add a second dependency manager merely to match another project. CPM or Conan integration may be supported behind the same CMake target interface if a concrete need is demonstrated and the complete corresponding CI matrix passes. Do not require both.
- Resolve SDK-specific dependencies through the ecosystem tool: Gradle/Maven, SwiftPM, uv/pip, NuGet, pub, npm, and official SDKs. Use lockfiles or equivalent pinned versions appropriate to each ecosystem. No hidden downloads at generation time.
- Cross-compiling dependencies must use the same target sysroot, ABI, compiler/runtime, sanitizer and deployment floor as the product. Never link host binaries into target outputs. Separate caches by toolchain and target.
- User-owned native implementation dependencies remain the user's responsibility; expose explicit target-based integration instead of rewriting their build files.

Supply documented dependency configuration, provenance and troubleshooting. Verify clean online setup and offline rebuild from populated cache. Prefer standard tooling over a custom package manager.

#### 20.4.3 Consumer integration and installation

Support all three native consumption modes:

```cmake
# Source integration
add_subdirectory(path/to/polyglue-runtime)
target_link_libraries(app PRIVATE PolyGlue::runtime)
```

```cmake
# Installed package
find_package(PolyGlue CONFIG REQUIRED)
target_link_libraries(app PRIVATE PolyGlue::runtime PolyGlue::cpp)
```

```cmake
# Pinned source dependency
include(FetchContent)
FetchContent_Declare(polyglue
    GIT_REPOSITORY https://github.com/polyglue/polyglue.git
    GIT_TAG <reviewed-release-or-commit>)
FetchContent_MakeAvailable(polyglue)
target_link_libraries(app PRIVATE PolyGlue::runtime)
```

The final implementation must provide relocatable config/version/target files, proper BUILD_INTERFACE and INSTALL_INTERFACE paths, runtime headers, correct transitive dependencies and optional generated module package exports. Test an independent consumer from a relocated installation, not just a target inside the repository. Test both static/shared linkage, multiple generated modules, custom implementation sources and a consumer with its own build flags. Never overwrite an existing consumer CMakeLists.txt unless explicitly generating a new package into an owned directory.

### 20.5 Python build orchestration and artifact pipeline

The Python CLI coordinates tools; it does not reimplement the compiler, linker, Gradle, Xcode or package manager. Use standard subprocess APIs with argument lists, explicit cwd and environment, checked exit codes and bounded timeouts. No shell-string concatenation or task-specific global mutable state. Log tool commands and versions with secrets redacted. SDK discovery runs only for commands that need the SDK.

Proposed package organization:

```text
src/polyglue/
├── cli/
├── config/
├── parser/
├── semantic/
├── ir/
├── backends/
├── templates/
└── build/
    ├── plan.py
    ├── runner.py
    ├── toolchains.py
    ├── cmake.py
    ├── artifacts.py
    ├── verify.py
    └── packagers/
        ├── android.py
        ├── apple.py
        ├── desktop.py
        ├── python.py
        ├── dart.py
        ├── dotnet.py
        └── web.py
```

This structure is conceptual; consolidate small functions rather than creating excessive files. Build plans are immutable data describing commands, input fingerprints, dependencies and expected outputs. The plan is inspectable before execution, supports host/target distinction, and validates requested SDKs/platforms/architectures up front.

Pipeline:

```text
Read configuration and product definition
                  |
Resolve IDL and native dependency closure
                  |
Validate host tools and target capabilities
                  |
Generate selected module sources
                  |
Plan target-specific native build slices
                  |
CMake configure -> compile -> stage/install
                  |
Ecosystem build (Gradle, Xcode, etc.)
                  |
Assemble final package and debug symbols
                  |
Inspect artifact ABI, architecture, exports, metadata
                  |
Install in separate consumer and execute conformance
                  |
Publish local artifact manifest and test evidence
```

The same CLI and code path is used locally, by Makefile and in GitHub Actions. The Makefile exposes thin aliases such as setup, lint, test, build, package, docs and clean; it must not duplicate build logic or assume all SDKs are available. No hidden IDE-only steps. If generating sources for an existing project, users can still build them using their own tools without the PolyGlue CLI.

#### 20.5.1 Build directories and incremental behavior

```text
build/polyglue/
└── <product>/
    └── <platform>/
        └── <sdk-variant>/
            └── <architecture>/
                └── <configuration>/
                    └── <sanitizer>/
                        ├── generated/
                        ├── cmake/
                        ├── stage/
                        ├── logs/
                        └── build-manifest.json
dist/
└── <product>/
    └── <version>/
        └── <format>/
            ├── <validated-artifact>
            ├── artifact-manifest.json
            └── checksums.sha256
```

Generated source outputs configured by the module may reside outside build/; the build plan references them or stages a snapshot without rewriting user files. Build cache keys include generator/runtime version, canonical IDL, effective config, all used templates, implementation source fingerprints, dependencies, compiler/SDK, architecture, flags and configuration. Do not reuse a previous artifact for a changed build plan. The tool must detect stale or missing outputs, unexpected files, architecture mismatches and interrupted builds. Clean only explicitly owned directories (never recursive deletion based on an unvalidated path). Temporary staging and atomic publication prevent partial packages appearing successful. Incremental output is equivalent to a clean build.

### 20.6 Binary and package outputs by target

All formats below are intended deliverables. A binary artifact is not considered supported until a separate consumer project installs/links and executes it.

| Target | Required final artifact / integration | Producer |
| --- | --- | --- |
| C | Static archive, shared library, public headers, relocatable CMake package | CMake |
| C++ | Static/shared library, C++ headers, generated module targets, CMake package | CMake |
| Java desktop | JAR with Java API and declared platform native library packaging; Maven metadata | Gradle + CMake JNI |
| Kotlin desktop | JAR with Kotlin/JVM API and native loader/distribution; Maven metadata | Gradle + CMake JNI |
| Java/Kotlin Android | AAR with classes.jar, manifest, consumer rules, ABI-specific JNI .so, POM/dependency metadata as required | Gradle + Android NDK/CMake |
| Objective-C | Native library/framework, public headers and module map, XCFramework for supported Apple slices | CMake + Apple SDK/Xcode |
| Swift | Swift module/framework, XCFramework and source or binary SwiftPM integration | SwiftPM/Xcode + CMake |
| Python generator | Pure Python wheel and sdist with templates, grammar and runtime sources | Python build backend / uv |
| Python bindings | Target-specific wheel with Python API and compiled native adapter; source distribution | Python packaging + CMake |
| Dart | Dart package with generated API and native assets/loading integration, plus separate web adapter | pub tooling + CMake |
| Flutter | Flutter plugin package and native dependencies for selected platforms; example app builds | Flutter + Gradle/Xcode/CMake |
| C# | NuGet package with managed assemblies and native RID-specific assets | dotnet pack + CMake |
| JavaScript | npm package with actual JS loader/runtime, ESM exports, WASM assets where needed | npm + Emscripten/CMake |
| TypeScript | npm package with valid declarations and matching JS runtime/exports | tsc + npm |
| WebAssembly | .wasm binary, generated JS loader, declarations and any required worker assets | Emscripten + CMake |

Examples are real applications but are not substitutes for reusable library artifacts. Platform application artifacts (APK, desktop executable, simulator .app, web bundle) are built and exercised separately. Signing, notarization, mobile distribution and registry publication require appropriate credentials and explicit authorization; local unsigned/test artifacts remain supported when the SDK permits.

#### 20.6.1 Android AAR and desktop JVM JAR

AAR packaging must support Java-only, Kotlin-only and intentional shared Java/Kotlin output.

```text
app_bridge.aar
├── AndroidManifest.xml
├── classes.jar
├── proguard.txt                 # consumer rules when needed
└── jni/
    ├── arm64-v8a/libapp_bridge.so
    ├── armeabi-v7a/libapp_bridge.so
    └── x86_64/libapp_bridge.so
```

Illustrative ABI list; the artifact must match the explicitly configured requested ABIs. Build one CMake slice per ABI with the official NDK, selected API floor and consistent C++ runtime/linkage. Stage only current native outputs. Gradle assembles the AAR using generated Java/Kotlin classes and native libraries, correct namespace/minSdk, dependency metadata and consumer R8 rules for any JNI-resolved methods/classes. Preserve required native library loading names and register JNI methods reliably. Handle shared C++ runtime dependencies without duplicate inconsistent copies.

Inspect AAR ZIP contents, class signatures, ABI directories, ELF machine type, dynamic dependencies, exported JNI entry points and applicable Android page-size/alignment requirements using SDK/NDK tools. Verify release shrinker behavior with R8 and real release consumer invocation. Strip production symbols as configured; retain matching external debug symbols and build IDs. Install the AAR in a separate Android sample via local Maven or direct AAR with explicitly declared transitive dependencies. Run instrumented tests on configured emulator/device; verify the package rather than compiling the source module directly.

For desktop JAR, use a documented native-loader strategy and platform/architecture-specific native resources or explicit native companion artifacts. Validate library paths, classpath and Maven dependencies; test loading in a clean process on each advertised host and architecture. Do not assume an Android AAR can serve desktop JVM consumers.

#### 20.6.2 Apple XCFramework and SwiftPM

Build Apple platforms through explicit SDK and architecture slices. Keep device, simulator and Mac Catalyst distinct even when all use arm64. Merge architectures only inside the same SDK/platform variant and compatible deployment/build configuration; do not merge device and simulator binaries into a single Mach-O.

| Platform | Slice policy |
| --- | --- |
| iOS/iPadOS | Device and simulator variants |
| macOS | Requested supported arm64/x86_64 architectures |
| tvOS | Device and simulator variants |
| watchOS | Device and simulator variants supported by selected SDK |
| visionOS | Device and simulator variants |
| Mac Catalyst | Separate macabi variant, not ordinary macOS |

Use Xcode/Apple SDK tools to build frameworks or static libraries with headers. For Swift public binary distribution, use library evolution/module stability where applicable, verify .swiftinterface and module metadata, and avoid forcing it for source-only builds. Objective-C headers, module maps and umbrella header names must agree with configured module prefixes and Swift imports. Preserve framework symlinks, resources and bundle metadata when staging/archiving. Use xcodebuild -create-xcframework for final assembly, not a hand-written fake bundle.

```text
AppBridge.xcframework/
├── Info.plist
├── <ios-device-slice>/
│   └── AppBridge.framework/
├── <ios-simulator-slice>/
│   └── AppBridge.framework/
├── <macos-slice>/
│   └── AppBridge.framework/
├── <visionos-device-slice>/
│   └── AppBridge.framework/
└── <visionos-simulator-slice>/
    └── AppBridge.framework/
```

The actual slice identifiers are produced by Apple tools, not guessed by PolyGlue. Include requested tvOS/watchOS/Catalyst variants as configured. Verify Info.plist library descriptors, Mach-O architecture, LC_BUILD_VERSION platform and minimum OS, actual optimization settings, public symbols, module interfaces, dependency install names/rpaths, and any required code signatures. Generate debug symbols where applicable and verify dSYM UUIDs match the exact slice binaries; static libraries need a documented symbolication strategy rather than invented dSYM guarantees. Preserve original Swift compiler interface metadata; remove machine-specific paths only by supported reproducible build configuration, never by modifying binary signatures or invalidating module interfaces. Signing policy is explicit; no credentials required for unsigned simulator builds.

SwiftPM binary packaging produces an XCFramework archive preserving framework structure, checksum using swift package compute-checksum, and a valid Package.swift with configured platforms, products and binaryTarget URL/checksum or local path. No fabricated download URL. A local archive/package must be usable before remote publication; publishing is separate. Verify fresh SwiftPM/Xcode consumers import generated APIs and run on requested simulator/device; include Objective-C and Swift consumers. Test visionOS independently. Verify package contains exactly the requested valid slices and no stale sanitizer/debug slice.

#### 20.6.3 Desktop libraries and native packages

Stage CMake install output: include/, lib/, bin/ where applicable, CMake package config/targets, runtime dependency metadata and license notices. Build .a/.so, .a/.dylib or .lib/.dll with correct platform naming; Windows import libraries travel with DLLs. Inspect exports, architecture, runtime dependencies, SONAME/install name/rpath, CRT configuration and public ABI. Package relocatable install archives without build-machine absolute paths. Verify find_package after moving the install tree and run a separate consumer with custom generated modules. Distribute per-platform/architecture artifacts rather than implying binary portability across OSes.

#### 20.6.4 Python, Dart, Flutter, C# and web packages

- Python: generator wheel remains pure Python and includes resource files. Compiled bindings wheel has correct platform/interpreter tags, native dependencies and loader paths; test import in clean venv outside source tree, installed package resource access and native calls. Do not publish a platform binary as a universal wheel.
- Dart: produce source package and native library asset configuration for supported native targets; verify loading from an independent pub consumer. Web package uses conditional imports and JS/WASM adapter; no FFI on web.
- Flutter: generate platform plugin integration and stage AAR/JNI or XCFramework/native source integration where appropriate. Keep one runtime instance per intended shared context. Desktop plugins use CMake/SDK builds; web bundles use JS/WASM. Validate actual plugin installation into clean app, build and run for every supported platform. No symlink pointing back into a developer's build tree in a distributable.
- C#: dotnet pack emits .nupkg with managed assemblies and native assets under runtimes/<rid>/native plus appropriate dependency metadata. Validate RID and ABI resolution, package dependencies, managed assembly/native version pairing, and install from a local NuGet feed into a new project. Test native callback and ownership across the packaged ABI.
- JS/TS/WASM: package exports and types resolve from a clean consumer; include .wasm and required JS/worker assets, correct loader URL handling and relative asset paths. Verify npm pack contents, browser and Node execution, memory growth, BigInt mapping and TypeScript declaration compatibility. Do not claim a .d.ts-only package is an implementation.

### 20.7 Artifact provenance and release validation

A successful package command emits an artifact manifest only after inspection. Record product/version, requested and actual platforms/architectures, format, module/type/ABI fingerprints, toolchain versions, source revision, dependency hashes, templates, build flags, configuration, sanitizer, file hashes, exported symbol summary, debug symbol identifiers and verification results. Use portable paths relative to the artifact root. Record test evidence separately from build provenance. Artifact generation is allowed before full support is verified; release approval requires independent package consumer tests and every required acceptance gate.

Verify reproducibility where toolchains permit it. Deterministic generation is mandatory; do not promise bit-for-bit equality of signed archives or compiler-specific outputs without evidence. Use checksums to identify final bytes and store release/debug variants separately. Never reuse stale binaries or overwrite an existing published release. Publishing to PyPI, Maven, SwiftPM release hosting, pub, NuGet or npm is explicitly separate from local packaging.

### 20.8 Build and packaging documentation

Add docs/build.md, docs/dependencies.md, docs/packaging.md, docs/templates.md and per-format guides for CMake, Android AAR/JAR, Apple XCFramework/SwiftPM, Python wheels, Dart/Flutter, NuGet and npm/WASM. Explain prerequisites, CLI commands, configuration, output directory, standalone consumer integration, debugging, supported architectures and offline dependency setup. Include complete copyable examples and verify them in CI. AGENTS.md requires keeping the toolchain/build layout consistent, using the CLI for CI, testing artifacts independently and not introducing unnecessary dependencies or duplicate build systems.

## 21. Implementation phases and reviews

| Phase | Deliverables | Gate |
| --- | --- | --- |
| 0 — specification | PROJECT.md, detailed examples, scope review | No missing discussed feature; unresolved choices explicitly recorded |
| 1 — compiler | Package, CLI, parser, IR, module config, naming/layout/import/annotation systems, template overrides, diagnostics and build-plan foundation | Compiler tests, template override tests and clean wheel installation |
| 2 — native base | Versioned C ABI, C/C++ generated bindings, memory, async, callbacks, CMake target/install graph and Python native build orchestration | C/C++ conformance, sanitizer pass and independent installed package consumer |
| 3 — JVM and Apple | Java/Kotlin/JNI, Obj-C/Swift, cross-runtime adapters, AAR/JAR and XCFramework/SwiftPM packagers | JVM/Android and Apple conformance plus actual packaged consumer tests |
| 4 — additional targets | Python, C#, Dart/Flutter, WASM/JS/TS and their packagers | All target-specific integration and installed artifact tests |
| 5 — advanced features | Complete type system, generics, external types, streams, optional registry, package/manifest modes | All applicable type/pair combinations pass |
| 6 — applications and docs | HTTP, camera, login per target, SVG, README, AGENTS.md, complete docs | Executable examples and accurate documentation |
| 7 — stabilization | Full CI, sanitizer, fuzz, stress, performance and deep reviews | All release acceptance gates green on candidate SHA |

Every phase includes implementation, automated tests, review and fixes. Tests are developed alongside the feature, not deferred to phase 7. Do not expand scope with unnecessary frameworks or abstractions. Review runtime contracts and compiler configuration before locking public APIs.

Explicit remaining design decisions to settle with proof-of-concept and tests: exact grammar, concrete ABI declarations, safe handle representation, detailed type mapping (especially unsigned/64-bit web values), executor policies, shared JVM/Apple artifact strategies, stream backpressure configuration and registry duplicate/override API. These are engineering design gates, not permission to drop requirements.

## 22. Release acceptance checklist

- [ ] Generator is installable and usable locally/offline; official packaging validated.
- [ ] Partial and individual template overrides, precedence, template export/check and custom build templates are proven in every target.
- [ ] CMake structure, dependency resolution, install/export and independent consumers work without changing consumer settings.
- [ ] Python CLI generates, builds, tests and packages every target; clean/incremental and failure behavior proven.
- [ ] AAR/JAR, XCFramework/SwiftPM, desktop libraries, native wheels, Dart/Flutter, NuGet and npm/WASM outputs are inspected and consumed in separate test projects.
- [ ] Every required IDL construct, configuration option, naming feature and annotation is implemented and tested.
- [ ] Module-specific paths, prefixes, dependencies and imports work in independent source/prebuilt builds.
- [ ] All required target languages and feasible directions pass actual generated-code conformance.
- [ ] All types, valid nested types and async return categories have evidence; forbidden combinations fail explicitly.
- [ ] DataView, MutableDataView, DataRef, callbacks, cancellation, streams and service replacement pass lifecycle tests.
- [ ] HTTP, camera/grayscale and login examples are runnable; device-dependent claims have appropriate evidence.
- [ ] Memory, ownership, leaks, deadlocks, races, use-after-free and other defined failure cases have automated tests.
- [ ] All required CI jobs pass on the exact release revision; no hidden mandatory skips.
- [ ] Deep review completed for every language, platform, runtime, ABI and generated API.
- [ ] Logo, README, AGENTS.md, documentation and capability matrix accurately match verified support.
- [ ] Owner authorizes license and package publication.

Completion means reproducible evidence for every acceptance gate, not a claim of mathematically bug-free software.
