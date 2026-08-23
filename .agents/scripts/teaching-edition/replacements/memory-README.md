# `_artifacts/_memory/`

This is the portable shared memory store for the command center. `MEMORY.md` is the index every agent
reads at session start. New learned facts are added only through the system's sanctioned memory flows;
a fresh teaching shell correctly begins with no learned memory files.

Project-only memories belong in the named project's own `_artifacts/_memory/` store, with a pointer
left in this command-center index.
