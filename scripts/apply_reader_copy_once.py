from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = root / "app/src/main.tsx"
build = root / "scripts/build.py"

text = main.read_text(encoding="utf-8")
replacements = {
    "type Story = { id: string; title: string; fields?: string[]; steps: StoryStep[]; links: { from: string; to: string; type: string }[] };":
        "type Story = { id: string; title: string; description?: string; fields?: string[]; steps: StoryStep[]; links: { from: string; to: string; type: string }[] };",
    "<p>This view is about field evolution. Field branches below are derived from canonical field data; choose one to frame its reviewed Network cluster.</p>":
        "<p>See how mathematical fields split, overlap, and recombine across time. Enter a branch to follow the researched questions and Stories inside it.</p>",
    "<p>Solid colored paths are links inside one Story. Dashed neutral connectors are separately reviewed handoffs between Stories; field framing is derived from Story field metadata.</p>":
        "<p>See where mathematical Stories intersect, branch apart, and hand questions to one another across time.</p>",
    "<p>Read one editorial path vertically. Person links are derived from the assertions supporting each step, not only from direct Person steps.</p>":
        "<p>{story.description || 'Follow the mathematical question through the historical steps that changed it.'}</p>",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"Expected UI text not found: {old[:80]}")
    text = text.replace(old, new, 1)
main.write_text(text, encoding="utf-8")

btext = build.read_text(encoding="utf-8")
old = "            'title': s['title'],\n            'fields': s.get('fields', []),"
new = "            'title': s['title'],\n            'description': s.get('description', ''),\n            'fields': s.get('fields', []),"
if old not in btext:
    raise SystemExit("Expected story-index build block not found")
build.write_text(btext.replace(old, new, 1), encoding="utf-8")

# This migration is intentionally one-shot; remove its runner artifacts from the resulting commit.
(root / ".github/workflows/reader-copy-once.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
