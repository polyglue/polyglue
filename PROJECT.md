# PolyGlue — project specification

Status: implementation pending. This document defines the intended 1.0 scope, not verified capabilities. All code, documentation, and tests are authored independently. No compatibility with other IDLs, generators, runtimes or wire formats is required; no Protocol Buffers.

## 1. Purpose and principles

PolyGlue is a Python interface compiler and template-based code generator for strongly typed, bidirectional, in-process native interoperability. Generate idiomatic models, contracts, proxies, adapters, factories and build integration from one modular IDL. Any supported runtime may implement or consume an interface when both runtimes can coexist. The generator is the product; the native runtime is a small supporting component, not a network RPC framework. No mandatory serialization, reflection-based dispatch, Python runtime in non-Python applications, global service registry, or JVM for generation. Prefer direct native calls and typed C ABI function tables over dynamic string dispatch.

Use original implementations, review licenses of any dependencies, preserve legally required notices; no copying reference implementations. Favor simple, maintainable code over abstractions without demonstrated use. Do not advertise untested targets. All examples and documentation in English.

## 2. Repository and tooling

- Python 3.12+; uv, pyproject.toml, uv.lock, src/polyglue, Lark grammar, Jinja2 templates with StrictUndefined, YAML safe loading, typed dataclasses and explicit configuration validation. Prefer argparse and standard library over unnecessary CLI/config frameworks. pytest, Hypothesis and Ruff for development. C++20 runtime, portable C ABI and CMake. No compulsory external formatter, Bazel, Scala or Java for generator execution.
- src/polyglue/{parser,semantic,ir,config,backends,templates,cli}; support/{core,c,cpp,jni,java,kotlin,objc,swift,python,dart,flutter,dotnet,wasm}; tests/{compiler,conformance,interop,memory,concurrency,fuzz,benchmarks}; examples/{idl,c,cpp,java,kotlin,objc,swift,python,dart,flutter,csharp,javascript,typescript}; docs; scripts; cmake; .github/workflows; extras/images/logo.svg; README.md, AGENTS.md, PROJECT.md, Makefile, LICENSE (license selection requires owner confirmation).
- Distribute wheel and sdist with grammar, templates and runtime sources; test installed wheel in a clean environment. Support uv run polyglue, uv tool install --editable ., pip install ., pinned uvx polyglue after publication, Python API, optional standalone executable after packaging validation. Do not publish to PyPI until release gates and owner authorization. Runtime version and ABI version are explicit.
- CLI: generate, validate, config show, list targets, --version, --config, --module, --target; nonzero failure exit; diagnostics with source spans and no output on validation failure. Offline generation. No automatic deletion of user-authored files.

## 3. IDL and semantics

Own grammar; UTF-8, comments and documentation, module declarations, multiple files per module, explicit imports, grouped imports and aliases; wildcard imports only if unambiguous. Public/private declarations, constants, typed defaults, records (value semantics), enums (explicit stable numeric values), flags, tagged variants, interfaces (identity/reference semantics), interface inheritance, typed callbacks, factories/static methods with explicitly defined implementation binding. User-defined generic records and interfaces only for supported concrete instantiations; generate concrete ABI specializations. Reject illegal value recursion, inheritance cycles, ambiguous imports, unsupported target features and duplicate symbols. Reference recursion may be legal. Resolve all symbols before rendering.

Types: void (returns only), bool, int8/16/32/64, uint8/16/32/64, float32/64, Unicode string, bytes (copy), list<T>, set<T>, map<K,V>, array<T> (optimized contiguous primitive arrays where possible), optional<T>, enum, flags, records, variants, interface references, Result<T,E>, DataView, MutableDataView, DataRef, callbacks, async methods, Stream<T>, CancellationToken, WeakRef<T>, timestamp (UTC, specified unit), duration (specified unit), uuid (16 bytes). External types via validated per-target adapter declarations; no Protobuf. No built-in Provider type: ordinary interfaces/callbacks express factories. Future is runtime machinery, not a second mandatory IDL spelling; async method syntax is canonical. Define equality/hash, stable ordering where promised, map key constraints, enum unknown-value policy, float NaN/Inf/-0, UTF-8 validation, null versus empty, integer range checks, JS BigInt for exact 64-bit values, and nested collection limits. No silent truncation or unsupported type substitution. Result models business failure; transport/runtime failures use a separate stable error status. No exceptions unwind across ABI.

