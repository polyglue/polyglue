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
- [12. Native runtime and ABI](#12-native-runtime-and-abi)
- [13. Memory and buffers](#13-memory-and-buffers)
- [14. Asynchronous operations callbacks and streams](#14-asynchronous-operations-callbacks-and-streams)
- [15. Interfaces and service discovery](#15-interfaces-and-service-discovery)
- [16. Language-specific integration](#16-language-specific-integration)
- [17. Example applications](#17-example-applications)
- [18. Test specification](#18-test-specification)
- [19. GitHub Actions](#19-github-actions)
- [20. Repository documentation and branding](#20-repository-documentation-and-branding)
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
| packaging | Wheel/sdist install, resource availability, CLI from clean environment |
| httpbin-live | External HTTP smoke with separate network failure reporting |

Use workflow names/filenames consistently (e.g. .github/workflows/c.yml). Only add README badges for real workflows. Each job regenerates its inputs and fails if required tests did not execute. Do not replace real test jobs with echo commands, empty matrices or allow-failure.

### 19.2 CI rules

PR and main runs execute mandatory checks. Expensive fuzzing and extended platform coverage also run nightly and before release; release gates require all mandatory evidence on the exact candidate SHA. Pin reviewed toolchains and action revisions, use least permissions, safe caches, timeouts and reproducible build environments. No secrets in untrusted PR jobs.

Collect JUnit/CTest reports, sanitizer output, coverage, copy counts, platform/test matrix, build logs and benchmark data as artifacts. Confirm jobs actually ran, inspect failures, fix root causes, rerun and record the SHA. Platform/runner unavailability remains an explicit blocker. Do not claim a passing run from a queued workflow or successful compilation alone.

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
├── LICENSE
├── src/polyglue/
│   ├── cli/
│   ├── config/
│   ├── parser/
│   ├── semantic/
│   ├── ir/
│   ├── diagnostics/
│   ├── backends/
│   └── templates/
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

## 21. Implementation phases and reviews

| Phase | Deliverables | Gate |
| --- | --- | --- |
| 0 — specification | PROJECT.md, detailed examples, scope review | No missing discussed feature; unresolved choices explicitly recorded |
| 1 — compiler | Package, CLI, parser, IR, module config, naming/layout/import/annotation systems, templates and diagnostics | Compiler tests and clean wheel installation |
| 2 — native base | Versioned C ABI, C/C++ generated bindings, memory, async and callback foundation | C/C++ conformance and sanitizer pass |
| 3 — JVM and Apple | Java/Kotlin/JNI, Obj-C/Swift, cross-runtime adapters | JVM/Android and Apple platform conformance |
| 4 — additional targets | Python, C#, Dart/Flutter, WASM/JS/TS | All target-specific integration tests |
| 5 — advanced features | Complete type system, generics, external types, streams, optional registry, package/manifest modes | All applicable type/pair combinations pass |
| 6 — applications and docs | HTTP, camera, login per target, SVG, README, AGENTS.md, complete docs | Executable examples and accurate documentation |
| 7 — stabilization | Full CI, sanitizer, fuzz, stress, performance and deep reviews | All release acceptance gates green on candidate SHA |

Every phase includes implementation, automated tests, review and fixes. Tests are developed alongside the feature, not deferred to phase 7. Do not expand scope with unnecessary frameworks or abstractions. Review runtime contracts and compiler configuration before locking public APIs.

Explicit remaining design decisions to settle with proof-of-concept and tests: exact grammar, concrete ABI declarations, safe handle representation, detailed type mapping (especially unsigned/64-bit web values), executor policies, shared JVM/Apple artifact strategies, stream backpressure configuration and registry duplicate/override API. These are engineering design gates, not permission to drop requirements.

## 22. Release acceptance checklist

- [ ] Generator is installable and usable locally/offline; official packaging validated.
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
