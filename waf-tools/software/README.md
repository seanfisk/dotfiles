Waf software tools directory
============================

This directory contains Waf tools which detect and configure specific pieces of software for the dotfiles. Each tool can contain three optional methods:

* `options(ctx)`
* `configure(ctx)`
* `build(ctx)`

These functions will be called during the corresponding stage of the main `wscript` file.

Each of the software tools assumes that our base Waf tools are already loaded.
