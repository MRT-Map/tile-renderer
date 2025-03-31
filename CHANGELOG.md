# Changelog

## Planned

## v5.0.7 (20250331)
* upgrade dependencies for Python 3.13
* change `requests` to `niquests`

## v5.0.6 (20241203)
* HTML escape component display names in svg element generation

## v5.0.5 (20241203)
* Component.tiles now returns empty set if no nodes in component

## v5.0.4 (20241202)
* Don't process component if it has no nodes

## v5.0.3 (20240727)
* Redirect all logging to stderr
* Increase size of text for `subdistrict`, `district`, `town`, `state`, `country`
* everything can now be accessible from `import tile_renderer` instead of having to import individual submodules

## v5.0.2 (20240727)
* fix `ValueError: A linearring requires at least 4 coordinates.` error

## v5.0.1 (20240726)
* add `version` field to the `Skin` format

## v5.0.0 (20240726)
* rewrote the renderer

## v0-v4
https://github.com/MRT-Map/tile-renderer/blob/old/docs/changelog.rst
