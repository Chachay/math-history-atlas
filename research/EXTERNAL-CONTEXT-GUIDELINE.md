# External context and mathematical questions

## Purpose

Math History Atlas is a history of mathematics, not a physics, engineering, astronomy, or technology atlas. External problems matter when they help explain why a mathematical method was introduced, made salient, or tested. The graph's intellectual spine should nevertheless remain mathematical questions.

The recurring pattern to investigate is:

```text
external historical context
        ↓
mathematical response / method
        ↓
new or sharpened mathematical question
        ↓
subsequent mathematical development
```

The arrows are hypotheses until supported by historical evidence. Chronological succession alone is not a causal edge.

## 1. Keep external problems out of the mathematical Question layer

A canonical `Question` should normally be a question that can be stated as a mathematical problem without requiring the reader to follow the external science or engineering application.

Prefer:

- Which functions can be represented by a trigonometric series?
- Under what conditions does the series converge?
- What class of functions is admissible for an integral or representation?
- When can a formal operator manipulation be justified?
- When is a representation unique?

Do not make the main Question layer primarily:

- How does heat propagate?
- How can a telegraph signal be transmitted farther?
- What orbit does a planet follow?
- How does an electromagnetic field behave?

Those may be historically essential contexts, but they should not become the backbone of the mathematical Question network merely because they motivated a work.

## 2. Preserve external context rather than deleting it

External context belongs in research packets, Story narrative, Works/Problems where the schema supports them, and provenance-backed transitions. It should answer:

- What concrete problem was the historical actor trying to solve?
- Why was this mathematical technique useful or necessary there?
- What limitation, ambiguity, or surprising success of the technique became mathematically consequential?

A Story may open with heat conduction, planetary motion, telegraphy, mechanics, or another external problem. It should transition quickly to the mathematical tension that the Atlas will follow.

External context should be visually subordinate to mathematical Questions in Network/Atlas projections. If a dedicated context node or badge is introduced later, it should enter the graph as a tributary, not replace the mathematical spine.

## 3. Distinguish context, response, and mathematical question

Use this conceptual separation even where the current schema does not yet encode all three as first-class types.

| Layer | Role | Fourier example | Heaviside example |
| --- | --- | --- | --- |
| External context | Historical demand outside mathematics | heat conduction | telegraphy / electromagnetic transmission |
| Mathematical response | Technique used to attack it | heat equation and trigonometric representation | operational calculus |
| Mathematical question | Internal mathematical tension made salient | representability, convergence, function | meaning and legitimacy of formal operator manipulation |

Do not collapse these into a single causal sentence.

## 4. Evidence rule for outside → inside transitions

A transition from an external problem to a mathematical development requires evidence appropriate to the strength of the claim.

Historical Critic and Story Critic should ask:

1. Did the actor actually work on the external problem claimed?
2. Is there evidence that this problem motivated or shaped the mathematical response, rather than merely co-occurring with it?
3. Is the later mathematical question documented as a contemporary concern, or is it a retrospective reconstruction?
4. Are intermediaries missing between a practical technique and its later rigorous or abstract formulation?
5. Does the source support historical influence, or only a modern mathematical relation?

Use calibrated predicates/perspectives such as `motivated`, `provided_context_for`, `made_salient`, `contributed_to`, and `later_connected_to` only when their evidential burden is met. Never upgrade chronology into `caused` or `spawned`.

## 5. Do not force every branch to originate outside mathematics

The Atlas should show both kinds of development:

```text
external problem → mathematical method → internal question
```

and

```text
internal mathematical problem → new structure → new internal question
```

Fourier/heat and a future Heaviside/telegraphy unit are candidates for the first pattern. Solvability by radicals and Galois theory are candidates for the second. Neither pattern is privileged as the universal explanation of mathematical change.

## 6. Research-unit design rule

For every proposed unit involving science, engineering, computation, economics, or another external domain, the brief must state separately:

- **external context** — what non-mathematical problem matters historically;
- **mathematical response** — what method or object entered the work;
- **Atlas Question** — what mathematical question the unit will add, sharpen, or connect;
- **historical test** — what evidence would justify the claimed outside → inside transition;
- **retrospective-risk test** — which tempting later connection must not be presented as contemporary causation without evidence.

If a unit cannot identify a substantive mathematical Question, it is probably outside the scope of Math History Atlas.

## 7. Story/editorial rule

A reader-facing Story may explain enough physics or engineering to make the mathematical stakes intelligible, but it should not become an application tutorial.

A good transition has the form:

> A concrete problem made a mathematical method useful; using that method exposed or sharpened a mathematical difficulty; the Story now follows that difficulty.

The exact historical strength of each clause must match the evidence. When only the modern mathematical relationship is known, label it as later interpretation rather than historical motivation.

## 8. Existing R001 implication

R001 remains valid as a Fourier/heat research unit, but `How does heat propagate?` should be understood as historical context rather than the long-term mathematical Question spine of the Atlas.

Future integration work should prefer the mathematical line:

```text
heat context
    ↓
trigonometric representation
    ↓
representability / convergence
    ↓
function concept
```

without erasing the fact that Fourier was solving a physical heat problem.

This is an editorial/modeling clarification, not permission to rewrite R001's historical claims without a reviewed change.

## 9. Cross-cutting Theme candidate

A future Theme/guided route may collect reviewed examples under a title such as:

**When the world asks mathematics a new question**

Candidate episodes include planetary motion/mechanics, vibrating strings, heat conduction, potential theory/electromagnetism, telegraphy/operational calculus, communication/information, and other cases that pass the evidence rule above.

The Theme must not imply that all later mathematics in those branches was caused by the external application.