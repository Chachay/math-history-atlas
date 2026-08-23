import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { NetworkFocusExplorer } from './components/NetworkFocusExplorer';
import type { ConceptEvolution, SemanticGraph } from './lib/graphQueries';
import './focusEntry.css';

async function loadJson<T>(name:string){
  const response=await fetch(`./data/${name}`);
  if(!response.ok) throw new Error(`${name}: ${response.status}`);
  return response.json() as Promise<T>;
}

function parseFocusFromHash(){
  const raw=window.location.hash.replace(/^#\/?/,'');
  const [path,query='']=raw.split('?');
  if(path!=='network') return {visible:false,focus:undefined as string|undefined};
  const params=new URLSearchParams(query);
  return {visible:true,focus:params.get('focus')||undefined};
}

function FocusEntry(){
  const [route,setRoute]=useState(parseFocusFromHash());
  const [graph,setGraph]=useState<SemanticGraph>();
  const [evolution,setEvolution]=useState<ConceptEvolution[]>([]);
  const [error,setError]=useState('');

  useEffect(()=>{
    const onHash=()=>setRoute(parseFocusFromHash());
    window.addEventListener('hashchange',onHash);
    return ()=>window.removeEventListener('hashchange',onHash);
  },[]);

  useEffect(()=>{
    Promise.all([
      loadJson<SemanticGraph>('semantic-network.json'),
      loadJson<{concepts:ConceptEvolution[]}>('concept-evolution.json'),
    ]).then(([semantic,concepts])=>{setGraph(semantic);setEvolution(concepts.concepts||[]);})
      .catch(err=>setError(String(err)));
  },[]);

  const initialId=useMemo(()=>{
    if(!graph) return undefined;
    if(route.focus&&graph.nodes.some(n=>n.id===route.focus)) return route.focus;
    if(graph.nodes.some(n=>n.id==='concept-function')) return 'concept-function';
    const conceptWithStates=evolution.find(row=>row.states.length>1);
    if(conceptWithStates&&graph.nodes.some(n=>n.id===conceptWithStates.concept_id)) return conceptWithStates.concept_id;
    return graph.nodes.find(n=>n.node_kind==='Work')?.id||graph.nodes[0]?.id;
  },[graph,evolution,route.focus]);

  if(!route.visible) return null;
  return <aside className="focus-standalone-shell">
    <div className="focus-standalone-head"><span>PROJECTION V3</span><h2>Focused exploration</h2><p>Explore one semantic node at a time. The overview above remains the context map; this view keeps each step locally readable.</p></div>
    {error&&<p className="focus-entry-error">Could not load Focus explorer: {error}</p>}
    {graph&&initialId&&<NetworkFocusExplorer key={initialId} graph={graph} conceptEvolution={evolution} initialNodeId={initialId}/>} 
  </aside>;
}

const mount=document.getElementById('focus-root');
if(mount) createRoot(mount).render(<FocusEntry/>);
