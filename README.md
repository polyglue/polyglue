<p align="center">
    <a href="https://github.com/polyglue/polyglue" target="_blank" rel="noopener noreferrer"><img width="120" src="extras/images/logo.svg" alt="PolyGlue logo"></a>
</p>

<h1 align="center">PolyGlue</h1>

<p align="center">
    Connect programming languages with native, type-safe code generation.
</p>

<p align="center">
    <strong>Version 0.0.1 — In development</strong>
</p>

## Project

PolyGlue is a code generator that allows different programming languages to call each other's methods and exchange data within the same application.

Define your data types and interfaces once in a common definition language (IDL). PolyGlue generates the native bindings for each selected language, removing the need to write and maintain the connecting code by hand.

For example, implement a feature in C++, Kotlin or Swift and call it from Flutter, Python or another compatible language. Calls work in both directions, without a server or mandatory JSON serialization.

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

## Supported languages and platforms

| | Language | Platforms |
| --- | --- | --- |
| ⚙️ | C | Desktop, Android, Android XR, Apple, Web/Node.js via WASM |
| ⚙️ | C++ | Desktop, Android, Android XR, Apple, Web/Node.js via WASM |
| ☕ | Java | Desktop, Android, Android XR |
| 🟣 | Kotlin | Desktop, Android, Android XR |
| 🍎 | Objective-C | Apple |
| 🐦 | Swift | Apple |
| 🐍 | Python | Desktop |
| 🎯 | Dart | Desktop, Android, iOS/iPadOS, Web |
| 🟪 | C# | Desktop |
| 🟨 | JavaScript | Web, Node.js |
| 🟦 | TypeScript | Web, Node.js |

| | Integration target | Platforms |
| --- | --- | --- |
| 🦋 | Flutter | Desktop, Android, iOS/iPadOS, Web |
| 🌐 | WebAssembly | Web, Node.js |

Desktop includes Linux, Windows and macOS. Apple includes macOS, iOS, iPadOS, tvOS, watchOS, visionOS and Mac Catalyst. The exact target matrix is in [PROJECT.md](PROJECT.md#2-supported-languages-and-platforms).

## Documentation

- [Project specification](PROJECT.md) — architecture, types, diagrams, examples and roadmap.
- [Engineering guidelines](AGENTS.md) — development and contribution rules.

## Contributing

Report bugs or suggest improvements through [GitHub Issues](https://github.com/polyglue/polyglue/issues). Read [AGENTS.md](AGENTS.md) before contributing.

## Support

Support the ongoing development of this project through [GitHub Sponsors](https://github.com/sponsors/paulocoutinhox) or [Ko-fi](https://ko-fi.com/paulocoutinho).

## License

The license has not been finalized yet.

---

Made with ❤️ by [Paulo Coutinho](https://github.com/paulocoutinhox).
