import React from 'react';
import { createRoot, Root } from 'react-dom/client';
import { LocalSemanticMap } from './components/LocalSemanticMap';
import type { SemanticGraph } from './lib/graphQueries';

let root:Root|null=null;
let host:HTMLElement|null=null;
let cache:Promise<SemanticGraph>|null=null;
async function loadGraph(){return cache ||= fetch('./data/semantic-network.json').then(r=>{if(!r.ok)throw new Error(`semantic-network.json: ${r.status}`);return r.json() as Promise<SemanticGraph>})}
function isNetwork(){const raw=window.location.hash.replace(/^#\/?/,'');return raw.split('?')[0].split('/').filter(Boolean)[0]==='network'}
function queryFocus(){const raw=window.location.hash.replace(/^#\/?/,'');const [,q='']=raw.split('?');return new URLSearchParams(q).get('focus')||undefined}
function unmount(){root?.unmount();root=null;host?.remove();host=null}
async function mount(){
  if(!isNetwork()){unmount();return}
  const panel=document.querySelector('.network-panel');
  if(!panel){requestAnimationFrame(mount);return}
  const graph=await loadGraph();
  const initial=queryFocus()||graph.nodes.find(n=>n.node_kind==='Work')?.id||graph.nodes[0]?.id;
  if(!initial)return;
  if(host?.dataset.focusId===initial)return;
  unmount();host=document.createElement('div');host.className='network-local-map-host';host.dataset.focusId=initial;panel.parentElement?.insertBefore(host,panel);
  root=createRoot(host);root.render(<LocalSemanticMap graph={graph} initialFocusId={initial} mode="network"/>);
}
window.addEventListener('hashchange',()=>requestAnimationFrame(mount));
window.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(mount));
requestAnimationFrame(mount);
