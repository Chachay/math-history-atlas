import React from 'react';
import { createRoot, Root } from 'react-dom/client';
import { LocalSemanticMap } from './components/LocalSemanticMap';
import type { SemanticGraph } from './lib/graphQueries';

type StoryStep={ref:string;assertion_refs?:string[];temporal_anchor?:{from?:number;to?:number|null}};
type Story={id:string;title:string;steps:StoryStep[]};
type LegacyAssertion={id:string;subject:string;object:string};

let root:Root|null=null;
let host:HTMLElement|null=null;
let cache:Promise<{graph:SemanticGraph;stories:Story[];assertions:LegacyAssertion[]}>|null=null;

async function loadJson<T>(name:string){const r=await fetch(`./data/${name}`);if(!r.ok)throw new Error(`${name}: ${r.status}`);return r.json() as Promise<T>}
function data(){return cache ||= Promise.all([loadJson<SemanticGraph>('semantic-network.json'),loadJson<Story[]>('story-index.json'),loadJson<{assertions:LegacyAssertion[]}>('graph.json')]).then(([graph,stories,legacy])=>({graph,stories,assertions:legacy.assertions}))}
function storyId(){const raw=window.location.hash.replace(/^#\/?/,'');const parts=raw.split('?')[0].split('/').filter(Boolean).map(decodeURIComponent);return parts[0]==='story'?parts[1]:undefined}

function unmount(){root?.unmount();root=null;host?.remove();host=null}

async function mount(){
  const id=storyId();
  if(!id){unmount();return}
  const layout=document.querySelector('.story-layout');
  if(!layout){requestAnimationFrame(mount);return}
  const payload=await data();
  const story=payload.stories.find(s=>s.id===id);
  if(!story){unmount();return}
  if(host?.dataset.storyId===id)return;
  unmount();
  host=document.createElement('div');host.className='story-semantic-map-host';host.dataset.storyId=id;
  layout.parentElement?.insertBefore(host,layout);
  root=createRoot(host);
  root.render(<LocalSemanticMap graph={payload.graph} story={story} legacyAssertions={payload.assertions} mode="story"/>);
}

window.addEventListener('hashchange',()=>requestAnimationFrame(mount));
window.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(mount));
requestAnimationFrame(mount);
