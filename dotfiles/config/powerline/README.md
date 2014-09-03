Powerline uses JSON files for configuration. The unfortunate thing about using JSON for configuration files is that it is illegal to comment JSON files.

Because we want comments, we've followed [Douglas Crockford's suggestion][json-comments] of running our JSON through a JavaScript minifier before use. Too bad it's yet another task to add to the already-complicated build process.

The commented JSON files are indicated by the file extension ``.cjson``. A little non-standard, I know, but it's better than not having comments.

[json-comments]: https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
