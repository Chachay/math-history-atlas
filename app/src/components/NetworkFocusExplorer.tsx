import React, { useMemo, useState } from 'react';
import {
  ConceptEvolution,
  GraphEdge,
  GraphNode,
  SemanticGraph,
  getConceptEvolution,
  getNode,
  groupAdjacentEdges,
  searchNodes,
} from '../lib/graphQueries';
import './networkFocus.css';

type Props = {
  graph: SemanticGraph;
  conceptEvolution: ConceptEvolution[];
  initialNodeId: string;
  onOpenDetails?: (node: GraphNode) => void;
};

type Choice = { edge: GraphEdge; node: GraphNode };

const KIND_LABELS: Record<string, string> = {
  Person: 'Person', Work: 'Work', Problem: 'Problem', Result: 'Result',
  Concept: 'Concept', ConceptState: 'Concept state', Event: 'Event',
};

function nodeYear(node: GraphNode) {
  return node.period?.from ?? node.start_year;
}

function choicesFor(graph: SemanticGraph, focusId: string) {
  const groups = groupAdjacentEdges(graph, focusId);
  const result: { label: string; choices: Choice[] }[] = [];
  for (const [label, edges] of groups) {
    const seen = new Set<string>();
    const choices = edges.flatMap(edge => {
      const otherId = edge.subject === focusId ? edge.object : edge.subject;
      if (seen.has(otherId)) return [];
      const node = getNode(graph, otherId);
      if (!node) return [];
      seen.add(otherId);
      return [{ edge, node }];
    });
    if (choices.length) result.push({ label, choices });
  }
  return result;
}

export function NetworkFocusExplorer({ graph, conceptEvolution, initialNodeId, onOpenDetails }: Props) {
  const [focusId, setFocusId] = useState(initialNodeId);
  const [trail, setTrail] = useState<string[]>([initialNodeId]);
  const [query, setQuery] = useState('');
  const focus = getNode(graph, focusId) || getNode(graph, initialNodeId);
  const groups = useMemo(() => focus ? choicesFor(graph, focus.id) : [], [graph, focus?.id]);
  const results = useMemo(() => query.trim() ? searchNodes(graph, query).slice(0, 7) : [], [graph, query]);

  if (!focus) return <section className="focus-explorer focus-empty">No focus node is available.</section>;

  const focusConceptId = focus.node_kind === 'Concept' ? focus.id : focus.concept_id;
  const evolution = focusConceptId ? getConceptEvolution(conceptEvolution, focusConceptId) : undefined;
  const totalChoices = groups.reduce((sum, group) => sum + group.choices.length, 0);
  const collapsed = totalChoices > 7;

  const navigate = (id: string) => {
    setFocusId(id);
    setTrail(current => [...current, id]);
    setQuery('');
  };
  const jumpTrail = (index: number) => {
    const id = trail[index];
    setFocusId(id);
    setTrail(current => current.slice(0, index + 1));
    setQuery('');
  };

  return <section className="focus-explorer" aria-label="Network focus explorer">
    <div className="focus-search-wrap">
      <input
        className="focus-search"
        value={query}
        onChange={event => setQuery(event.target.value)}
        placeholder="Search works, problems, concepts…"
        aria-label="Search semantic network"
      />
      {results.length > 0 && <div className="focus-search-results">
        {results.map(node => <button key={node.id} onClick={() => navigate(node.id)}>
          <span>{node.name}</span><small>{KIND_LABELS[node.node_kind] || node.node_kind}{nodeYear(node) ? ` · ${nodeYear(node)}` : ''}</small>
        </button>)}
      </div>}
    </div>

    <nav className="focus-breadcrumbs" aria-label="Exploration history">
      {trail.map((id, index) => {
        const node = getNode(graph, id);
        if (!node) return null;
        return <React.Fragment key={`${id}:${index}`}>
          {index > 0 && <span>›</span>}
          <button className={index === trail.length - 1 ? 'current' : ''} onClick={() => jumpTrail(index)}>{node.name}</button>
        </React.Fragment>;
      })}
    </nav>

    <article className={`focus-card kind-${focus.node_kind.toLowerCase()}`}>
      <div className="focus-card-head"><span className="focus-kind">{KIND_LABELS[focus.node_kind] || focus.node_kind}</span>{nodeYear(focus) && <time>{nodeYear(focus)}</time>}</div>
      <h2>{focus.name}</h2>
      {focus.detail && <p>{focus.detail}</p>}
      <div className="focus-card-actions">
        {onOpenDetails && <button onClick={() => onOpenDetails(focus)}>Details</button>}
      </div>
    </article>

    {evolution && evolution.states.length > 0 && <section className="focus-evolution">
      <header><h3>Concept evolution</h3><p>Attested states are ordered by date; chronology alone does not assert causation.</p></header>
      <div className="focus-state-list">
        {evolution.states.map(state => {
          const node = getNode(graph, state.id);
          if (!node) return null;
          return <button key={state.id} className={state.id === focus.id ? 'active' : ''} onClick={() => navigate(state.id)}>
            <time>{state.period?.from ?? '—'}</time><span>{state.label}</span>
          </button>;
        })}
      </div>
    </section>}

    <section className="focus-adjacency">
      <header><h3>Explore from here</h3>{collapsed && <p>{totalChoices} connected items are folded into semantic groups.</p>}</header>
      {groups.map(group => <details key={group.label} open={!collapsed}>
        <summary>{group.label}<span>{group.choices.length}</span></summary>
        <div className="focus-choice-list">
          {group.choices.map(({ edge, node }) => <button key={`${edge.id}:${node.id}`} onClick={() => navigate(node.id)}>
            <span className={`choice-kind kind-${node.node_kind.toLowerCase()}`}>{KIND_LABELS[node.node_kind] || node.node_kind}</span>
            <b>{node.name}</b>
            {nodeYear(node) && <time>{nodeYear(node)}</time>}
          </button>)}
        </div>
      </details>)}
    </section>
  </section>;
}
