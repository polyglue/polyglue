# PolyGlue

## Purpose and capabilities

PolyGlue is a planned Python interface compiler and source generator for typed, bidirectional interoperability between native and managed runtimes. The current development version is 0.0.1. The repository currently contains the specification, project documentation and original branding, not a working compiler or native runtime.

Read [PROJECT.md](PROJECT.md) before implementation. It defines product scope, all target languages and platforms, IDL semantics, module-first configuration, template overrides, ABI, native packaging, examples, test matrix and acceptance gates. Do not claim a planned capability has been implemented.

## Owner standards

Always write the product name as PolyGlue, with an uppercase P and G, in documentation, headings, branding, illustrations and user-facing text. Keep lowercase polyglue for technical identifiers such as the Python package, CLI command and repository path. Preserve language-specific identifier conventions.

Follow the owner's [skills collection](https://github.com/paulocoutinhox/skills), initially reviewed at [fcca67d](https://github.com/paulocoutinhox/skills/tree/fcca67d378ee025d646aa70c2b6f514c151fa5c4). Read the current applicable skill and its relevant references before modifying the corresponding area. Do not install or update the collection automatically.

- Code Developer: general engineering and the profiles for every changed language.
- Code Review: impact tracing, evidence-based findings and verification.
- Git: task-aware naming, reviewed snapshots, human author and explicit delivery authorization.
- Editor Config and Git Ignore: consistent formatting and privacy boundaries.
- Security Audit: threat model, authorization, negative tests, evidence and remediation.
- PyPI Library: package architecture, installed consumer checks and trusted publication.
- NPM Library, Android App Testing and Apple App Testing: use for the relevant targets and artifacts.

For C, Objective-C, Java, Dart, C# and other languages without a dedicated profile, follow the other-languages research procedure and the actual compiler/SDK contract. Owner conventions are not universal language requirements. Do not force invalid syntax to imitate another language. The project-specific release and Git restrictions in this file override optional general workflows.

## Architecture and repository map

Current files:

- PROJECT.md: planned architecture, specification and release acceptance.
- README.md: concise public product introduction.
- AGENTS.md: working rules.
- extras/images/logo.svg: original vector logo used by the README.

Planned implementation map (create directories when they contain actual functionality):

- src/polyglue/: Python CLI, parser, semantic resolver, IR, config, diagnostics, backends, templates and build orchestration.
- support/: C++20 runtime, C11 ABI surface and language-specific support libraries.
- cmake/: build options, dependency targets, sanitizer configuration, install/export and toolchain integration.
- examples/: shared IDL modules and real consumer/provider apps for each language.
- tests/: compiler, generated-code, native, cross-language, memory, concurrency, installed-consumer and fuzz tests.
- docs/: current user documentation, not implementation plans disguised as supported features.
- .github/workflows/: independent target CI and artifact checks.
- build/ and dist/: ignored generated build and package outputs.

The compiler resolves logical symbols, module dependencies, type/ABI identities, naming, annotations, physical file plans and imports before rendering Jinja2. Templates render validated models and may be overridden per module and target. Preserve every configured lookup layer, including module target defaults. Deterministic generated files must not contain wall-clock timestamps or machine-specific absolute source paths. Concrete generic specializations must have one public artifact owner in the module dependency closure. No untrusted IDL can execute code or select arbitrary output paths.

The runtime implements shared ABI mechanics, ownership, references, buffers, async/callbacks, cancellation and optional registry. Generated adapters connect typed interfaces in both directions. Keep business logic in the consumer/provider implementations. Use one compatible runtime per execution context. Attach adapters only to a validated, initialized context. Never exchange handles across independent contexts. A shared explicit cancellation token may notify several operations, while cancellation of one operation does not automatically signal the shared token. Register cancellation observers without a lost-request race and remove them before freeing their contexts. Python is the build-time generator and orchestrator, not a required runtime in non-Python applications. Do not overwrite unowned outputs or leave a stale successful manifest after an incomplete generation. Do not introduce mandatory JSON serialization, Protocol Buffers, network RPC or compatibility layers with other tools.

The type system supports built-in exact date, timestamp, duration and UUID values, with checked native conversions. Keep the built-in catalog limited to the specified common types and use external types or ordinary IDL for domain-specific values. External types use module-owned versioned descriptors, existing canonical ABI representations and explicit host-language adapters. Users must be able to add a type without editing or rebuilding the generator. Never silently truncate temporal values, invent a target mapping, evaluate descriptor code or use raw foreign pointers as integers. Follow the external type schema and tests in PROJECT.md.

Modules are the unit of generation. Products aggregate modules for binary distribution without changing module identity. Use CMake for native code and the proper ecosystem tooling for Gradle, Apple, SwiftPM, Python, Dart/Flutter, .NET and JS/TS/WASM. Isolate final artifacts by SDK version, build number, platform, architecture or slice set, format, configuration and sanitizer. Keep build plans and subprocess execution in Python and reuse the same CLI locally and in CI. No duplicate build systems or speculative helper frameworks.

## Type and platform reference

The following tables mirror the planned contract in PROJECT.md section 5.4. Keep the two copies identical when modifying a mapping. These are required target mappings, not evidence of implemented support. A backend must not invent a different representation merely to pass its tests.

### Canonical type mapping

These tables are the proposed default public APIs, not native struct layouts. C and WASM describe the boundary representation. Generated wrappers are small and typed. Their final names follow module naming rules. Flutter uses the Dart native or Dart Web column according to its platform. Java and Kotlin share one model only when explicitly configured. Swift may import Objective-C models. Shared model ownership does not change the canonical type.

All numeric conversions check range and type. All collection mappings obey the key and optional rules below. A wrapper is required when a native representation cannot preserve the full value or lifetime contract. No silent conversion or fallback. A pointer, offset or handle is valid only inside its owning runtime or WASM instance. `async` is a declaration modifier rather than a value type. Async callbacks use the same completion contract as async methods. `void` is return-only, including the success case of Result. The WASM column describes a conceptual canonical lowering, not a finalized ABI signature.

