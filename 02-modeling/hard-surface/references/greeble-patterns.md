# Greeble Patterns

## Reusable Greeble Library

Build once, instance everywhere:

| Greeble | Approx Tris | Use |
|---------|-------------|-----|
| Bolt head (hex) | 50 | Surface attachment |
| Vent slot | 100 | Heat dissipation |
| Cable port | 150 | Connectivity |
| LED strip | 80 | Status indicators |
| Hinge bracket | 200 | Mechanical joints |
| Rail segment | 300 | Mounting systems |

## Scatter Rules

- Random rotation on Z only for surface-attached greebles
- Align to face normal using geometry nodes or shrinkwrap
- Density falloff: more greebles near hero camera angles
- Disable greebles on LOD1+

## Collection Structure

```
COL-Greebles
├── GEO-Greeble_Bolt_01
├── GEO-Greeble_Vent_01
└── GEO-Greeble_Port_01
```

Instance via collection instance or geometry nodes scatter.
