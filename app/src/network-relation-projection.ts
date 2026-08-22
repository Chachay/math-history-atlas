// Temporary projection shim for PR #46 visual review.
// It changes disclosure defaults only; canonical data and Story semantics remain untouched.
// Once the relation-first projection is approved, fold these defaults into NetworkView.

let appliedForNetwork = false;

function applyRelationFirstProjection() {
  const onNetwork = window.location.hash.replace(/^#\/?/, '').startsWith('network');
  if (!onNetwork) {
    appliedForNetwork = false;
    return;
  }

  const hero = document.querySelector<HTMLElement>('.hero-card');
  if (hero) {
    const heading = hero.querySelector('h2');
    const paragraph = hero.querySelector('p');
    if (heading && heading.textContent?.startsWith('Network —')) {
      heading.textContent = heading.textContent.replace('Network —', 'Network — What connects? ·');
    }
    if (paragraph) {
      paragraph.textContent = 'See which Questions, Works, Concepts, and People are connected by reviewed relations. Story selections highlight one curated reading without defining the graph.';
    }
  }

  document.querySelectorAll<HTMLButtonElement>('.story-filter button').forEach(button => {
    if (button.textContent?.trim() === 'Question forest') button.textContent = 'All relations';
  });

  const controls = document.querySelector<HTMLElement>('.network-controls');
  const contextButton = controls?.querySelector<HTMLButtonElement>('button');
  if (!appliedForNetwork && contextButton?.textContent?.includes('Show Work')) {
    appliedForNetwork = true;
    contextButton.click();
    return;
  }

  if (controls && !controls.querySelector('.relation-reading-key')) {
    const key = document.createElement('span');
    key.className = 'relation-reading-key';
    key.textContent = 'Nodes = mathematical/historical objects · Lines = reviewed relations';
    controls.appendChild(key);
  }

  appliedForNetwork = true;
}

const observer = new MutationObserver(applyRelationFirstProjection);
observer.observe(document.documentElement, { childList: true, subtree: true });
window.addEventListener('hashchange', () => queueMicrotask(applyRelationFirstProjection));
queueMicrotask(applyRelationFirstProjection);
