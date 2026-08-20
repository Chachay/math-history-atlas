import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pathlib import Path
import sys, networkx as nx
from pydantic import ValidationError
from scripts.common import ROOT, load_yaml_files
from scripts.models import Entity, Question, Assertion, FieldModel, ConceptState, Story

ALLOWED_PREDICATES={'authored','raised_question','spawned','reframed','generalized','split_into','merged_with','influenced','motivated','contributed_to'}

def validate_all():
    errors=[]
    raw_entities=load_yaml_files(ROOT/'data/entities'); raw_questions=load_yaml_files(ROOT/'data/questions')
    raw_assertions=load_yaml_files(ROOT/'data/assertions'); raw_fields=load_yaml_files(ROOT/'data/fields')
    raw_states=load_yaml_files(ROOT/'data/concept_states'); raw_stories=load_yaml_files(ROOT/'editorial/stories')
    sources=load_yaml_files(ROOT/'sources')
    def parse(model, rows, label):
        result=[]
        for row in rows:
            try: result.append(model.model_validate(row))
            except ValidationError as e: errors.append(f'{label} {row.get("id","?")}: {e}')
        return result
    entities=parse(Entity,raw_entities,'entity'); questions=parse(Question,raw_questions,'question')
    assertions=parse(Assertion,raw_assertions,'assertion'); fields=parse(FieldModel,raw_fields,'field')
    states=parse(ConceptState,raw_states,'concept_state'); stories=parse(Story,raw_stories,'story')
    all_rows=raw_entities+raw_questions+raw_assertions+raw_fields+raw_states+raw_stories+sources
    ids=[r.get('id') for r in all_rows if isinstance(r,dict) and r.get('id')]
    dup={x for x in ids if ids.count(x)>1}
    if dup: errors.append(f'duplicate IDs: {sorted(dup)}')
    entity_ids={e.id for e in entities}; question_ids={q.id for q in questions}; ref_ids=entity_ids|question_ids
    assertion_ids={a.id for a in assertions}; source_ids={s['id'] for s in sources}; field_ids={f.id for f in fields}
    for e in entities:
        if e.start_year and e.end_year and e.start_year>e.end_year: errors.append(f'invalid years: {e.id}')
        for f in e.fields:
            if f not in field_ids: errors.append(f'unknown field {f} on {e.id}')
    for f in fields:
        for p in f.parents:
            if p not in field_ids: errors.append(f'unknown field parent {p} on {f.id}')
    for a in assertions:
        if a.subject not in ref_ids: errors.append(f'dangling assertion subject {a.subject}')
        if a.object not in ref_ids: errors.append(f'dangling assertion object {a.object}')
        if a.predicate not in ALLOWED_PREDICATES: errors.append(f'unknown predicate {a.predicate}')
        if not a.sources: errors.append(f'missing sources on {a.id}')
        for s in a.sources:
            if s not in source_ids: errors.append(f'missing source reference {s} on {a.id}')
    for s in states:
        if s.concept_id not in entity_ids: errors.append(f'dangling concept state {s.id}')
    for story in stories:
        step_ids={x.id for x in story.steps}
        for step in story.steps:
            if step.ref not in ref_ids: errors.append(f'invalid StoryStep ref {step.ref} in {story.id}')
            if step.narrative and not step.assertion_refs:
                errors.append(f'narrative without assertion_refs on {step.id} in {story.id}')
            if step.narrative and step.temporal_anchor is None:
                errors.append(f'narrative StoryStep missing temporal_anchor on {step.id} in {story.id}')
            for assertion_id in step.assertion_refs:
                if assertion_id not in assertion_ids:
                    errors.append(f'unknown StoryStep assertion_ref {assertion_id} on {step.id} in {story.id}')
        for q in story.question_phases:
            if q not in question_ids: errors.append(f'invalid question phase {q} in {story.id}')
        by_step={x.id:x for x in story.steps}
        g=nx.DiGraph(); g.add_nodes_from(step_ids)
        for link in story.links:
            if link.from_ not in step_ids or link.to not in step_ids: errors.append(f'invalid StoryLink in {story.id}')
            else:
                g.add_edge(link.from_,link.to)
                source=by_step[link.from_].temporal_anchor
                target=by_step[link.to].temporal_anchor
                if source and target and source.from_ is not None and target.from_ is not None:
                    if target.from_ < source.from_ and link.type != 'retrospective':
                        errors.append(f'backward StoryLink requires retrospective type: {story.id} {link.from_}->{link.to}')
        if not nx.is_directed_acyclic_graph(g): errors.append(f'Story DAG cycle detected: {story.id}')
    return errors

if __name__=='__main__':
    errs=validate_all()
    if errs:
        print('\n'.join('ERROR: '+e for e in errs)); sys.exit(1)
    print('Validation passed.')