#### Type meaning and native boundary

| IDL | Meaning | C | WebAssembly |
| --- | --- | --- | --- |
| `bool` | True or false | uint8_t (0/1) | i32 (0/1) |
| `int8` | Signed 8-bit integer | int8_t | i32, checked |
| `int16` | Signed 16-bit integer | int16_t | i32, checked |
| `int32` | Signed 32-bit integer | int32_t | i32 |
| `int64` | Signed 64-bit integer | int64_t | i64 |
| `uint8` | Unsigned 8-bit integer | uint8_t | i32, checked |
| `uint16` | Unsigned 16-bit integer | uint16_t | i32, checked |
| `uint32` | Unsigned 32-bit integer | uint32_t | i32 bit pattern |
| `uint64` | Unsigned 64-bit integer | uint64_t | i64 bit pattern |
| `float32` | 32-bit floating-point value | float | f32 |
| `float64` | 64-bit floating-point value | double | f64 |
| `string` | Unicode text | UTF-8 descriptor | UTF-8 in linear memory |
| `bytes` | Independent binary value | Owned byte descriptor | Owned byte buffer |
| `void` | Successful return with no payload | Status, no payload | Status, no payload |
| `record` | Named group of values | Generated value/handle | Canonical fields |
| `enum` | One declared integer value | int32_t + constants | i32, checked |
| `flags` | Combined named bits | uint32_t + constants | i32 bit mask |
| `variant` | One of several tagged alternatives | Tagged value + destroy | Tag + active payload |
| `list<T>` | Ordered sequence | Typed descriptor/handle | Length + elements |
| `set<T>` | Unique values | Typed descriptor/handle | Canonical unique elements |
| `map<K,V>` | Keys mapped to values | Typed descriptor/handle | Canonical key/value pairs |
| `array<T>` | Sequence with contiguous primitive optimization | Typed array descriptor | Length + typed or element buffer |
| `optional<T>` | Absent or present value | Presence tag + payload | Presence tag + payload |
| `Result<T,E>` | Business success or business error | Tagged result + destroy | Tag + active payload |
| `interface` | Reference to an implementation | Typed opaque handle | Context-local typed handle |
| `callback` | Callable passed to another implementation | Function table + context | Typed callback handle |
| `async method / callback` | Operation with asynchronous completion | Completion + operation handle | Operation handle + completion |
| `Stream<T>` | Sequence of asynchronous events | Subscription handle | Subscription handle |
| `WeakRef<T>` | Reference that does not retain the object | Weak handle | Context-local weak handle |
| `CancellationToken` | Cooperative stop signal | Token handle | Token handle |
| `date` | Calendar date, without a time | int64_t epoch days | i64 epoch days |
| `timestamp` | UTC instant, exact microseconds | int64_t UTC microseconds | i64 UTC microseconds |
| `duration` | Signed elapsed nanoseconds | int64_t nanoseconds | i64 nanoseconds |
| `uuid` | 128-bit identifier | 16-byte value | 16 canonical bytes |
| `DataView` | Scoped read-only borrowed memory | Const pointer + length | Scoped offset + length |
| `MutableDataView` | Scoped exclusive writable memory | Writable pointer + length | Exclusive scoped offset + length |
| `DataRef` | Shared owning buffer reference | Owning handle | Context-local owner handle |
| `external` | User-defined host type with canonical mapping | Declared type / adapter | Declared canonical representation |

#### Native and JVM public APIs

| IDL | C++ | Java | Kotlin | Objective-C | Swift |
| --- | --- | --- | --- | --- | --- |
| `bool` | bool | boolean | Boolean | BOOL | Bool |
| `int8` | std::int8_t | byte | Byte | int8_t | Int8 |
| `int16` | std::int16_t | short | Short | int16_t | Int16 |
| `int32` | std::int32_t | int | Int | int32_t | Int32 |
| `int64` | std::int64_t | long | Long | int64_t | Int64 |
| `uint8` | std::uint8_t | short | UByte | uint8_t | UInt8 |
| `uint16` | std::uint16_t | int | UShort | uint16_t | UInt16 |
| `uint32` | std::uint32_t | long | UInt | uint32_t | UInt32 |
| `uint64` | std::uint64_t | BigInteger | ULong | uint64_t | UInt64 |
| `float32` | float | float | Float | float | Float |
| `float64` | double | double | Double | double | Double |
| `string` | std::string | String | String | NSString | String |
| `bytes` | `std::vector<uint8_t>` | byte[] | ByteArray | NSData | Data |
| `void` | void | void / Void | Unit | void | Void |
| `record` | struct | Immutable class | data class | NSObject model | struct or imported model |
| `enum` | enum class | Generated enum | enum class | NS_ENUM | enum |
| `flags` | Flags wrapper | Flags wrapper | Flags wrapper | NS_OPTIONS | OptionSet |
| `variant` | std::variant | Tagged class | Sealed class | Tagged object | Associated-value enum |
| `list<T>` | `std::vector<T>` | `List<T>` | `List<T>` | NSArray | [T] |
| `set<T>` | std::set / hash set | `Set<T>` | `Set<T>` | NSSet | `Set<T>` |
| `map<K,V>` | std::map / hash map | `Map<K,V>` | `Map<K,V>` | NSDictionary | `Dictionary<K,V>` |
| `array<T>` | std::vector / array wrapper | Primitive array / wrapper | Primitive array / wrapper | Typed buffer / wrapper | Typed buffer / wrapper |
| `optional<T>` | `std::optional<T>` | Nullable boxed T / wrapper | T? / wrapper | Nullable object / boxed optional | `Optional<T>` |
| `Result<T,E>` | PolyGlue Result | Generated Result | Sealed Result | Tagged result object | Result / tagged enum |
| `interface` | Owning interface reference | Interface + proxy | Interface + proxy | Protocol + proxy | Protocol + proxy |
| `callback` | Callable wrapper | Functional interface | Function / SAM | Block | Closure |
| `async method / callback` | Awaitable / future | CompletableFuture | suspend | Completion block | async throws |
| `Stream<T>` | Async stream | Publisher adapter | Flow | Subscription + block | AsyncSequence |
| `WeakRef<T>` | Weak interface reference | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper |
| `CancellationToken` | Token wrapper | Token wrapper | Token wrapper | Token wrapper | Token wrapper |
| `date` | std::chrono::year_month_day | LocalDate | LocalDate | Calendar date wrapper | Calendar date wrapper |
| `timestamp` | `sys_time<microseconds>` | Instant | Instant | Exact wrapper + NSDate conversion | Exact wrapper + Date conversion |
| `duration` | std::chrono::nanoseconds | Duration | java.time.Duration | Exact duration wrapper | Duration or exact wrapper |
| `uuid` | UUID value wrapper | UUID | UUID | NSUUID | UUID |
| `DataView` | Scoped read-only span | Checked read view | Checked read view | Checked read view | Scoped read-only access |
| `MutableDataView` | Scoped writable span | Checked write view | Checked write view | Checked write view | Scoped writable access |
| `DataRef` | RAII owner | Retained buffer owner | Retained buffer owner | Retained buffer owner | Retained buffer owner |
| `external` | Declared type / adapter | Declared type / adapter | Declared type / adapter | Declared type / adapter | Declared type / adapter |

