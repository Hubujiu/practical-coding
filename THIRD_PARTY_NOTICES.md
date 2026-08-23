# Third-Party Notices

## DeusData/codebase-memory-mcp

Practical Coding uses `DeusData/codebase-memory-mcp` as the optional Codebase Memory backend.

- Project: `DeusData/codebase-memory-mcp`
- Source: https://github.com/DeusData/codebase-memory-mcp
- License: MIT
- Upstream revision reviewed when the direct-backend policy was established: `010569fa6ce1bc5d6430f858129243ea1a2e3fd5`

Practical Coding does not vendor the upstream source tree or release binaries. When Codebase Memory is enabled, the Skill invokes an existing upstream executable or an official package launcher such as `npx --yes codebase-memory-mcp@latest` in CLI mode.

This choice is intentional: parser accuracy, Tree-sitter grammars, Hybrid LSP resolution, semantic search, indexing, coverage reporting, concurrency, and graph queries stay owned and maintained upstream instead of being copied into a divergent Practical Coding implementation.

If Practical Coding later vendors upstream code or carries a source patch, retain the upstream copyright and MIT license terms with the copied/substantial portions.

The upstream MIT license is reproduced below for attribution.

```text
MIT License

Copyright (c) 2025 DeusData

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
