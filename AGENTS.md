# PolyGlue

## Purpose and capabilities

PolyGlue is a planned Python interface compiler and source generator for typed, bidirectional interoperability between native and managed runtimes. The current development version is 0.0.1. The repository currently contains the specification and project documentation, not a working compiler or native runtime.

Read [PROJECT.md](PROJECT.md) before implementation. It defines product scope, all target languages and platforms, IDL semantics, module-first configuration, template overrides, ABI, native packaging, examples, test matrix and acceptance gates. Do not claim a planned capability has been implemented.

## Owner standards

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
- README.md: public introduction and project status.
- AGENTS.md: working rules.

Planned implementation map (create directories when they contain actual functionality):

- src/polyglue/: Python CLI, parser, semantic resolver, IR, config, diagnostics, backends, templates and build orchestration.
- support/: C++20 runtime, C11 ABI surface and language-specific support libraries.
- cmake/: build options, dependency targets, sanitizer configuration, install/export and toolchain integration.
- examples/: shared IDL modules and real consumer/provider apps for each language.
- tests/: compiler, generated-code, native, cross-language, memory, concurrency, installed-consumer and fuzz tests.
- docs/: current user documentation, not implementation plans disguised as supported features.
- extras/images/: source branding assets.
- .github/workflows/: independent target CI and artifact checks.
- build/ and dist/: ignored generated build and package outputs.

The compiler resolves logical symbols, module dependencies, type/ABI identities, naming, annotations, physical file plans and imports before rendering Jinja2. Templates render validated models and may be overridden per module and target. No untrusted IDL can execute code or select arbitrary output paths.

The runtime implements shared ABI mechanics, ownership, references, buffers, async/callbacks, cancellation and optional registry. Generated adapters connect typed interfaces in both directions. Keep business logic in the consumer/provider implementations. Use one compatible runtime per execution context. Python is the build-time generator and orchestrator, not a required runtime in non-Python applications. Do not introduce mandatory JSON serialization, Protocol Buffers, network RPC or compatibility layers with other tools.

Modules are the unit of generation. Products aggregate modules for binary distribution without changing module identity. Use CMake for native code and the proper ecosystem tooling for Gradle, Apple, SwiftPM, Python, Dart/Flutter, .NET and JS/TS/WASM. Keep build plans and subprocess execution in Python and reuse the same CLI locally and in CI. No duplicate build systems or speculative helper frameworks.

## Development commands

No runnable compiler, package metadata, build system or CI exists yet. Do not describe a planned command as working.

Implement and document the real commands as features become available. Planned interfaces include uv sync --locked, uv run --locked ruff check ., uv run --locked ruff format --check ., uv run --locked pytest, uv run --locked polyglue validate, generate, doctor, build, test, package, run, clean and templates list/export/check. Makefile targets must be thin calls into existing tools, not a duplicate implementation. Update this section with verified setup, lint, test and packaging commands as each phase lands.

Use uv for Python dependencies and explicitly requested standalone Python tooling. Use the language's proper SDK and toolchain for native and application code. Do not create unrelated wrappers or background refresh automation.

## Code standards

Write code, identifiers, comments, technical documentation and commit messages in clear English. Prefer meaningful names, concrete responsibilities, early returns, named intermediate results and visible error paths. Separate validation, computation, mutation, I/O and return with blank lines. Avoid long chains, deep nesting, repeated business rules, hidden side effects, needless else after return and generic utility buckets. Extract helpers only for a meaningful responsibility or real reuse. Do not add interfaces, factories or abstractions without an actual boundary.

Keep every ordinary function call, full signature and string literal on one source line. Name complex arguments first. Structural blocks, collection/object literals and trailing closures keep normal indentation. Fix formatter configuration rather than accepting wrapped calls. Join already-wrapped calls and verify formatting twice is idempotent.

Give each class, enum, component, screen and view its own appropriately named file, including supporting types, except for required language/tool constructs. Follow the mandatory filename policy below. Do not hide multiple types in one file to evade the rule.

Comments are rare, in English, explain necessary intent and use complete sentences with initial capital and final period. Keep each comment sentence on one line. No decorative section comments, redundant narration or prose semicolons. Preserve required directives and license notices. Use no legacy aliases or compatibility shims unless specifically requested.

### Filenames and paths

Hyphens (dash, kebab-case) are mandatory for repository-owned multiword filenames and directories wherever the language and toolchain allow them. Do not choose underscores merely for convenience or personal preference. Examples: user-repository.idl, user-repository.hpp, user-repository.cpp, file-header.j2, dependency-check.cmake, build-android.py (standalone script), kotlin-android.yml and memory-safety.md. Apply the rule to source files, templates, tests, documentation, scripts, assets, generated files and workflow filenames.

Exceptions are narrow: Python importable module/package names and required files such as __init__.py, language/tool-required discovery or naming conventions (including enforced Dart lowercase_with_underscores lint and Java public-type filenames), symbol-named files required by the adopted language profile, and exact standard filenames such as CMakeLists.txt, Package.swift, pyproject.toml and AGENTS.md. Record the reason when a new exception is needed. A standalone Python script that is not imported as an ordinary Python module uses hyphens. Do not change required identifiers, ABI symbols, package names, configuration keys or environment variables just to remove underscores from filenames. Consumer-defined naming overrides remain supported; the repository and official default generated output obey this policy.