#### Managed and web public APIs

| IDL | Python | Dart native | Dart Web | C# | JavaScript | TypeScript |
| --- | --- | --- | --- | --- | --- | --- |
| `bool` | bool | bool | bool | bool | boolean | boolean |
| `int8` | int | int | int | sbyte | number | number |
| `int16` | int | int | int | short | number | number |
| `int32` | int | int | int | int | number | number |
| `int64` | int | int | BigInt | long | bigint | bigint |
| `uint8` | int | int | int | byte | number | number |
| `uint16` | int | int | int | ushort | number | number |
| `uint32` | int | int | int | uint | number | number |
| `uint64` | int | BigInt | BigInt | ulong | bigint | bigint |
| `float32` | float | double | double | float | number | number |
| `float64` | float | double | double | double | number | number |
| `string` | str | String | String | string | string | string |
| `bytes` | bytes | Uint8List | Uint8List | byte[] | Uint8Array | Uint8Array |
| `void` | None | void | void | void | undefined | void |
| `record` | Frozen dataclass | Immutable class | Immutable class | record / class | Immutable object | Readonly model + runtime object |
| `enum` | Enum | enum | enum | enum | Frozen constants | Checked numeric type |
| `flags` | IntFlag / checked wrapper | Flags wrapper | Flags wrapper | Flags enum / wrapper | Checked mask | Checked mask |
| `variant` | Tagged dataclass union | Sealed class | Sealed class | Tagged record hierarchy | Tagged object | Discriminated union |
| `list<T>` | list[T] | `List<T>` | `List<T>` | `IReadOnlyList<T>` | Array | `ReadonlyArray<T>` |
| `set<T>` | set[T] | `Set<T>` | `Set<T>` | `IReadOnlySet<T>` | Set | `Set<T>` |
| `map<K,V>` | dict[K,V] | `Map<K,V>` | `Map<K,V>` | `IReadOnlyDictionary<K,V>` | Map | `Map<K,V>` |
| `array<T>` | Typed buffer / list | TypedData / wrapper | TypedData / wrapper | T[] / `Memory<T>` | TypedArray / Array | TypedArray / `ReadonlyArray<T>` |
| `optional<T>` | T or None / wrapper | T? / wrapper | T? / wrapper | T? / wrapper | T or null / wrapper | T or null / wrapper |
| `Result<T,E>` | Tagged result | Sealed Result | Sealed Result | Generated Result | Tagged object | Discriminated union |
| `interface` | Protocol/ABC + proxy | Interface + proxy | Interface + proxy | Interface + proxy | Provider object / proxy | Interface + runtime proxy |
| `callback` | Callable | Typed function | Typed function | Delegate | Function | Typed function |
| `async method / callback` | Awaitable / async def | Future | Future | Task | Promise | Promise |
| `Stream<T>` | AsyncIterator | Stream | Stream | `IAsyncEnumerable<T>` | AsyncIterable | `AsyncIterable<T>` |
| `WeakRef<T>` | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper | Weak handle wrapper |
| `CancellationToken` | Token wrapper | Token wrapper | Token wrapper | CancellationToken adapter | AbortSignal adapter | AbortSignal adapter |
| `date` | datetime.date | Calendar date wrapper | Calendar date wrapper | DateOnly | Calendar date wrapper | Calendar date wrapper |
| `timestamp` | Exact wrapper + aware datetime conversion | Exact wrapper + UTC DateTime conversion | Exact wrapper + UTC DateTime conversion | Exact wrapper + DateTimeOffset conversion | bigint + Date conversion | bigint + Date conversion |
| `duration` | Exact wrapper + timedelta conversion | Exact wrapper + Duration conversion | Exact wrapper + Duration conversion | Exact wrapper + TimeSpan conversion | bigint nanoseconds | bigint nanoseconds |
| `uuid` | uuid.UUID | UUID wrapper | UUID wrapper | Guid | Canonical UUID string | Canonical UUID string |
| `DataView` | Checked read view | Checked read view | Checked read view | Scoped read-only access | Checked linear-memory view | Checked linear-memory view |
| `MutableDataView` | Checked write view | Checked write view | Checked write view | Scoped writable access | Checked writable memory view | Checked writable memory view |
| `DataRef` | Retained buffer owner | FFI buffer owner | Web buffer owner | SafeHandle / owner | Linear-memory owner | Linear-memory owner |
| `external` | Declared type / adapter | Declared type / adapter | Declared type / adapter | Declared type / adapter | Declared type / adapter | Declared type / adapter |

