export type GraphNode = { id:string; node_kind:string; name:string; concept_id?:string; fields?:string[]; detail?:string; period?:{from?:number;to?:number|null}; start_year?:number };
export type GraphEdge = { id:string; subject:string; object:string; predicate:string; relation_family?:string };
export type SemanticGraph = { nodes:GraphNode[]; claims:GraphEdge[]; structural_edges:GraphEdge[]; default_edge_ids:string[] };
export type ConceptEvolution = { concept_id:string; name:string; fields?:string[]; states:{id:string;label:string;period?:{from?:number;to?:number|null}}[]; related_claim_ids:string[]; evidence_transitions:{claim_id:string;from:string;to:string;predicate:string;mode:string}[] };

export function getNode(graph:SemanticGraph,id:string){ return graph.nodes.find(n=>n.id===id); }
export function getDefaultEdges(graph:SemanticGraph){ const ids=new Set(graph.default_edge_ids); return graph.claims.filter(e=>ids.has(e.id)); }
export function getAdjacentEdges(graph:SemanticGraph,id:string){ return [...graph.claims,...graph.structural_edges].filter(e=>e.subject===id||e.object===id); }
export function getNeighbors(graph:SemanticGraph,id:string){
  const seen=new Set<string>();
  return getAdjacentEdges(graph,id).map(edge=>{ const other=edge.subject===id?edge.object:edge.subject; if(seen.has(other)) return null; seen.add(other); return getNode(graph,other); }).filter(Boolean) as GraphNode[];
}
export function getConceptStates(graph:SemanticGraph,conceptId:string){ return graph.nodes.filter(n=>n.node_kind==='ConceptState'&&n.concept_id===conceptId).sort((a,b)=>(a.period?.from??999999)-(b.period?.from??999999)); }
export function getConceptEvolution(rows:ConceptEvolution[],conceptId:string){ return rows.find(row=>row.concept_id===conceptId); }
export function searchNodes(graph:SemanticGraph,query:string){ const q=query.trim().toLocaleLowerCase(); if(!q)return []; return graph.nodes.filter(n=>`${n.name} ${(n.fields||[]).join(' ')}`.toLocaleLowerCase().includes(q)); }

export const READER_RELATION_GROUPS:Record<string,string>={
  problem_relation:'Problems', conceptual_content:'Mathematical ideas', result_relation:'Results', development:'Earlier / later developments', documentary:'Works and attribution', identity:'Concept evolution'
};
export function groupAdjacentEdges(graph:SemanticGraph,id:string){
  const groups=new Map<string,GraphEdge[]>();
  for(const edge of getAdjacentEdges(graph,id)){ const key=READER_RELATION_GROUPS[edge.relation_family||'']||'Related'; const rows=groups.get(key)||[]; rows.push(edge); groups.set(key,rows); }
  return groups;
}
