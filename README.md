<p align="center">
    <a href="https://github.com/polyglue/polyglue"><img width="100" src="extras/images/logo.svg" alt="PolyGlue logo"></a><br>
    <strong>PolyGlue</strong><br>
    Connect programming languages with native, type-safe code generation.<br>
    <sub>Version 0.0.1 · In development</sub>
</p>

## Project

PolyGlue is a code generator that allows different programming languages to call each other's methods and exchange data within the same application.

Define your data types and interfaces once in a common definition language (IDL). PolyGlue generates the native bindings for each selected language, removing the need to write and maintain the connecting code by hand.

For example, share the same C++ code between an iOS app written in Swift and an Android app written in Kotlin. Calls work in both directions within each app, without a server or mandatory JSON serialization.

<p align="center">
    <img width="740" src="extras/images/how-it-works.svg" alt="PolyGlue generates Swift and Kotlin bindings so iOS and Android apps can each use the same C++ source code.">
</p>

> PolyGlue is in early development. The features and targets below are planned, not verified support.

## Features

- 🔗 **Native bindings:** type-safe calls and implementations in both directions.
- 🧩 **Modular IDL:** reusable records, enums, interfaces, variants and generic types.
- 📚 **Type system:** collections, nullable values, UTC timestamps and typed results.
- 🧬 **Custom types:** extend the type system with your own adapters.
- ⚡ **Async:** asynchronous methods, callbacks, streams and cancellation.
- 💾 **Memory:** borrowed views, owning references and zero-copy buffers where supported.
- 🔄 **Services:** optional registration, discovery and replacement of implementations.
- 🎨 **Customization:** module-specific naming, prefixes, annotations and template overrides.
- 🛠️ **Build tools:** generate, compile and test with one Python command-line tool.
- 📦 **SDK packaging:** versioned native libraries, AARs, XCFrameworks and language packages.
- ☁️ **Deploy:** upload validated SDKs to Amazon S3, Cloudflare R2 and compatible storage.

## Supported languages

- ⚙️ C
- ⚙️ C++
- ☕ Java
- 🟣 Kotlin
- 🍎 Objective-C
- 🐦 Swift
- 🐍 Python
- 🎯 Dart
- 🟪 C#
- 🟨 JavaScript
- 🟦 TypeScript

Integration targets:

- 🦋 Flutter
- 🌐 WebAssembly

## Supported platforms

Linux, Windows, macOS, Android, Android XR, iOS, iPadOS, tvOS, watchOS, visionOS, Mac Catalyst, Web and Node.js.

Choose the languages and targets for your project and compile the generated code with the appropriate toolchains. See the [target matrix](PROJECT.md#2-supported-languages-and-platforms) for planned runtime and build coverage.

## Documentation

- [Project specification](PROJECT.md) — architecture, types, diagrams, examples and roadmap.
- [Engineering guidelines](AGENTS.md) — development and contribution rules.

## Contributing

Report bugs or suggest improvements through [GitHub Issues](https://github.com/polyglue/polyglue/issues). Read [AGENTS.md](AGENTS.md) before contributing.

## Support

Support the ongoing development of this project through [GitHub Sponsors](https://github.com/sponsors/paulocoutinhox) or [Ko-fi](https://ko-fi.com/paulocoutinho).

## License

The license has not been finalized yet.

Made with ❤️ by [Paulo Coutinho](https://github.com/paulocoutinhox).