Java unsigned values use checked wider types. Kotlin uses exact unsigned types with checked JNI bit conversions. Python integers and JavaScript Number inputs are checked, including rejection of Python bool as an integer. JavaScript and Dart Web must not convert exact 64-bit values through JavaScript Number. Use BigInt or an exact checked bit representation at the adapter boundary. A JS or WASM signed bit pattern is not the mathematical unsigned value until it has been decoded. Numeric arrays use exact contiguous representations only where available. Float32 rounding occurs at the boundary. Strings use validated UTF-8 with explicit lengths, including embedded NUL. Invalid UTF-8 or unpaired surrogates fail. C bool accepts only 0/1. Record and collection values do not share mutable object identity. Interface and DataRef references retain ownership explicitly.

Collection key types are limited to bool, integer, string, enum and UUID, plus external types proven to preserve one of those key representations. Reject duplicate canonical keys. There is no portable set/map iteration order. Key wrappers are needed when host equality differs from canonical equality, such as Swift canonical-equivalent Unicode strings. Objective-C dictionary keys must also support NSCopying. Generated key wrappers must be immutable, implement canonical equality and hashing, and copy without changing their value. Java/Kotlin and Objective-C shared models must preserve the same rules. JS UUID keys use canonical strings. Preserve float signed zero, infinity and NaN classification without promising NaN payload bits. UUID bytes use network order. No borrowed memory may escape a direct synchronous parameter. DataRef is read-only by default and retains its true owner. See sections 5.6, 5.8, 13 and 14 of PROJECT.md for detailed rules.

### Platform coverage

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
| Web (browser) | C/C++ via WASM, JS, TS, Dart/Flutter Web | Browser execution |
| Node.js | C/C++ via WASM, JS, TS | Node execution |

Flutter uses Dart bindings and platform integration, not a separate type system. WASM uses the canonical ABI lowering and generated web bindings. All platform entries remain planned until their required build and execution evidence exists.

### Required UTC and optional rules

Every instant crosses as signed UTC epoch microseconds, without reading the host default timezone. Convert timezone-aware inputs to UTC before crossing. Never assume a timezone for naive or ambiguous values. Return UTC-native instants when a native conversion is representable and reject precision/range loss. A calendar date crosses as Gregorian epoch days without time or timezone, and durations cross as signed nanoseconds. Apply these rules recursively in external adapters, collections, callbacks, async, streams and records. Use checked integer epoch conversion with a nonnegative fractional remainder for negative instants. Verify java.time API availability on the configured Android SDK floor or explicitly tested desugaring.

All types are non-null unless declared `optional<T>`. Every method argument is supplied explicitly. Only record construction may apply a declared default for an omitted field. A constructor-only omission sentinel is never transported. The decoder must not reapply defaults to a present record. An omitted optional without a default is absent. Explicit null means absent for an optional and an error for a required value, never a request to use a default. Preserve empty, false and zero values. Use a presence tag at the ABI for every optional layer. Do not read or release inactive payloads. Nested optional states must remain distinct even if a host's nullable type collapses them. Use typed wrappers for those cases and for nullable Objective-C collection elements. JS/TS use null for absence, reject explicit undefined for values and sparse array holes, and reserve undefined for a no-payload void return. A missing map key differs from a present key with an absent optional value. A failed invocation, business error and cancellation differ from successful absence. Void is return-only, except the no-payload success of Result<void,E>. Null is a literal allowed for optional values, not an independent type. Apply PROJECT.md section 5.8 and the shared conformance fixtures.

## README and documentation standards

Follow the owner's established public README style, as seen in the Haylen and XPLPC repositories. Keep the README in English with a centered original SVG logo, project name and short tagline. Present the final product design without temporary development labels or progress disclaimers. Keep actual implementation status and verification evidence in PROJECT.md and AGENTS.md. Use plain English and start with a direct definition of PolyGlue, what it generates, what problem it solves and one short example. Keep the Project section to at most three short paragraphs. Follow with brief features, logo-based language and integration tables, platform coverage, documentation, contributing, support, license and author credit. Do not tell a story or add tutorial code, detailed workflows or Mermaid to the README. Use a compact centered header with minimal whitespace while preserving the standard Markdown section headings and established README layout. Use recognizable local SVG logos and names in HTML tables, with up to three items per row, without fixed cell widths. Keep assets in extras/images/languages/ at 512 × 512 intrinsic dimensions and display them at 50 × 50 through HTML. Preserve upstream attribution and license notices, and include meaningful alt text. List platforms separately without a language-to-platform column. Link to the detailed matrix for runtime and build coverage. The consumer selects targets and compiles the generated code using the appropriate toolchains. Keep the owner-approved static overview at extras/images/how-it-works.svg, showing iOS (Swift) and Android (Kotlin) each calling shared C++ source compiled into its own app. Preserve its visual style, using platform colors and neutral shared-logic blocks. Keep progressive learning, examples and diagrams in PROJECT.md and docs/. Use the actual GitHub-rendered Markdown surface and meaningful alternative text. Do not turn the README into a second technical specification. Keep implementation details, configuration and full examples in PROJECT.md or docs/.

Use neutral language and platform headings to present the product scope. Track unimplemented and unverified capabilities in the technical documents. Never invent successful tests, published packages or releases. Keep the README language and platform lists aligned with PROJECT.md. Maintain the detailed compatibility matrix in PROJECT.md and AGENTS.md. Distinguish Flutter and WASM integration targets from programming languages. Add real CI badges only when the referenced workflows exist. Add installation instructions, runnable examples and release badges only when verified. Keep support links and author credit consistent with the owner's other repositories. PolyGlue is licensed under the MIT License. Link the root LICENSE file in the README and preserve applicable third-party license notices. Do not link to future files that do not exist.

