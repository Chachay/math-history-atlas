from pathlib import Path

path = Path(__file__).resolve().parents[1] / "app/src/main.tsx"
text = path.read_text(encoding="utf-8")

old = '''type NetworkPoint = { x: number; y: number; year: number };
type NetworkLayout = { positions: Record<string, NetworkPoint>; minYear: number; maxYear: number; ticks: number[] };
'''
new = '''type NetworkPoint = { x: number; y: number; year: number };
type NetworkLayout = { positions: Record<string, NetworkPoint>; minYear: number; maxYear: number; ticks: number[]; yearY: Record<number, number>; height: number };
'''
assert old in text
text = text.replace(old, new, 1)

start = text.index('function buildNetworkLayout(')
end = text.index('\nfunction NetworkView(', start)
old_block = text[start:end]
new_block = '''function buildNetworkLayout(data: Dataset, lookup: Record<string, Entity | Question>): NetworkLayout {
  const storyRefs = [...new Set(data.stories.flatMap(story => story.steps.map(step => step.ref)))].filter(id => lookup[id]);
  const yearByRef = Object.fromEntries(storyRefs.map(id => [id, networkYear(id, lookup[id], data)]));
  const uniqueYears = [...new Set(Object.values(yearByRef))].sort((a, b) => a - b);
  const minYear = uniqueYears[0] ?? 1750;
  const maxYear = uniqueYears[uniqueYears.length - 1] ?? 1860;

  // Chronology is an ordering constraint, not a linear scale. Dense historical periods
  // receive enough visual space to remain readable instead of collapsing together.
  const top = 50;
  const bottom = 50;
  const minGap = 46;
  const targetGap = uniqueYears.length > 1 ? 500 / (uniqueYears.length - 1) : 0;
  const gap = uniqueYears.length > 1 ? Math.max(minGap, Math.min(78, targetGap)) : 0;
  const height = Math.max(640, Math.round(top + bottom + gap * Math.max(1, uniqueYears.length - 1)));
  const yearY: Record<number, number> = {};
  uniqueYears.forEach((year, index) => { yearY[year] = top + index * gap; });

  const storyIndex = new Map(data.stories.map((story, index) => [story.id, index]));
  const memberships = new Map<string, string[]>();
  data.stories.forEach(story => story.steps.forEach(step => {
    const current = memberships.get(step.ref) || [];
    if (!current.includes(story.id)) current.push(story.id);
    memberships.set(step.ref, current);
  }));
  const laneMin = 76;
  const laneMax = 285;
  const laneStep = data.stories.length > 1 ? (laneMax - laneMin) / (data.stories.length - 1) : 0;
  const positions: Record<string, NetworkPoint> = {};
  storyRefs.forEach(id => {
    const memberStories = memberships.get(id) || [];
    const year = yearByRef[id];
    let x = 180;
    if (memberStories.length === 1) {
      const lane = storyIndex.get(memberStories[0]) || 0;
      x = laneMin + lane * laneStep;
      x += (stableFraction(id) - 0.5) * 26;
    } else if (memberStories.length > 1) {
      const lanes = memberStories.map(story => storyIndex.get(story) || 0);
      x = laneMin + (lanes.reduce((a, b) => a + b, 0) / lanes.length) * laneStep;
    }
    positions[id] = { x: Math.max(62, Math.min(292, x)), y: yearY[year], year };
  });
  return { positions, minYear, maxYear, ticks: uniqueYears, yearY, height };
}
'''
text = text[:start] + new_block + text[end:]

old = '''  const yForYear = (year: number) => 45 + ((year - layout.minYear) / Math.max(1, layout.maxYear - layout.minYear)) * 550;
'''
new = '''  const yForYear = (year: number) => layout.yearY[year] ?? 50;
'''
assert old in text
text = text.replace(old, new, 1)

old = '''    <section className="hero-card"><h2>Network — {layout.minYear}–{layout.maxYear} · local Story graph</h2><p>Historical entities remain the graph. Story paths are overlays. Vertical position is chronological; horizontal lanes are derived from Story membership, with shared nodes literally shared between paths.</p><div className="entity-legend"><span><i className="person-mark" />Person</span><span><i className="concept-mark" />Concept</span><span><i className="work-mark" />Work</span></div></section>
'''
new = '''    <section className="hero-card"><h2>Network — {layout.minYear}–{layout.maxYear} · local Story graph</h2><p>Historical entities remain the graph. Vertical order follows chronology, but dense periods expand to preserve readability; vertical distance is not proportional to elapsed time. Horizontal lanes come from Story membership, with shared nodes literally shared between paths.</p><div className="entity-legend"><span><i className="person-mark" />Person</span><span><i className="concept-mark" />Concept</span><span><i className="work-mark" />Work</span></div></section>
'''
assert old in text
text = text.replace(old, new, 1)

old = '''      <svg className="network-svg" viewBox="0 0 360 640">
        <line x1="38" y1="30" x2="38" y2="610" className="time-axis" />
'''
new = '''      <svg className="network-svg" viewBox={`0 0 360 ${layout.height}`}>
        <line x1="38" y1="30" x2="38" y2={layout.height - 30} className="time-axis" />
'''
assert old in text
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Replaced linear time scaling with chronological minimum-spacing layout.")