Illustrative syntax (freeze grammar with tests before expanding):

```text
module domain;
record User {
    id: int64;
    name: string;
}
```

```text
module repository;
import domain.User;
interface UserRepository {
    async findById(id: int64): optional<User>;
    async findAll(): list<User>;
    async count(): int64;
    async exists(id: int64): bool;
}
```

## 4. Module-first configuration

Each module owns its YAML file, logical globally unique module identity/version, IDL roots, dependency declarations and individual target settings. Project file lists modules and supplies defaults. Precedence: built-in defaults < project defaults < module defaults < module target < declaration annotations (only where valid). Relative paths resolve against declaring config file. Validate schema and unknown keys. Explicit source vs prebuilt dependencies; prebuilt manifests contain canonical symbol identities, contract and ABI fingerprints, runtime version, generated names, public import/include references and target layout. Resolve transitively; detect incompatible duplicates, cycles and missing artifacts. No duplicate code for shared domain types.

```yaml
module:
  name: repository
  version: 1.0.0
sources: [idl/**/*.idl]
dependencies:
  domain:
    path: ../domain/module.yaml
    mode: source
targets:
  cpp:
    output: ../../native/repository
    namespace: app::repository
    include_prefix: app/repository
  kotlin:
    output: ../../android/generated/repository
    package: com.app.repository
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
```

All targets support relevant file paths, public/private header and source directories, namespace/package/module/assembly, prefixes/suffixes per category, casing, acronym policy, file extensions, imports, template overrides, formatting, file header/license, target availability and sources vs package output. Configure independent module prefixes (e.g. DOM vs REP). Do not assume Swift directory equals module or Java and Kotlin can emit duplicate JVM classes. Source/package modes integrate with CMake, Gradle, SwiftPM/module maps, Python packages, Dart pubspec/Flutter plugin, .NET csproj and JS package exports as applicable.

## 5. Compiler and backend pipeline

Discover sources → parse AST → build symbol table → semantic validation → canonical IR → plan all target names/files → resolve dependencies/imports → build language-specific render models → render Jinja2 → validate output plan → write atomically and emit manifest. Templates render only; type mapping, names and imports are Python logic. Backends expose capability declarations and independent naming, type mapping, layout, import, annotation and marshalling policies. Plugin entry points optional and explicit trusted opt-in; do not execute untrusted templates/plugins implicitly. Deterministic ordering, UTF-8/LF, no timestamps by default, stable source-relative paths. Avoid rewriting identical files. Detect case-insensitive filesystem collisions, reserved filenames, traversal/symlink escapes, conflicting outputs and keywords after case conversion. Only delete stale files known to the manifest and explicitly authorized. Golden and compilation tests exercise custom output layouts.

Naming: PascalCase, camelCase, snake_case, SCREAMING_SNAKE_CASE, kebab-case for filenames, lowercase and custom prefix/suffix. Preserve or normalize acronyms with explicit rules. Per-category types, records, interfaces, enums, enum members, methods, async methods, fields, parameters, constants, files, modules, proxies and internal symbols. Reject collisions instead of silently mangling public contracts. Generate idiomatic documentation and imports/includes/forward declarations; optional external formatters only.

Annotations: typed schema and placement validation for module, type, method, field, parameter, callback and enum member. Universal annotations (deprecated, readonly, thread/executor, availability, ownership) and backend-specific names, selectors and attributes. Automatically derive nullability, ownership and safe names where possible. Apple: @objc, @nonobjc, NS_SWIFT_NAME, NS_SWIFT_ASYNC_NAME, nullability, NS_ENUM/NS_OPTIONS, ARC, availability including visionOS, MainActor and Sendable only when valid. JVM: JvmName/JvmStatic and nullability. C/C++: visibility, calling conventions, nodiscard, noexcept only when proven. C#: marshaling/layout; Dart: FFI annotations; Python and TS typing. Unknown/invalid annotations fail; irrelevant known target annotations do not leak into other targets. Test actual compiler import behavior, not just string output.