Maintain the original clean vector logo in extras/images/logo.svg. Use the existing asset directly, without external fonts, images, scripts or unnecessary duplicates. Keep the README header readable on light and dark backgrounds. Keep AGENTS.md free of diagrams, including Mermaid and ASCII flowcharts. Keep the synchronized type and platform tables here. Maintain GitHub Mermaid diagrams in PROJECT.md beside each major feature contract, including value conversions, direct and registry calls, callbacks, async, cancellation, streams, memory, errors, compiler and build/distribution pipelines. Keep technical diagrams and Mermaid out of README.md. Use only the approved static explanatory image in the README. Use sequence diagrams where they make independent call directions easier to understand. Show both directions and meaningful failure or cleanup paths. Avoid duplicating diagrams for equivalent types. Update the diagrams with the corresponding contracts and keep prose understandable without rendering. Do not introduce a documentation generator or diagram dependency solely for these assets. Check actual links, images, anchors and rendered Markdown where available. Follow the Markdown profile in the owner's skills.

## Development commands

No runnable compiler, package metadata, build system or CI exists yet. Do not describe a planned command as working.

Implement and document the real commands as features become available. Planned interfaces include uv sync --locked, uv run --locked ruff check ., uv run --locked ruff format --check ., uv run --locked pytest, uv run --locked polyglue validate, generate, doctor, build, test, package, deploy, run, clean and templates list/export/check. Makefile targets must be thin calls into existing tools, not a duplicate implementation. Update this section with verified setup, lint, test and packaging commands as each phase lands.

Use uv for Python dependencies and explicitly requested standalone Python tooling. Use the language's proper SDK and toolchain for native and application code. Do not create unrelated wrappers or background refresh automation.

## Code standards

Implement the final requested contract, not a compatibility layer. Remove old APIs, config formats, aliases, migration-only branches, legacy checks, dead code and unused dependencies together with their callers. Do not use hacks, hidden fallbacks, silent retries, fake defaults, swallowed errors or substitute implementations to hide a failure. ABI/version checks reject incompatible artifacts, not dispatch to older implementations. Explicit template inheritance for unmodified files, deliberately selected registry overrides and safe finalization are required semantics, not fallbacks after errors. Keep the simplest maintainable solution. Do not add features, abstractions, tests, automation or scaffolding merely to show work. Fix real substantiated review findings and do not invent speculative problems.

Write code, identifiers, comments, technical documentation and commit messages in clear English. Prefer meaningful names, concrete responsibilities, early returns, named intermediate results and visible error paths. Separate validation, computation, mutation, I/O and return with blank lines. Keep independent if statements, loops and other logical statements visually separate. Do not crowd code into adjacent blocks. Avoid long chains, deep nesting, repeated business rules, hidden side effects, needless else after return and generic utility buckets. Extract helpers only for a meaningful responsibility or real reuse. Do not add interfaces, factories or abstractions without an actual boundary.

Keep every ordinary function call, full signature and string literal on one source line. Name complex arguments first. Structural blocks, collection/object literals and trailing closures keep normal indentation. Fix formatter configuration rather than accepting wrapped calls. Join already-wrapped calls and verify formatting twice is idempotent.

Give each class, enum, component, screen and view its own appropriately named file, including supporting types, except for required language/tool constructs. Follow the mandatory filename policy below. Do not hide multiple types in one file to evade the rule.

Comments are rare, in English, explain necessary intent and use complete sentences with initial capital and final period. Keep each comment sentence on one line. No decorative section comments, redundant narration or prose semicolons. Preserve required directives and license notices. Use no legacy aliases, compatibility shims or old-format detection. Do not add comments narrating the user's requested changes. Keep natural-language sentences free of semicolons. Preserve required programming-language syntax.

### Filenames and paths

Hyphens (dash, kebab-case) are mandatory for repository-owned multiword filenames and directories wherever the language and toolchain allow them. Do not choose underscores merely for convenience or personal preference. Examples: user-repository.idl, user-repository.hpp, user-repository.cpp, file-header.j2, dependency-check.cmake, build-android.py (standalone script), kotlin-android.yml and memory-safety.md. Apply the rule to source files, templates, tests, documentation, scripts, assets, generated files and workflow filenames.

Exceptions are narrow: Python importable module/package names and required files such as __init__.py, language/tool-required discovery or naming conventions (including enforced Dart lowercase_with_underscores lint and Java public-type filenames), symbol-named files required by the adopted language profile, and exact standard filenames such as CMakeLists.txt, Package.swift, pyproject.toml and AGENTS.md. Record the reason when a new exception is needed. A standalone Python script that is not imported as an ordinary Python module uses hyphens. Do not change required identifiers, ABI symbols, package names, configuration keys or environment variables just to remove underscores from filenames. Consumer-defined naming overrides remain supported. The repository and official default generated output obey this policy.

### Modern Python and dependency freshness

Use the newest stable CPython release and latest stable uv for active development, tooling and CI. Use pyproject.toml with explicit build-system and project metadata, src layout, uv.lock, dependency groups, uv sync --locked, uv run --locked, uv add, uv lock --upgrade and uv build --no-sources as applicable. Use the latest stable Ruff, pytest, Hypothesis, Lark, Jinja2 and other justified dependencies. Prefer modern supported typing, standard-library APIs and native async patterns. Do not add legacy Python compatibility or duplicate pip/requirements.txt/Poetry/Pipenv/virtualenv workflows. uv manages the development environment. Pip installation is a supported consumer option, not the development workflow. Keep distribution compatibility ranges distinct from exact development lock resolution.

