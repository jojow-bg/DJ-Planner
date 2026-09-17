# Scheduling model

## Slots and time

Clock times are parsed into minutes. If the end clock is earlier than or equal to the start, the event ends on the following day (equal times represent 24 hours). Availability bounds are mapped onto this event interval. Use clocks that belong to the event's day/night window; dates and time zones are not modeled.

For `n` present DJs, the existing algorithm chooses a standard duration close to `event duration / n`, rounded to a multiple of 15 minutes. The first `n - 1` slots receive this duration; the last receives the remainder. If a rounded duration leaves no positive final slot, the algorithm reduces it or falls back to equal fractional durations.

Example: 20:00–00:00 and five DJs produces 45, 45, 45, 45 and 60 minutes. A single DJ gets the entire interval. Off-grid starts are preserved. This behavior is deliberately retained from the working application, including its exceptions; strict quarter-hour boundaries are a future option.

## Hard constraints

Let `x[i,d]` be 1 if DJ `d` plays slot `i`, otherwise 0.

- For each slot, `sum_d x[i,d] = 1`.
- For each present DJ, `sum_i x[i,d] = 1`.
- Assignments outside a DJ's complete availability window are set to 0.
- A lock sets its assignment to 1; contradictory locks are rejected or make the model infeasible.

An unavailable DJ is omitted. There is no option for multiple appearances in one event.

The validator also checks generated boundaries, chronological slot indices, positive durations, complete roster coverage and availability. A lineup generated for old event times cannot be silently archived against new times.

## Objective

A slot's value is the duration-weighted sum of overlapping time bands. Uncovered minutes contribute zero; overlapping bands contribute additively, so avoid overlapping bands unless intentional.

For each candidate assignment, the score combines:

| Term | Existing weight | Effect |
| --- | --- | --- |
| Slot value × deficit in historical mean value | 120 | Favors higher-value slots for previously disadvantaged DJs |
| Slot duration × deficit in cumulative minutes | 0.08 | Favors longer slots for DJs with less total playing time |
| Proximity to any historical relative position | 75, inside a 0.28 radius | Discourages repeating historical positions |

Relative positions run from 0 (opening) to 1 (closing); a single slot uses 0.5. Historical baselines include all recorded DJs, even those not attending the current event. DJs without history use those baselines. A small roster-order term breaks some ties; coefficients are scaled by 1,000 and rounded to integers for CP-SAT.

These weights express competing preferences, not a statistical guarantee of fairness. Accumulated minutes are not normalized by attendance. Positions anywhere in the full history influence the repeat penalty; history is not restricted to the latest event.

## Results and errors

The search uses eight workers and an eight-second limit. `OPTIMAL` and `FEASIBLE` results are accepted. A timeout without a solution is distinguished from proven infeasibility and invalid models. Multiple equally good solutions can produce different orders.

Infeasibility diagnostics list legal slots per DJ. They are not a minimal conflict explanation: every DJ may individually have a legal slot while two DJs compete for the same single slot.

Manual swaps preserve the roster but can violate availability. The UI reports violations; validation is required before archive/export. Locks prevent manual swapping of locked slots.
