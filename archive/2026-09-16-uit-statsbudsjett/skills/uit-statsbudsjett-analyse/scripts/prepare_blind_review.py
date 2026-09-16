"""Lager vurderingspakke uten modellnavn, tidsmålinger eller koblingsnøkkel."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def prepare(run, case_id, inputs, gold_path, output, mapping_path, seed):
    output, mapping_path = Path(output).resolve(), Path(mapping_path).resolve()
    if Path(inputs).resolve() == output or Path(inputs).resolve() in output.parents:
        raise ValueError('Vurderingspakken må ligge utenfor kildemappen.')
    if mapping_path == output or output in mapping_path.parents:
        raise ValueError('Koblingsnøkkelen må lagres utenfor vurderingspakken.')
    if output.exists() or mapping_path.exists():
        raise ValueError('Velg nye filstier; tidligere vurderingsgrunnlag skal bevares.')
    input_paths = list(Path(inputs).rglob('*'))
    if Path(inputs).is_symlink() or any(path.is_symlink() for path in input_paths):
        raise ValueError('Kildepakken kan ikke inneholde symbolske lenker.')
    gold = json.loads(Path(gold_path).read_text(encoding='utf-8'))['cases'][case_id]
    answers, excluded = [], []
    for folder in sorted((Path(run) / 'jobs').iterdir()):
        metrics_path = folder / 'metrics.json'
        if not metrics_path.exists():
            continue
        metrics = json.loads(metrics_path.read_text(encoding='utf-8'))
        if metrics['case_id'] != case_id:
            continue
        if metrics['status'] != 'succeeded':
            excluded.append({'job_id': metrics['job_id'], 'status': metrics['status']})
            continue
        answer = (folder / 'answer.txt').read_bytes()
        json.loads(answer)
        order = hashlib.sha256((seed + metrics['job_id']).encode()).hexdigest()
        answers.append((order, metrics['job_id'], answer))
    output.mkdir(parents=True)
    shutil.copytree(inputs, output / 'input')
    (output / 'gold.json').write_text(json.dumps(gold, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    candidates = {}
    for index, (_, job_id, answer) in enumerate(sorted(answers), 1):
        candidate_id = f'candidate-{index:03d}'
        (output / f'{candidate_id}.json').write_bytes(answer)
        candidates[candidate_id] = {'job_id': job_id, 'answer_sha256': hashlib.sha256(answer).hexdigest()}
    mapping = {'case_id': case_id, 'seed': seed, 'candidates': candidates, 'excluded': excluded,
               'limitation': 'Modellmetadata er skjult. Svarenes innhold er uendret og kan røpe arbeidsfasen. Uferdige jobber uten metrics er ikke med.'}
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return mapping


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--case', required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--gold', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--seed', default='statsbudsjett-review')
    args = parser.parse_args()
    result = prepare(args.run, args.case, args.inputs, args.gold, args.output, args.mapping, args.seed)
    print(f'{len(result["candidates"])} svar kopiert uendret; koblingsnøkkelen ligger utenfor pakken.')