Always use the newest stable released versions of direct runtime, development, build, test and packaging dependencies, GitHub Actions (including reusable workflows and third-party actions), SDKs and toolchains at the time of implementation or maintenance. Verify the actual latest stable release from the official upstream release, registry or tool documentation rather than relying on memory, stale examples, or an assumed latest major. Do not choose beta, RC, nightly or moving main/master dependencies unless the owner explicitly approves them. Do not add unnecessary dependencies simply because newer tools exist.

Resolve and test upgrades together across all affected consumers and targets. Check the latest mutually compatible versions of coupled ecosystems such as Kotlin/AGP/Gradle/JDK, Xcode/Swift and Dart/Flutter. An older direct version is an explicit blocker or exception, never a silent choice: document the newest version, the concrete incompatibility, tested alternative and required owner approval. Transitive versions must respect real upstream constraints. Report incompatible or vulnerable resolutions and fix them where possible. A dependency update does not authorize a PolyGlue version bump, tag, release or publication.

Keep lockfiles committed and update them deliberately using ecosystem-native tools. Pin the latest verified stable action release to its immutable commit SHA with the release tag in a comment. Pin native source revisions and archive hashes. Use latest stable runner images where appropriate and record the exact SDK/compiler versions actually installed. Use fixed resolved versions in builds and release evidence. No unreviewed floating downloads or lockfile upgrades inside ordinary CI. Review dependency/action currency whenever changing implementation, CI or packaging and again before an authorized release. Run the applicable complete build/test matrix after upgrades. No automatic dependency-update PRs, scheduled mutation, or auto-publication without separate authorization.

### Language conventions

- Python: src layout, pyproject.toml, uv.lock, Ruff, typed interfaces, focused classes, dataclasses where appropriate, pathlib, context managers, explicit encoding and narrow exceptions. All __init__.py files completely empty. Import from defining modules. No TYPE_CHECKING branches. Fix cycles through architecture. Avoid mutable global config, broad Any and shell-string subprocess commands. Bound concurrency, preserve cancellation and close resources.
- C: C11 public headers, explicit fixed-width ABI, checked size arithmetic, explicit init/destroy and ownership, correct calling conventions. Headers must compile in C and C++.
- C++: C++20, named namespaces, direct self-contained includes, one class/enum per file, class-owned functions (static when no instance state), except required ABI functions, operators and entrypoints. No anonymous namespaces or using namespace in headers. No descriptive method/member/section comments in headers. RAII, rule of zero, unique ownership by default, shared ownership only where real, weak refs to break cycles, no unclear raw owning pointers, unchecked casts or avoidable manual new/delete. Use narrow clang-format off/on regions around lambdas per owner preference.
- Java/JNI: explicit checked mappings, direct imports, one type per file, bounded local references, correct thread-specific JNIEnv and exception translation. Keep global/weak references tied to actual ownership.
- Kotlin/Android: structured coroutines, cancellation propagation, explicit scopes/dispatchers, one type per file. New sample UI uses MVVM and one-way state flow. Keep business logic outside views. No GlobalScope, unsafe non-null assertions or leaked Activity references. Use the checked-in Gradle wrapper.
- Objective-C: ARC, correct prefixes/selectors, nullability, explicit bridge ownership, block lifetime, module maps and Swift import metadata. One primary type per file, declarations and implementation paired.
- Swift: one type per file, MVVM for new sample apps, structured concurrency, MainActor for UI, deliberate Sendable, ARC and weak capture where justified. No force casts/unwraps or unchecked concurrency escape without proof. Test actual SDK imports and availability.
- Dart/Flutter: explicit isolate ownership, typed APIs, lifecycle and cancellation. Keep FFI and web adapters separate. Explicit native resource disposal, no invalid borrowed-view escape or synchronous foreign-thread return. New sample UI separates models, views and view models where appropriate.
- C#: typed interop, precise layout/calling convention, SafeHandle/IDisposable, rooted callbacks, cancellation-aware Task and explicit ownership. Avoid exceptions crossing native ABI.
- JavaScript/TypeScript: ESM, strict TypeScript, runtime input validation, exact BigInt mapping, explicit cleanup, bounded tasks and no unnecessary CommonJS compatibility. Review npm dependency lifecycle scripts before approving them.
- WASM: explicit linear-memory bounds, growth and borrow policy, exact integer conversions, rooted callbacks, no stale views.
- Markdown: clear headings, portable CommonMark/GFM, correct relative links and renderer anchors, fenced code with language labels, no fake runnable examples, meaningful image alt text. Validate real rendered documentation.

### Formatting configuration

Commit the formatter and editor settings when the corresponding language is implemented. Use UTF-8, LF, final newline and trailing-whitespace cleanup except significant Markdown hard breaks. Default four spaces for native/Python/Swift/Kotlin/Java/C#/Dart, two for JS/TS/JSON/YAML/HTML/CSS/SVG and Markdown indentation, tabs for Makefile recipes. Respect tool-required syntax.

| Tool | Required setting |
| --- | --- |
| Ruff | line-length = 320, format.skip-magic-trailing-comma = true, lint.isort.split-on-trailing-comma = false |
| clang-format | ColumnLimit: 0 |
| swift-format | lineLength: 320 |
| SwiftLint | line_length: 320 |
| ktlint | max_line_length = 320 in the Kotlin section of .editorconfig |
| Prettier | printWidth: 320 |

Use valid language-specific settings for remaining formatters. No blanket disable of lint/format or whole-file formatter exclusions merely to hide style errors. Generated defaults should follow these conventions where language syntax permits. Consumer overrides are explicit and do not change the repository's own style.

## Ownership, security and privacy

Name the owner of every task, callback, registration, subscription, native handle, allocation, buffer and lock. Validate sizes, alignment, ranges, encodings, handles, ABI compatibility and caller/runtime origin at the real boundary. Never return dangling references or silently replace failure with empty/success. Distinguish expected Result failures, runtime errors, absence, cancellation and successful empty values.