## 6. Native ABI and memory

Document versioned C ABI before generating bridges. Fixed-width types, explicit alignment and layout, size/version headers for function tables, opaque handles with generation counters, stable deterministic type IDs distinct from ABI fingerprints. Verify ABI and target architecture before invocation; no C++ STL or managed pointers across C ABI. Allocator/deallocator pairing, explicit ownership on every argument and return, consistent calling conventions, visibility, error codes and diagnostics. Avoid raw pointer dereference from untrusted handles. Check overflow in lengths, offset arithmetic and allocations. No exception escapes ABI. One shared runtime per execution context; integration tests detect duplicate instances.

Interfaces carry a typed function table, opaque context and lifetime operations. Provider adapters hold runtime-specific strong references (JNI global references, ARC, Python references, GC handles, Dart isolate-owned handles, JS roots). Proxies retain and release correctly; preserve identity where documented; explicit close/dispose plus safe finalizer fallback. No finalizer-only correctness. Handle stale/foreign handles, refcount overflow, reentrant destruction, cycles and weak references; never call foreign code or destroy foreign objects under registry locks. Runtime teardown must drain/cancel calls and release references before unloading or invalidate safely if runtime is already gone.

bytes: independent copy. DataView: immutable borrowed memory restricted to synchronous scoped access; reject storing/returning/async capture when unsafe; managed APIs use scoped wrappers and checked validity rather than exposing escapable raw views by default. MutableDataView: exclusive scoped write, no concurrent readers/writers; enforce borrow rules or reject. DataRef: shared owned memory, slice with retained owner, release once on required executor, explicit read/write policy; immutable default. No implicit copy for zero-copy contracts: reject unsupported source memory or expose explicit copy conversion. WASM memory growth can invalidate views; pin/lease or reacquire checked views, never claim arbitrary JS heap zero-copy. Camera/GPU buffers need explicit mapping and platform adapters. Bounds, alignment, empty buffers, aliases, concurrent release and overflow tested. Instrument allocated/freed bytes, copies, live handles and operations; distinguish library instrumentation from runtime allocations.

## 7. Async, callbacks and streams

Canonical async syntax generates C completion callback, C++ awaitable, Java CompletableFuture, Kotlin suspend, Objective-C completion block, Swift async throws, Python awaitable, Dart Future, C# Task, JS/TS Promise. Do not block event loops or create threads per call. Use native schedulers/executors; capture originating context for completion. States pending/running/completed/failed/cancelled with atomic exactly-once terminal transition; safe inline completion, duplicate/late completion, cancellation races, timeout, shutdown, reentrant callbacks and exceptions. Cancellation cooperative, with explicit completion policy and release of pending references. No lock held across user code. Sync calls only when target permits correct thread access; cross-isolate synchronous Dart return is not generally possible; reject unsupported paths or require async. JNI attach/detach and exception checks, Swift actor isolation, Python GIL/thread state/event loop, .NET delegates/GC lifetime, Dart NativeCallable listener/isolate teardown, JS event loop/WASM memory constraints. Callbacks have typed signatures and explicit lifetime (scoped, retained, one-shot); async callbacks where cross-thread return needed. Streams specify subscription, bounded queue, backpressure/drop policy, ordering, terminal event, cancellation and retained buffers; test slow consumer and unsubscribe races.

## 8. Optional service discovery

All interfaces can be passed directly, returned by factories or injected without registry. Registry is optional, scoped by explicit runtime context; global convenience shares that same context, not a separate singleton per language. Generated type descriptors carry logical identity and ABI fingerprint; never infer from language class names. Registration stores typed provider table and retained context; returns unique token. Lookup validates contract, retains a snapshot, constructs generated proxy. get returns fixed instance; dynamic proxy resolves on each call; distinguish missing service from failure. Optional parent fallback, explicit priority/replacement policy and removal by token; deterministic ties, no implicit retry on provider error. Default behavior should be explicit replacement or error, not silent override; scoped override stack may be enabled. In-flight call pins provider until terminal state; unregister affects future lookups, runtime detach cancels/drains safely. Existing streams pin subscription provider. No locks during execution or foreign retain/release; design snapshot ownership to enforce this. Test concurrent registration, removal, lookup, reentrancy, destruction, ABA, runtime restart, isolation and ABI mismatch. No special Provider<T> built-in. Freeze API only after C/C++ and managed proof of concept.

