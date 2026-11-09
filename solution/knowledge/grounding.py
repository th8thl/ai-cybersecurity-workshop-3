"""Citation membership alone is insufficient: require a matching exact excerpt."""
from jsonschema import validate
from .generation import ANSWER_SCHEMA

def validate_answer(answer, passages):
    validate(answer,ANSWER_SCHEMA)
    if answer['abstain']:
        if answer['claims']:
            raise ValueError('An abstention must not contain claims.')
        return answer
    if not answer['claims']:
        raise ValueError('An answer needs evidence or must abstain.')
    by_id = {p['id']:p for p in passages}
    for claim in answer['claims']:
        source = by_id.get(claim['citation'])
        if source is None or (not claim['quote'].strip() or claim['quote'] not in source['text']):
            raise ValueError('Unsupported answer: citation and exact excerpt must match a retrieved passage.')
    return answer
