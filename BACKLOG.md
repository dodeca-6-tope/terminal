# Backlog

All new state primitives should be headless — data and logic only, no
rendering. Users control how things look.

## Focus control
Track which component owns keyboard input so KeyMap and multiple InputBuffers
coexist without manual guards. The focused component consumes keys; others
ignore them.

## KeyMap
Headless key-binding primitive: maps keys to actions, exposes hint data,
dispatches on key press. Needs focus control to know when to yield to an
active input.

## Modal
Headless modal state (open/close, confirm/cancel) so apps don't hand-roll
overlay logic every time. Should integrate with focus control (modal captures
input while open).