No exceptions cross ABI. No foreign callback, scheduler or deleter runs while internal locks are held. Establish lock ordering, exactly-once terminal state, shutdown behavior, cancellation and actual execution lifetime. Cancel does not prove foreign work stopped. DataView and MutableDataView are direct synchronous parameter-only borrows. Reject stored, returned and async borrowed values. DataRef is an owning reference. Validate handles against runtime-owned metadata and acquire their live references atomically. Caller cancellation does not end provider execution. Drain operations, remove registrations and invalidate handles, then drain the releases caused by those actions on live owning executors before detaching a runtime. Keep cleanup available when business calls are blocked. Do not allow a borrowed view to become DataRef unless its true owner can be retained with a legal independent lifetime. Copies must be explicit. Ordinary value types and collections do not promise shared identity. Never claim zero-copy without appropriate evidence. Check portable key equality and distinct optional states across runtimes. Completion tokens remain valid until actual provider ownership ends. A synchronous callback, including one returning void, must finish in its allowed calling context. Only explicit async callbacks can queue owning arguments for later execution. Never implement synchronous Dart callbacks with an asynchronous NativeCallable.listener. Reject borrowed values in async dispatch. Initialize completion state before starting foreign work and retain start-call references through inline completion. A lossless stream obeys demand, drains accepted values on normal end and releases pending values on cancellation or failure. An empty stream can complete before the first item. Check reentrancy and race conditions even in managed runtimes.

Treat IDL, YAML, manifests, native inputs, external SDK output and package archives as untrusted data. Templates and implementation build extensions are explicit trusted developer input. Bound parser nesting and resource use. Reject path traversal, unintended symlink writes, ABI mismatch and unsupported combinations. Use subprocess argument arrays, timeouts and redacted logs. Never run arbitrary commands from IDL. Use safe archive extraction and atomic/owned writes.

Use least-privilege CI permissions, latest stable verified and pinned dependencies and actions, explicit current SDKs, no credentials on untrusted PRs and no automatic external publication. Keep private keys, tokens, signing stores, .env files, personal data, real camera images, logs, caches, .venv, build outputs, package archives and local IDE files out of commits. Keep lockfiles, sanitized fixtures, required wrappers and source assets. A tracked secret needs rotation and an authorized remediation plan, not only an ignore rule.

Security review records assets, threat boundaries, actual entrypoints, source location, trigger, effect, evidence and fix. Use positive and negative tests, fuzzing, sanitizers, dependency checks and redacting secret scanning where justified. Do not claim a security guarantee from a clean scan. Use fake sample credentials and do not log passwords.

## Git and delivery

Work on the authorized current main branch for requested direct repository edits. Do not create branches, PRs, automated dependency PRs or merge commits unless the workflow or owner actually requests them. Use task-aware branch names if authorized and needed. Use a short imperative English conventional subject, for example docs: clarify module settings or fix: retain callback owner, or the exact supplied issue key. No invented task ID, agent attribution, generated-by footers or co-author trailers.

Before local edits and staging, inspect git status --short --branch, unstaged and staged diffs, untracked/ignored paths and actual author identity. Preserve unrelated user changes. Stage intended paths, check git diff --cached --check and review the staged diff. Use one reviewed commit per requested delivery and the real configured human identity. If editing through a connector, inspect the current remote file/tree, use current SHAs and a reviewed commit, and report integration identity limitations accurately.

Do not implicitly push, reset, clean, stash, amend, delete branches, rewrite history or create tags/releases. A direct requested GitHub edit authorizes the corresponding remote commit only. No unconditional force push. The single-root history policy explicitly authorized for the skills repository does not itself authorize rewriting this repository. A future explicitly authorized snapshot rewrite must follow the Git skill's complete-tree and explicit force-with-lease procedure.

## Version and release policy

Current development version: 0.0.1. Do not increment it unless the owner requests that specific change. The canonical version will live in pyproject.toml when the package exists, with derived runtime/CLI/artifact metadata and independent ABI/module versions.

Development builds and CI artifacts do not constitute releases. A version change does not authorize a Git tag, GitHub Release, PyPI, TestPyPI, npm, Maven, NuGet, pub or other external publication. Do not create any tag or release without explicit approval. Do not publish a placeholder to reserve a name.

Production PyPI publication is forbidden until all PROJECT.md acceptance gates pass on the exact revision, the owner confirms completion and explicitly approves that version for publication. Future pending Trusted Publisher: project polyglue, owner polyglue, repository polyglue, workflow publish.yml, environment pypi. No registry upload-capable workflow or real cloud deployment until separately authorized. Implementing and testing a consumer-facing deploy command does not authorize any external upload. Normal CI builds, tests and retains test artifacts only. Future publication must be manually initiated, protected, use OIDC in a dedicated publish job and upload the exact tested wheel/sdist. No persistent registry token, automatic publish trigger or skip-existing workaround. See PROJECT.md for full requirements.

## SDK versioning and deployment

The tool's version remains independent of IDL module versions, runtime ABI and consumer SDK version/build number. Resolve products.<id>.artifact.version and build_number once from the product configuration. Pass these exact values to CMake and ecosystem tooling, generated product metadata, archive paths and manifests. Do not duplicate manually edited version values, increment them automatically, change the ABI identity on a build number change or alter package versions to conceal a registry conflict. Validate platform constraints and final binary metadata. Keep per-product metadata in staging to avoid overwriting shared generated source. Derive embedded metadata from the resolved build plan, not from a self-referential final artifact manifest.

Implement only one optional Python deployment integration using the latest stable verified boto3/botocore. Support AWS S3, Cloudflare R2 and endpoints with the required S3 behavior. Other deployment protocols belong to consumer-owned scripts using the artifact manifest. No custom cloud framework. Deployment consumes the exact validated package bytes, version and build number. No implicit build, version increment, publish or upload. The completed artifact manifest hashes payloads, the checksum file also hashes the manifest, and neither hashes itself. Do not embed final artifact hashes recursively in the payloads. Explicitly select the destination and artifact. Dry-run must work without network or credentials. Use standard scoped credential providers, HTTPS and secret redaction. Never store keys in code, YAML, logs, manifests or packages.

