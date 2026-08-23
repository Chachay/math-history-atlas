import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './atlasEntry.css';

type AtlasConcept={
  id:string; name:string; fields:string[]; state_count:number;
  first_attested_state_year?:number|null; last_attested_state_year?:number|null;
  states:{id:string;year?:number|null;label:string}[];
};
type AtlasField={
  id:string; name:string; parents:string[]; concept_ids:string[];
  concept_count:number; concept_state_count:number; related_node_ids:string[];
};
type AtlasProjection={projection_version:number;fields:AtlasField[];concepts:AtlasConcept[];cross_field_concepts:{concept_id:string;fields:string[]}[];notes:string[]};

async function loadProjection(){
  const response=await fetch('./data/atlas-projection.json');
  if(!response.ok) throw new Error(`atlas-projection.json: ${response.status}`);
  return response.json() as Promise<AtlasProjection>;
}
function isAtlasRoute(){return window.location.hash.replace(/^#\/?/,'').split('?')[0]==='atlas';}

function AtlasV3Entry(){
  const [visible,setVisible]=useState(isAtlasRoute());
  const [data,setData]=useState<AtlasProjection>();
  const [error,setError]=useState('');
  useEffect(()=>{const onHash=()=>setVisible(isAtlasRoute());window.addEventListener('hashchange',onHash);return()=>window.removeEventListener('hashchange',onHash);},[]);
  useEffect(()=>{loadProjection().then(setData).catch(err=>setError(String(err)));},[]);
  const conceptMap=useMemo(()=>new Map((data?.concepts||[]).map(row=>[row.id,row])),[data]);
  if(!visible)return null;
  const fields=(data?.fields||[]).filter(field=>field.id!=='mathematics'&&field.concept_count>0);
  return <aside className="atlas-v3-shell">
    <header className="atlas-v3-head"><span>PROJECTION V3</span><h2>Atlas as a concept landscape</h2><p>Fields are aggregated from the researched semantic graph. Concepts bridge the long-range Atlas and their historically situated states in Network.</p></header>
    {error&&<p className="atlas-v3-error">Could not load semantic Atlas: {error}</p>}
    <div className="atlas-v3-fields">
      {fields.map(field=>{
        const concepts=field.concept_ids.map(id=>conceptMap.get(id)).filter(Boolean) as AtlasConcept[];
        return <section className="atlas-v3-field" key={field.id}>
          <header><div><h3>{field.name}</h3><p>{field.concept_count} concepts · {field.concept_state_count} attested states</p></div></header>
          <div className="atlas-v3-concepts">
            {concepts.slice(0,7).map(concept=><button key={concept.id} onClick={()=>{window.location.hash=`#/network?field=${encodeURIComponent(field.id)}&focus=${encodeURIComponent(concept.id)}`;}}>
              <b>{concept.name}</b>
              <span>{concept.state_count} state{concept.state_count===1?'':'s'}{concept.first_attested_state_year?` · ${concept.first_attested_state_year}${concept.last_attested_state_year&&concept.last_attested_state_year!==concept.first_attested_state_year?`–${concept.last_attested_state_year}`:''}`:''}</span>
            </button>)}
          </div>
          {concepts.length>7&&<details><summary>{concepts.length-7} more concepts</summary><div className="atlas-v3-concepts extra">{concepts.slice(7).map(concept=><button key={concept.id} onClick={()=>{window.location.hash=`#/network?field=${encodeURIComponent(field.id)}&focus=${encodeURIComponent(concept.id)}`;}}><b>{concept.name}</b><span>{concept.state_count} states</span></button>)}</div></details>}
        </section>;
      })}
    </div>
    {(data?.cross_field_concepts.length||0)>0&&<section className="atlas-v3-cross"><h3>Concepts crossing field boundaries</h3><div>{data?.cross_field_concepts.slice(0,7).map(row=>{const concept=conceptMap.get(row.concept_id);if(!concept)return null;return <button key={row.concept_id} onClick={()=>{window.location.hash=`#/network?focus=${encodeURIComponent(row.concept_id)}`;}}><b>{concept.name}</b><span>{row.fields.join(' · ')}</span></button>;})}</div></section>}
  </aside>;
}

const mount=document.getElementById('atlas-v3-root');
if(mount)createRoot(mount).render(<AtlasV3Entry/>);
