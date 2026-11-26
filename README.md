<p align="center">
    <a href="https://github.com/polyglue/polyglue" target="_blank" rel="noopener noreferrer"><img width="120" src="extras/images/logo.svg" alt="PolyGlue logo"></a>
</p>

<h1 align="center">PolyGlue</h1>

<p align="center">
    One definition. Multiple languages. Native interoperability.
</p>

<p align="center">
    <strong>Version 0.0.1 — In development</strong>
</p>

## Project

PolyGlue is a cross-platform interface compiler and code generator designed to connect programming languages through native, strongly typed interfaces.

Define your models and interfaces once, then generate bindings for multiple languages. Implement a contract in Kotlin, Swift, C++ or another supported runtime and consume it from a different language without a server or mandatory serialization.

> PolyGlue is in early development. The features and targets below describe the planned scope, not verified support.

## Features

- 🔗 **Native interoperability:** bidirectional calls through generated interfaces and bindings.
- 🧩 **Modular IDL:** reusable models, interfaces and independent modules.
- 📚 **Rich types:** records, collections, enums, results, dates and custom external types.
- ⚡ **Asynchronous operations:** native async APIs, callbacks, streams and cancellation.
- 💾 **Shared memory:** explicit ownership and zero-copy buffers where supported.
- 🔄 **Service discovery:** optional registry with replaceable implementations.
- 🎨 **Customization:** per-module naming, prefixes, annotations and template overrides.
- 🛠️ **Build tools:** one Python CLI for generation, compilation, testing and packaging.
- 📦 **SDK distribution:** versioned AAR, XCFramework, native libraries and ecosystem packages.
- ☁️ **Cloud deployment:** optional upload to Amazon S3, Cloudflare R2 and compatible storage.
- ✅ **Quality:** automated cross-language, memory, concurrency and packaged-consumer tests.

## Supported languages and platforms

The following targets are planned. Each combination is confirmed only after its build and runtime tests pass.

### Languages

C, C++, Java, Kotlin, Objective-C, Swift, Python, Dart, C#, JavaScript and TypeScript.

Flutter and WebAssembly are also planned integration targets.

### Platforms

| Platform | Primary targets |
| --- | --- |
| 🐧 Linux | C, C++, Java, Kotlin, Python, Dart, Flutter, C# |
| 🪟 Windows | C, C++, Java, Kotlin, Python, Dart, Flutter, C# |
| 🍎 macOS | C, C++, Objective-C, Swift, Java, Kotlin, Python, Dart, Flutter, C# |
| 🤖 Android | C, C++, Java, Kotlin, Dart, Flutter |
| 🥽 Android XR | C, C++, Java, Kotlin |
| 📱 iOS and iPadOS | C, C++, Objective-C, Swift, Dart, Flutter |
| 📺 tvOS | C, C++, Objective-C, Swift |
| ⌚ watchOS | C, C++, Objective-C, Swift |
| 🥽 visionOS | C, C++, Objective-C, Swift |
| 💻 Mac Catalyst | C, C++, Objective-C, Swift |
| 🌐 Web | WebAssembly, JavaScript, TypeScript, Dart and Flutter Web where supported |

## Workflow

Define → Generate → Build → Test → Package → Deploy (optional).

See the [compiler pipeline](PROJECT.md#111-pipeline) and [SDK distribution workflow](PROJECT.md#205-python-build-orchestration-and-artifact-pipeline) for details.

## Documentation

- [Project specification](PROJECT.md)
- [Engineering and contribution rules](AGENTS.md)

Installation instructions, usage examples and language guides will be added as the implementation is verified. No package has been released yet.