Use conditional object creation, actual checksum verification and a completion manifest written last. Claim the exact artifact manifest first and reject a conflicting identity before uploading any other object. Reconcile ambiguous completion using actual remote bytes, not by issuing an unconditional write. Custom S3 endpoints must use explicitly selected credentials intended for that endpoint, never unrelated AWS role credentials. Never overwrite or delete remote objects automatically, trust ETags as SHA-256, or claim a multi-object atomic transaction. An identical re-run may verify and reuse existing bytes. Conflicting bytes require a new build number or explicit destination. Keep ordinary deployment tests network-free and cloud-credential-free. CI may fetch declared dependencies and toolchains. Real cloud verification requires explicit authorization, scoped test credentials and isolated prefixes. Report missing access as a blocker. See PROJECT.md sections 7.8 and 20.10.

## Testing, CI and review

Before changing code, read the contract, affected direct/transitive consumers, configuration and tests. State the invariant and its owner. Implement the final behavior and update affected consumers together. Do not hide partial failures or add speculative compatibility.

Use real compiler, formatter, linter, type checker, tests and appropriate runtime/SDK. Every changed behavior has meaningful verification, reusing existing cases where they already prove the contract. Each new test must protect a real invariant, reachable defect, distinct conversion/lifecycle path or platform integration risk. No trivial getter tests, duplicate assertions, arbitrary permutations, artificial sleeps or tests written to inflate counts. Prefer shared parameterized fixtures, deterministic concurrency and bounded property/fuzz testing. Verify all relevant directions, types, nested types, annotations, imports, output layouts, override templates and binary artifacts. Every feasible ordered language pair must execute all supported type cases and distinct valid usage paths, including date/time, custom types, async, callbacks, streams and ownership. Compare expected case IDs against real executions and fail on missing required cases. The required inventory is independent of backend self-reported capabilities. Missing implementations cannot be classified as unsupported to pass CI. Test user-owned external descriptors and adapters from an installed generator without source changes, including conversion failures and source/prebuilt consumers. Test clean installed consumers outside the repository. A generated declaration or successful compile does not establish interoperability.

Required target CI includes C, C++, Java, Kotlin desktop/Android, Objective-C, Swift/Apple platforms, Python, Dart, Flutter native/web, C#, JS/TS and WASM. Follow the full platform and case matrix in PROJECT.md. Use ASan/LSan, UBSan, separate TSan, MSan when supported, runtime-specific lifetime diagnostics, deterministic race orchestration and watchdogs. Exercise use-after-free, double-free, overflow, uninitialized memory, leaks, stale handles, reference cycles, cancellation/completion races, deadlocks, reentrancy, allocator mismatch, invalid buffer scopes, teardown and explicit copy counters. Run real sample HTTP, grayscale and fake login calls across language boundaries. Device-only evidence is separate from fixtures.

Run tests on the packaged AAR, JAR, XCFramework, Swift package, CMake package, wheel, Dart/Flutter, NuGet and npm/WASM artifacts, not only source code. Reuse the full conformance suite through the packaged consumer where practical. Do not repeat identical source and package tests without a distinct risk. Inspect binary metadata, architectures, exports, debug symbols, dependency closure and release optimization. Keep evidence tied to SHA, actual SDK/compiler, artifact manifest hash and payload hashes. Packaging structural validation is not test approval. Keep package bytes immutable after inspection. Run installed-package tests against those bytes. Deploy requires applicable product test evidence for the same bytes and does not rebuild or retest.

Use the detailed checklist in PROJECT.md section 22 as the backlog and acceptance contract. Keep items unchecked until implementation, meaningful tests and documentation are verified. Review correctness, API/ABI, state, memory, concurrency, security, maintainability, dependency impact, documentation and all affected language bindings. Prioritize actionable confirmed defects. Fix root causes, add regressions, rerun checks and inspect CI logs. No skipped mandatory tests, false green jobs, disabled checks or fake evidence. Missing tools/devices are blockers. Report exact checks, failures, commit and remaining limitations. Do not assert that tests prove the absence of all possible defects.

### CI speed and caching

Use the latest stable verified GitHub Actions and native ecosystem caches for uv, Gradle/JVM, Android, SwiftPM, CMake/native, Dart/Flutter, NuGet, npm and Emscripten where relevant. Key caches by lockfiles, OS, toolchain, SDK, architecture and ABI-affecting options. Compiler caching is optional when measured useful. Never cache test verdicts, secrets, unverified final binaries or mix sanitizer and release artifacts. Use verified same-run artifacts to share generated sources, native libraries and packages. Run the tests even on cache hits. Keep independent jobs parallel, avoid repeated builds and dependency installation, bound timeouts and measure cold/warm CI. Do not reduce coverage or omit transitive consumers for speed. Documentation-only changes may run documentation checks without rebuilding unchanged executable inputs, but final acceptance requires real execution on the candidate revision. Run long stress/fuzz/device tests deliberately when relevant and before release, not unnecessary recurring jobs. See PROJECT.md section 19.6.

### Final review and cleanup

Before delivery, verify the detailed PROJECT.md checklist against actual source and test evidence. Compare README.md, AGENTS.md, PROJECT.md and all existing docs/ with real behavior, commands, versions, capabilities, examples and CI. Fix real inconsistencies, validate local links and runnable examples, and do not invent documentation for unsupported features. Remove obsolete code, dead files, redundant tests, stale generated artifacts, temporary logs, caches and unused dependencies within the authorized task scope. Do not delete unrelated user files, source fixtures, lockfiles or required evidence. Review the final tree and diff, run warranted checks again and inspect actual CI results. Report only completed work, exact evidence and remaining blockers. Preserve version and publication restrictions.
