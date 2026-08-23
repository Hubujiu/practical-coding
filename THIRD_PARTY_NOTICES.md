# Third-Party Notices

## DeusData/codebase-memory-mcp

Practical Coding's embedded Codebase Memory helper is inspired by and adapts selected lightweight behaviour from:

- Project: `DeusData/codebase-memory-mcp`
- Source: https://github.com/DeusData/codebase-memory-mcp
- License: MIT
- Upstream revision reviewed for the current filtering/concurrency design: `010569fa6ce1bc5d6430f858129243ea1a2e3fd5`

Adapted areas include the always-skip discovery policy and the design principle that graph mutations are serialized per project. Practical Coding does **not** vendor the upstream native parser bundle, Hybrid LSP pipeline, daemon, watcher, MCP server, UI, semantic model, or release binaries.

The upstream MIT license is reproduced below.

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