## 9. Targets and platform contract

Required languages: C, C++, Java, Kotlin, Objective-C, Swift, Python, Dart, C#, JavaScript, TypeScript; Flutter integration (not a separate language). Required platform coverage: Windows, Linux, macOS, Android, Android XR, iOS/iPadOS, tvOS, watchOS, visionOS, Mac Catalyst, WebAssembly browser and Node where valid. Native visionOS independent of Flutter; Flutter native visionOS only if upstream supports it and test environment exists. Distinguish build-only, simulator execution and physical device execution. Do not assume all runtimes coexist or all sanitizers work on each target. Maintain machine-readable capability matrix and generate/test every claimed direction and type; unsupported combinations fail validation with reason. Mobile camera/device access may require physical device evidence.

## 10. Sample applications

Every language has a minimal runnable consumer and provider example, with UI where platform appropriate, CLI for C/C++/Python and other headless targets, and automated integration harness. Shared IDL modules domain, auth, network, media, repository; generate from clean tree. No manual bridge bypass, fake transport, or same-language-only test presented as interoperability.

- HTTP: actual request to https://httpbin.org/get or /post, show status, headers and response, verify typed response, errors, cancellation and timeout. Deterministic CI uses local HTTP fixture implementing equivalent contract; separate live smoke job with explicit network failure reporting, not a substitute for deterministic tests. Provider in another runtime; use platform HTTP API or small dependency justified by target. No external dependency in core runtime.
- Camera: acquire real frame on supported devices, transfer pixel buffer through generated DataRef, convert to grayscale in a different language, display result. Deterministic fixture in CI (known pixels, padded stride, odd dimensions, empty/invalid inputs) verifies exact grayscale algorithm and copy counts. Document pixel format, planes, stride, orientation, alpha preservation and overflow. No camera claim from fixture alone; emulator/device permissions and physical camera smoke when feasible. DataView sync processing tests and DataRef async tests.
- Login: simple form or CLI, fake credentials only, auth implementation in another runtime validates input and returns populated fake User (id/name/email/login flag); typed errors for invalid credentials; never log password. Repository returns list<User>, optional<User>, integer, bool and void asynchronously across module boundaries.
- Each target exercises both directions, interface passing, callback progress, completion, cancellation, service replacement and shutdown. Flutter Android → Kotlin, Apple → Swift, native → Dart async callback; browser → WASM and reverse. Publish build/run instructions and actual test evidence per target.

## 11. Verification and CI

GitHub Actions separate required jobs/workflows for generator, C, C++, Java, Kotlin desktop, Kotlin Android, Objective-C, Swift, Python bindings, Dart, Flutter Android/iOS/desktop/web, C#, JavaScript, TypeScript, WASM, Apple platform matrix (including visionOS, watchOS, tvOS, Catalyst), Android XR where runner supports it, conformance, sanitizers, fuzz, docs and packaging. Matrix OS/architectures/compiler versions according to supported claims. Pin toolchains/actions to reviewed versions; least permissions, timeouts, deterministic dependencies, cache only safe inputs, no secret use for untrusted PRs. Compile freshly generated code; run actual consumer/provider tests and examples; fail on missing test executables, skipped mandatory cases, sanitizer findings or missing artifacts. No empty jobs or allow-failure for required checks. Publish logs, JUnit, coverage, sanitizer reports and capability results tied to commit SHA. No fabricated badges. PR fast suite, nightly extended stress/fuzz and platform matrix; release requires all mandatory jobs on same revision. Observe workflow runs, inspect failed logs, correct root causes, rerun and record results. A runner unavailable is blocked, not passing.

Conformance: shared fixtures and case IDs for every type and nesting, both directions, sync/async, errors, callbacks, streams, ownership, external adapters, cross-module and prebuilt modules. Boundary values, Unicode/invalid UTF-8, null/empty, signedness, BigInt, NaN/Inf, list/map/set duplicates, variants unknown tags, generic specialization, invalid layouts and ABI. Cross-language pair matrix for feasible colocated runtimes; explain unsupported pairs. Validate generated files and actual ABI layout on 32/64-bit where supported. Test deterministic generation, naming, import collisions, annotations, path safety, malformed IDL/YAML, missing dependencies, template failures and packaging.

