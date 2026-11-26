<p align="center">
    <a href="https://github.com/polyglue/polyglue"><img width="180" src="extras/images/logo.svg" alt="PolyGlue logo"></a><br>
    <strong>PolyGlue</strong><br>
    Generate native type-safe bindings from a single definition to connect programming languages across platforms.<br>
    <sub>Version 0.0.1</sub>
</p>

## Project

PolyGlue is a code generator that allows different programming languages to call each other's methods and exchange data within the same application.

Define your data types and interfaces once in a common definition language (IDL). PolyGlue generates the native bindings for each selected language, removing the need to write and maintain the connecting code by hand.

For example, share the same C++ code between an iOS app written in Swift and an Android app written in Kotlin. Calls work in both directions within each app, without a server or mandatory JSON serialization.

<p align="center">
    <img width="740" src="extras/images/how-it-works.svg" alt="PolyGlue generates Swift and Kotlin bindings so iOS and Android apps can each use the same C++ source code.">
</p>

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

## Languages

<p align="center">
    <img src="extras/images/languages/c.svg" width="88" height="88" alt="C" title="C">
    <img src="extras/images/languages/cpp.svg" width="88" height="88" alt="C++" title="C++">
    <img src="extras/images/languages/java.svg" width="88" height="88" alt="Java" title="Java">
    <img src="extras/images/languages/kotlin.svg" width="88" height="88" alt="Kotlin" title="Kotlin">
    <img src="extras/images/languages/objective-c.svg" width="88" height="88" alt="Objective-C" title="Objective-C">
    <img src="extras/images/languages/swift.svg" width="88" height="88" alt="Swift" title="Swift">
    <img src="extras/images/languages/python.svg" width="88" height="88" alt="Python" title="Python">
    <img src="extras/images/languages/dart.svg" width="88" height="88" alt="Dart" title="Dart">
    <img src="extras/images/languages/csharp.svg" width="88" height="88" alt="C#" title="C#">
    <img src="extras/images/languages/javascript.svg" width="88" height="88" alt="JavaScript" title="JavaScript">
    <img src="extras/images/languages/typescript.svg" width="88" height="88" alt="TypeScript" title="TypeScript">
</p>

## Platforms

<p align="center">
    <img src="extras/images/platforms/linux.svg" width="88" height="88" alt="Linux" title="Linux">
    <img src="extras/images/platforms/windows.svg" width="88" height="88" alt="Windows" title="Windows">
    <img src="extras/images/platforms/macos.svg" width="88" height="88" alt="macOS" title="macOS">
    <img src="extras/images/platforms/android.svg" width="88" height="88" alt="Android" title="Android">
    <img src="extras/images/platforms/android-xr.svg" width="88" height="88" alt="Android XR" title="Android XR">
    <img src="extras/images/platforms/ios.svg" width="88" height="88" alt="iOS" title="iOS">
    <img src="extras/images/platforms/ipados.svg" width="88" height="88" alt="iPadOS" title="iPadOS">
    <img src="extras/images/platforms/tvos.svg" width="88" height="88" alt="tvOS" title="tvOS">
    <img src="extras/images/platforms/watchos.svg" width="88" height="88" alt="watchOS" title="watchOS">
    <img src="extras/images/platforms/visionos.svg" width="88" height="88" alt="visionOS" title="visionOS">
    <img src="extras/images/platforms/mac-catalyst.svg" width="88" height="88" alt="Mac Catalyst" title="Mac Catalyst">
    <img src="extras/images/platforms/web.svg" width="88" height="88" alt="Web" title="Web">
    <img src="extras/images/platforms/nodejs.svg" width="88" height="88" alt="Node.js" title="Node.js">
    <img src="extras/images/languages/flutter.svg" width="88" height="88" alt="Flutter" title="Flutter">
    <img src="extras/images/languages/webassembly.svg" width="88" height="88" alt="WebAssembly" title="WebAssembly">
</p>

Choose the languages and targets for your project and compile the generated code with the appropriate toolchains. See the [target matrix](PROJECT.md#2-supported-languages-and-platforms) for runtime and build coverage.

## Documentation

- [Project specification](PROJECT.md) — architecture, types, diagrams, examples and roadmap.
- [Engineering guidelines](AGENTS.md) — development and contribution rules.

## Contributing

Report bugs or suggest improvements through [GitHub Issues](https://github.com/polyglue/polyglue/issues). Read [AGENTS.md](AGENTS.md) before contributing.

## Support

Support the ongoing development of this project through [GitHub Sponsors](https://github.com/sponsors/paulocoutinhox) or [Ko-fi](https://ko-fi.com/paulocoutinho).

## License

This project is licensed under the [MIT License](LICENSE).

Made with ❤️ by [Paulo Coutinho](https://github.com/paulocoutinhox).
