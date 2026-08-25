import React from 'react';
import {createRoot,Root} from 'react-dom/client';
import './components/localSemanticMap.css';

type FieldRow={id:string;name:string;concept_ids:string[];concept_count:number;concept_state_count:number};
type ConceptRow={id:string;name:string;fields:string[];state_count:number;first_attested_state_year?:number|null;last_attested_state_year?:number|null};
type Projection={fields:FieldRow[];concepts:ConceptRow[];cross_field_concepts:{concept_id:string;fields:string[]}[]};
let root:Root|null=null,host:HTMLElement|null=null,cache:Promise<Projection>|null=null;
function isAtlas(){const raw=window.location.hash.replace(/^#\/?/,'');const p=raw.split('?')[0].split('/').filter(Boolean)[0];return !p||p==='atlas'}
async function load(){return cache ||= fetch('./data/atlas-projection.json').then(r=>{if(!r.ok)throw new Error(`atlas-projection.json: ${r.status}`);return r.json() as Promise<Projection>})}
function openConcept(id:string){window.location.hash=`#/network?focus=${encodeURIComponent(id)}`}
function unmount(){root?.unmount();root=null;host?.remove();host=null}
async function mount(){if(!isAtlas()){unmount();return}const panel=document.querySelector('.atlas-panel');if(!panel){requestAnimationFrame(mount);return}if(host)return;const data=await load();host=document.createElement('section');host.className='panel semantic-atlas-entry';panel.parentElement?.insertBefore(host,panel);root=createRoot(host);const concepts=new Map(data.concepts.map(c=>[c.id,c]));const fields=data.fields.filter(f=>f.concept_count>0);root.render(<><header><span className="eyebrow">SEMANTIC ATLAS</span><h3>Enter through a mathematical concept</h3><p>Fields are aggregated from the same Concept identities and historical states used by Network and Story.</p></header><div className="semantic-field-grid">{fields.map(field=><article key={field.id}><h4>{field.name}</h4><small>{field.concept_count} concepts · {field.concept_state_count} attested states</small><div>{field.concept_ids.slice(0,8).map(id=>{const c=concepts.get(id);return c?<button key={id} onClick={()=>openConcept(id)}><b>{c.name}</b><span>{c.state_count} states{c.first_attested_state_year?` · ${c.first_attested_state_year}${c.last_attested_state_year&&c.last_attested_state_year!==c.first_attested_state_year?`–${c.last_attested_state_year}`:''}`:''}</span></button>:null})}</div></article>)}</div></>)}
window.addEventListener('hashchange',()=>requestAnimationFrame(mount));window.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(mount));requestAnimationFrame(mount);