### Modern Python and dependency freshness

Use the newest stable CPython release and latest stable uv for active development, tooling and CI. Use pyproject.toml with explicit build-system and project metadata, src layout, uv.lock, dependency groups, uv sync --locked, uv run --locked, uv add, uv lock --upgrade and uv build --no-sources as applicable. Use the latest stable Ruff, pytest, Hypothesis, Lark, Jinja2 and other justified dependencies. Prefer modern supported typing, standard-library APIs and native async patterns; do not add legacy Python compatibility or duplicate pip/requirements.txt/Poetry/Pipenv/virtualenv workflows. uv manages the development environment; pip installation is a supported consumer option, not the development workflow. Keep distribution compatibility ranges distinct from exact development lock resolution.

Always use the newest stable released versions of direct runtime, development, build, test and packaging dependencies, GitHub Actions (including reusable workflows and third-party actions), SDKs and toolchains at the time of implementation or maintenance. Verify the actual latest stable release from the official upstream release, registry or tool documentation rather than relying on memory, stale examples, or an assumed latest major. Do not choose beta, RC, nightly or moving main/master dependencies unless the owner explicitly approves them. Do not add unnecessary dependencies simply because newer tools exist.

Resolve and test upgrades together across all affected consumers and targets. Check the latest mutually compatible versions of coupled ecosystems such as Kotlin/AGP/Gradle/JDK, Xcode/Swift and Dart/Flutter. An older direct version is an explicit blocker or exception, never a silent choice: document the newest version, the concrete incompatibility, tested alternative and required owner approval. Transitive versions must respect real upstream constraints; report incompatible or vulnerable resolutions and fix them where possible. A dependency update does not authorize a PolyGlue version bump, tag, release or publication.

Keep lockfiles committed and update them deliberately using ecosystem-native tools. Pin the latest verified stable action release to its immutable commit SHA with the release tag in a comment. Pin native source revisions and archive hashes. Use latest stable runner images where appropriate and record the exact SDK/compiler versions actually installed. Use fixed resolved versions in builds and release evidence; no unreviewed floating downloads or lockfile upgrades inside ordinary CI. Review dependency/action currency whenever changing implementation, CI or packaging and again before an authorized release. Run the applicable complete build/test matrix after upgrades. No automatic dependency-update PRs, scheduled mutation, or auto-publication without separate authorization.

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

No exceptions cross ABI. No foreign callback, scheduler or deleter runs while internal locks are held. Establish lock ordering, exactly-once terminal state, shutdown behavior, cancellation and actual execution lifetime. Cancel does not prove foreign work stopped. DataView and MutableDataView are scoped borrows; DataRef is an owning reference. Copies must be explicit. Never claim zero-copy without appropriate evidence. Check reentrancy and race conditions even in managed runtimes.

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

Production PyPI publication is forbidden until all PROJECT.md acceptance gates pass on the exact revision, the owner confirms completion and explicitly approves that version for publication. Future pending Trusted Publisher: project polyglue, owner polyglue, repository polyglue, workflow publish.yml, environment pypi. No upload-capable workflow until separately authorized. Normal CI builds, tests and retains test artifacts only. Future publication must be manually initiated, protected, use OIDC in a dedicated publish job and upload the exact tested wheel/sdist. No persistent registry token, automatic publish trigger or skip-existing workaround. See PROJECT.md for full requirements.

## Testing, CI and review

Before changing code, read the contract, affected direct/transitive consumers, configuration and tests. State the invariant and its owner. Implement the final behavior and update affected consumers together. Do not hide partial failures or add speculative compatibility.

Use real compiler, formatter, linter, type checker, tests and appropriate runtime/SDK. Every changed contract has a behavior regression test. Verify all relevant directions, types, nested types, annotations, imports, output layouts, override templates and binary artifacts. Test clean installed consumers outside the repository. A generated declaration or successful compile does not establish interoperability.

Required target CI includes C, C++, Java, Kotlin desktop/Android, Objective-C, Swift/Apple platforms, Python, Dart, Flutter native/web, C#, JS/TS and WASM. Follow the full platform and case matrix in PROJECT.md. Use ASan/LSan, UBSan, separate TSan, MSan when supported, runtime-specific lifetime diagnostics, deterministic race orchestration and watchdogs. Exercise use-after-free, double-free, overflow, uninitialized memory, leaks, stale handles, reference cycles, cancellation/completion races, deadlocks, reentrancy, allocator mismatch, invalid buffer scopes, teardown and explicit copy counters. Run real sample HTTP, grayscale and fake login calls across language boundaries. Device-only evidence is separate from fixtures.

Run tests on the packaged AAR, JAR, XCFramework, Swift package, CMake package, wheel, Dart/Flutter, NuGet and npm/WASM artifacts, not only source code. Inspect binary metadata, architectures, exports, debug symbols, dependency closure and release optimization. Keep evidence tied to SHA and actual SDK/compiler.

Review correctness, API/ABI, state, memory, concurrency, security, maintainability, dependency impact, documentation and all affected language bindings. Prioritize actionable confirmed defects. Fix root causes, add regressions, rerun checks and inspect CI logs. No skipped mandatory tests, false green jobs, disabled checks or fake evidence. Missing tools/devices are blockers. Report exact checks, failures, commit and remaining limitations. Do not assert that tests prove the absence of all possible defects.
