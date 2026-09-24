# Kitbash Library Spec

## Naming
`GEO-KB_[Category]_[Part]_[Variant]`

Categories: `Handle`, `Bracket`, `Bolt`, `Panel`, `Pipe`, `Vent`, `Switch`, `Label`, `Foot`, `Hinge`

## Grid
- Base module: 0.05m
- Prefer 0.05 / 0.1 / 0.25 / 0.5m extents
- Origin at attach face center

## Collections
`COL-Kitbash_[SetName]` with subcollections per category.

## Export
Instance in scenes; do not unique-mesh every use unless hero.
