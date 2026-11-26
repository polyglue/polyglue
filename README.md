# PolyGlue

**One definition. Multiple languages. Native interoperability.**

PolyGlue is a cross-platform interface compiler and code generator designed for type-safe, bidirectional interoperability between programming languages.

Define your data models, interfaces, callbacks, and asynchronous operations once, then generate idiomatic native bindings for multiple languages. Implementations can live in any compatible target runtime, rather than being restricted to C++.

> **Development version:** 0.0.1 (unreleased).
>
> **Project status:** Early design and development. The features, targets, and APIs described below are planned, not yet implemented or released.

## Goals

- Python-based compiler with customizable Jinja2 templates.
- Independent, modular interface definition language (IDL).
- Bidirectional native calls without mandatory serialization or network transport.
- Strongly typed records, enums, interfaces, collections, results, callbacks, async operations, and streams.
- Explicit memory ownership, borrowed data views, and shared buffers with zero-copy transfers where supported.
- Optional service discovery and replaceable implementations.
- Per-module and per-target configuration for naming conventions, prefixes, namespaces, packages, output paths, imports, annotations, and formatting.
- Native support libraries maintained and tested in the same repository as the generator.
- Deterministic code generation and integration with existing build systems.
- Distribution through PyPI, local installation, and standalone tooling.

## Example

The following IDL illustrates the proposed syntax:

```typescript
module domain;

record User {
    id: int64;
    name: string;
}
```

```typescript
module repository;

import domain.User;

interface UserRepository {
    async findById(id: int64): optional<User>;
    async findAll(): list<User>;
    async count(): int64;
    async exists(id: int64): bool;
}
```

A repository implemented in Kotlin could be consumed from Dart, Swift, or C++ when the corresponding runtimes are available in the same execution environment. Generated adapters would handle type conversion, object references, async completion, and lifecycle management.

## Planned targets

| Language | Interoperability mechanism |
| --- | --- |
| C | C ABI |
| C++ | Native interfaces |
| Java / Kotlin | JNI |
| Objective-C | Objective-C++ |
| Swift | Native Apple adapters |
| Python | CPython adapters |
| Dart / Flutter | FFI and platform adapters |
| C# | .NET native interoperability |
| JavaScript / TypeScript | WebAssembly and JavaScript adapters |

Planned platforms include Windows, Linux, macOS, Android, Android XR, iOS, iPadOS, tvOS, watchOS, visionOS, Mac Catalyst, and WebAssembly. Actual target combinations depend on runtime and platform capabilities.

## Architecture

```text
IDL + Module Configuration
           |
    Python Compiler
           |
    Semantic IR
           |
    Language Backends + Templates
           |
    Generated Native Bindings
           |
    Native Support Runtime
```

The compiler and generator are build-time tools. Generated applications do not require Python unless Python is itself a selected runtime target.

## Quality and testing

PolyGlue aims to provide independent CI jobs for every supported language, platform-specific integration tests, cross-language conformance tests, memory and ownership validation, copy tracking, concurrency stress tests, fuzzing, sanitizers, and performance benchmarks.

Support will be declared only after the corresponding implementation and tests are available.

## Installation

PolyGlue is not yet published. Development builds are for local and CI testing only. PyPI publication requires completed acceptance checks and explicit owner approval.

## Documentation

- [Project specification](PROJECT.md)
- [Engineering and contribution rules](AGENTS.md)

## Design

PolyGlue is an independent project. It does not aim for compatibility with existing IDL tools and does not require Protocol Buffers.
