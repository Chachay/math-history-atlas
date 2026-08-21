# Origins of mathematical questions and external context

## Purpose

Math History Atlas tracks how **mathematical Questions change, branch, and recombine**. New Questions can arise in at least three historically distinct ways:

1. **internal mathematical development** — an existing mathematical problem, failed method, counterexample, or structure produces a new question;
2. **external stimulation** — a problem in physics, engineering, astronomy, computation, economics, or another domain makes a mathematical response useful and may expose or sharpen an internal mathematical question;
3. **cross-field recombination** — previously distinct mathematical fields, methods, or objects meet and create a new framework or question.

None of these origins is privileged by default. The Atlas is not an application-history atlas, but neither is mathematics treated as historically sealed from the world around it.

The graph's intellectual spine remains mathematical Questions.

## 1. Three development patterns

### A. Internal mathematical development

```text
mathematical question
        ↓
mathematical response / structure
        ↓
new or sharpened mathematical question
```

Examples to investigate include polynomial solvability → permutations/solvability structure, failure of unique factorization → ideal theory, limitations of integration → new integration questions, and uniqueness questions for trigonometric series → exceptional point sets.

These are not secondary to externally stimulated developments. They are a principal mode of mathematical change.

### B. External stimulation

```text
external historical context
        ↓
mathematical response / method
        ↓
new or sharpened mathematical question
        ↓
subsequent mathematical development
```

Examples may include heat conduction → trigonometric representation → representability/convergence questions, or telegraphy/electromagnetism → operational methods → questions about the legitimacy of formal operator manipulation.

### C. Cross-field recombination

```text
mathematical field / method A
             +
mathematical field / method B
             ↓
new framework / invariant / question
```

Later candidates include algebra + topology, algebra + geometry, analysis + geometry, and number theory + geometry. A cross-field link must be historically demonstrated; modern subject classification alone does not establish a historical encounter.

All arrows in all three patterns are hypotheses until supported by historical evidence. Chronological succession alone is not a causal edge.

## 2. Keep external problems out of the mathematical Question layer

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

## 3. Preserve external context rather than deleting it

External context belongs in research packets, Story narrative, Works/Problems where the schema supports them, and provenance-backed transitions. It should answer:

- What concrete problem was the historical actor trying to solve?
- Why was this mathematical technique useful or necessary there?
- What limitation, ambiguity, or surprising success of the technique became mathematically consequential?

A Story may open with heat conduction, planetary motion, telegraphy, mechanics, or another external problem. It should transition quickly to the mathematical tension that the Atlas will follow.

External context should be visually subordinate to mathematical Questions in Network/Atlas projections. If a dedicated context node or badge is introduced later, it should enter the graph as a tributary, not replace the mathematical spine.

## 4. Distinguish context, response, and mathematical question

Use this conceptual separation even where the current schema does not yet encode all three as first-class types.

| Layer | Role | Fourier example | Heaviside example |
| --- | --- | --- | --- |
| External context | Historical demand outside mathematics | heat conduction | telegraphy / electromagnetic transmission |
| Mathematical response | Technique used to attack it | heat equation and trigonometric representation | operational calculus |
| Mathematical question | Internal mathematical tension made salient | representability, convergence, function | meaning and legitimacy of formal operator manipulation |

Do not collapse these into a single causal sentence.

For internal developments, make the analogous distinction between the **prior mathematical problem**, the **response**, and the **new question**. For recombinations, identify both contributing mathematical lines rather than presenting the later framework as if it appeared fully formed.

## 5. Evidence rules for transitions

Historical Critic and Story Critic should test the origin type rather than assuming it.

### For internal development

Ask:

1. Was the earlier mathematical problem actually known to the actor or community claimed?
2. Did the response address that problem in the historical sources?
3. Is the later question documented as contemporary, or reconstructed retrospectively?
4. Are intermediaries missing?

### For external stimulation

Ask:

1. Did the actor actually work on the external problem claimed?
2. Is there evidence that this problem motivated or shaped the mathematical response, rather than merely co-occurring with it?
3. Is the later mathematical question documented as a contemporary concern, or is it a retrospective reconstruction?
4. Are intermediaries missing between a practical technique and its later rigorous or abstract formulation?
5. Does the source support historical influence, or only a modern mathematical relation?

### For cross-field recombination

Ask:

1. Were both mathematical lines historically available to the actors claimed?
2. Is there evidence of actual transfer, synthesis, shared method, or conceptual encounter?
3. Does modern classification make the connection look stronger or earlier than it was?
4. Is credit being concentrated on one person where the synthesis was distributed?

Use calibrated predicates/perspectives such as `motivated`, `provided_context_for`, `made_salient`, `contributed_to`, and `later_connected_to` only when their evidential burden is met. Never upgrade chronology into `caused` or `spawned`.

## 6. Research-unit design rule

Every proposed Research Unit should identify its dominant origin pattern where useful:

- **internal mathematical development**;
- **external stimulation**;
- **cross-field recombination**;
- or an explicitly evidenced mixture.

This is an analytical label, not a requirement to force every episode into one box.

For a unit involving an external domain, the brief must state separately:

- **external context** — what non-mathematical problem matters historically;
- **mathematical response** — what method or object entered the work;
- **Atlas Question** — what mathematical question the unit will add, sharpen, or connect;
- **historical test** — what evidence would justify the claimed outside → inside transition;
- **retrospective-risk test** — which tempting later connection must not be presented as contemporary causation without evidence.

For an internally driven unit, state the prior mathematical problem and what new question or structure it generated. For a recombination unit, state the contributing mathematical lines and the evidence needed to establish a genuine historical encounter.

If a unit cannot identify a substantive mathematical Question, it is probably outside the scope of Math History Atlas.

## 7. Forest-level portfolio rule

Do not choose Research Units solely by asking what chronologically follows the previous unit. At periodic checkpoints, inspect the whole graph and ask:

- Which mathematical branch is overdeveloped or missing?
- Are we documenting both internally generated and externally stimulated developments without imposing a quota?
- Where do historically real cross-field recombinations begin to appear?
- Does the next unit add a new question, deepen an existing branch, or establish a warranted intersection?
- Are we accidentally turning the Atlas into a biography sequence, a single-field timeline, or an application-history timeline?

Breadth and integration are both goals; neither should be manufactured by unsupported historical edges.

## 8. Story/editorial rule

A reader-facing Story may explain enough physics or engineering to make the mathematical stakes intelligible, but it should not become an application tutorial.

A good externally stimulated transition has the form:

> A concrete problem made a mathematical method useful; using that method exposed or sharpened a mathematical difficulty; the Story now follows that difficulty.

An internally driven Story should make the prior mathematical tension equally explicit. A recombination Story should show what each contributing line supplied and when the encounter actually occurred.

The exact historical strength of each clause must match the evidence. When only the modern mathematical relationship is known, label it as later interpretation rather than historical motivation.

## 9. Existing R001 implication

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

## 10. Cross-cutting Theme candidates

A future Theme/guided route may collect reviewed examples under titles such as:

**When the world asks mathematics a new question**

for externally stimulated episodes, while other Themes may follow internally generated tensions or cross-field recombinations.

The external-context Theme must not imply that all later mathematics in those branches was caused by the application. More generally, no Theme should replace the evidence-backed historical graph with a predetermined philosophy of how mathematics develops.
