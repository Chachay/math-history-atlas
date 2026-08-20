from scripts.validate import validate_all
from scripts.build_intersections import build_intersections

def test_sample_data_valid(): assert validate_all()==[]
def test_fourier_is_intersection():
    rows=build_intersections()
    hit=[x for x in rows if x['entity']=='concept-fourier-series']
    assert hit and hit[0]['story_count']==3