Memory and concurrency: ASan (use-after-free/return/scope, double free, overflow), LSan/Valgrind, UBSan, MSan where instrumented dependencies permit, TSan separate builds, platform equivalents, JNI CheckJNI, ARC and Swift strict concurrency, Python debug/refcount tests, .NET GC stress, Dart isolate restart, JS memory growth. Test stale handles, foreign handles, double release, allocator mismatch, reference cycles, concurrent buffer retain/release, mutation aliasing, zero-copy pointer identity and instrumented copy counts, thread affinity, callbacks after disposal, cancellation vs completion, deadlock/reentrant calls, lock inversion, shutdown while active, runtime reload, out-of-memory/error paths, repeated init/teardown. Use barriers and deterministic race orchestration, watchdog timeouts, stress seeds, subprocess tests for fatal failures; demonstrate sanitizer jobs detect deliberate faults in isolated harnesses. Fuzz grammar, semantic resolver, ABI entrypoints and converters with bounded inputs. Benchmarks track latency, throughput, allocations and bytes copied; baseline before setting thresholds. Coverage reports and regression tests for each discovered defect. Coverage percentage is not proof of no bugs.

## 12. Documentation and repository practices

README: centered SVG logo, accurate workflow badges only once workflows exist, concise project/usage/examples/platform table/docs links/status. AGENTS.md: enforce this specification, English source, minimal dependencies, no placeholder success, test before commit, review diffs, update capability matrix and docs, report blockers honestly. Docs: getting started, IDL grammar/reference, types, ownership and zero-copy, async/threading, ABI, config/modules/naming/annotations, registry, per-language integration, platform requirements, samples, CI/test matrix, troubleshooting, contribution and release. SVG original clean modern vector mark, no external assets. Keep generated files out of repo unless fixtures or explicitly documented. Do not overwrite unrelated changes. No release or claim of 100% safety merely because tests passed.

## 13. Implementation sequence and gates

1. Commit this plan first; review scope and remove redundant dependencies/features. Define grammar and ABI contracts, capabilities and test IDs.
2. Bootstrap Python package, parser, semantic IR, module/config resolution, backend framework, deterministic output and tests; install wheel locally and execute CLI.
3. Implement C ABI/C++ runtime and generated C/C++ bindings; ownership, errors, DataView/DataRef, async/callbacks, conformance and sanitizer gates. Design registry only after typed references work.
4. Add JNI Java/Kotlin and Apple Objective-C/Swift adapters; verify Android and Apple platform builds/runs, cross-runtime examples.
5. Add Python, C#, Dart/Flutter and WASM JS/TS; test idiomatic async, callbacks and memory lifetime, complete platform matrix.
6. Finish advanced types, streams, external adapters, annotations, module packaging and registry; all claimed type/target directions tested. No optional feature becomes public without evidence.
7. Complete example apps, docs, SVG, README, packaging and workflow coverage. Deep review every backend, generated API, ABI, ownership and concurrency; simplify redundant code. Fix all failures, rerun required CI, record commit-specific evidence. Release candidate only when capability matrix and acceptance checklist are green; owner approves publishing.

## 14. Acceptance checklist

- [ ] Complete generator and all required backends with no placeholder implementation.
- [ ] All supported types and nested combinations tested in each supported direction.
- [ ] Real cross-language consumers/providers and sample applications pass.
- [ ] Memory, copy, race, deadlock, lifetime, cancellation, teardown and fuzz suites pass.
- [ ] Required platform jobs pass with honest distinction between build/run/device coverage.
- [ ] Docs, AGENTS.md, README, SVG and installation artifacts validated.
- [ ] Independent deep review and regression fixes complete.
- [ ] Latest required CI runs green on exact release commit; no mandatory skips.
- [ ] Owner authorization before publication.

No finite test suite can establish absolute absence of defects. Completion means all explicit acceptance gates have reproducible evidence, not a promise of bug-free software.
