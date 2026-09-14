"""Lager varige fagoppdrag og kontrollerer at hele leveransen finnes."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def prepare_work_orders(config, project):
    project = Path(project)
    run = project / 'leveranser' / config['run_id']
    (run / 'oppdrag').mkdir(parents=True, exist_ok=True)
    for role in config['roles']:
        lines = [
            f'# Fagoppdrag: {role["id"]} – budsjett {config["budget_year"]}',
            f'Status: {config["stage"]}. Delområder: {", ".join(role["parts"])}.',
            'Prioritet 1: korrekt informasjon. Prioritet 2: ferdig fremstilt analyse raskest mulig.',
            '\n## Les før årets kilder',
            'Les arbeidsflyt/leveransekontrakt.md og årets arbeidsdeling. Følg dokumentstatus og fasitgrense.',
            f'Les ditt varige fagminne: `{role["history"]}`.',
            f'Historiske år som skal være dekket: {", ".join(map(str, config["history_years"]))}.',
            'Hvis minnet mangler: rekonstruer det fra historiske originaler først. Dokumenter hull; ikke fyll dem med generell kunnskap.',
            f'Lagre minne-lest.json under leveranser/{config["run_id"]}/deler/{role["id"]}/ med role, sha256 og read_at_utc.',
            '\n## Undersøk og lever',
            f'Startord: {", ".join(role["keywords"])}. Utvid fra historiske erfaringer og årets forutsetninger.',
            'Les hele relevante avsnitt, tabeller og fotnoter. Skill mottaker, nivå/endring, år og budsjettstadium.',
            f'For hver del {", ".join(role["parts"])}: lever notater.md, rapport.md og funn.json i egen delmappe.',
            'Funn må ha kilde, riktig PDF-side og entydige tekstankre til markerte kildeutdrag. Dokumenter også avviste treff og negative søk.',
            f'Lagre årets erfaring separat i arbeidsminne/{role["id"]}/erfaringer-{config["budget_year"]}-proeve.md.',
            'Ikke endre andre rollers filer. Rapporter endringer mot forrige prøve; ikke send noe til andre mennesker.',
        ]
        (run / 'oppdrag' / f'{role["id"]}.md').write_text('\n\n'.join(lines) + '\n', encoding='utf-8')
        for part in role['parts']:
            (run / 'deler' / role['id'] / part).mkdir(parents=True, exist_ok=True)
    return run


def check_memory(role, project, receipt):
    memory = project / role['history']
    issues = []
    if not memory.exists() or not memory.read_text(encoding='utf-8').strip():
        issues.append(f'Mangler historisk fagminne: {memory}')
    if not receipt.exists():
        issues.append(f'Mangler kvittering for innlest minne: {receipt}')
        return issues
    record = json.loads(receipt.read_text(encoding='utf-8'))
    if record.get('role') != role['id']:
        issues.append(f'Feil fagrolle i minnekvittering: {receipt}')
    if not record.get('read_at_utc'):
        issues.append(f'Mangler tidspunkt for innlest minne: {receipt}')
    if not record.get('sha256'):
        issues.append(f'Mangler sha256 i minnekvittering: {receipt}')
    elif memory.exists() and hashlib.sha256(memory.read_bytes()).hexdigest() != record['sha256']:
        issues.append(f'Minnet er endret etter registrert innlesing: {memory}')
    return issues


def check_part(part):
    issues = []
    required = ['notater.md', 'rapport.md', 'funn.json', 'belegg/kildeutdrag.json', 'belegg/kildeutdrag.md']
    for name in required:
        path = part / name
        if not path.exists() or not path.read_text(encoding='utf-8').strip():
            issues.append(f'Mangler delleveranse: {path}')
    if not (part / 'funn.json').exists() or not (part / 'belegg/kildeutdrag.json').exists():
        return issues
    findings = json.loads((part / 'funn.json').read_text(encoding='utf-8'))
    evidence = json.loads((part / 'belegg/kildeutdrag.json').read_text(encoding='utf-8'))
    if [item['id'] for item in findings] != [item['id'] for item in evidence]:
        issues.append(f'Funn og markerte kildeutdrag samsvarer ikke: {part}')
    if findings and not (part / 'belegg/kildeutdrag.pdf').exists():
        issues.append(f'Mangler PDF med markerte kildeutdrag: {part}')
    for record in evidence:
        if record['highlight_count'] < 1 or not (part / 'belegg' / record['image']).exists():
            issues.append(f'Mangler markering eller bilde for {record["id"]}: {part}')
    return issues


def check_delivery(config, project):
    project = Path(project)
    run = project / 'leveranser' / config['run_id']
    issues = []
    for role in config['roles']:
        folder = run / 'deler' / role['id']
        issues.extend(check_memory(role, project, folder / 'minne-lest.json'))
        experience = project / 'arbeidsminne' / role['id'] / f'erfaringer-{config["budget_year"]}-proeve.md'
        if not experience.exists() or not experience.read_text(encoding='utf-8').strip():
            issues.append(f'Mangler årets lagrede erfaring: {experience}')
        for part in role['parts']:
            issues.extend(check_part(folder / part))
    editor = config['editor']
    issues.extend(check_memory(editor, project, run / 'minne-lest-redaktor.json'))
    for name in editor['deliverables']:
        path = run / name
        if not path.exists() or path.stat().st_size == 0:
            issues.append(f'Mangler samlet leveranse: {path}')
        elif path.suffix == '.pptx' and not zipfile.is_zipfile(path):
            issues.append(f'PowerPoint-filen er ikke en gyldig pakke: {path}')
    return {'ready': not issues, 'run_id': config['run_id'], 'issues': issues,
            'scope': 'Filer, minneidentitet og samsvar mellom funn/kildeutdrag. Faglig og visuell godkjenning krever egen kontroll.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'check'])
    parser.add_argument('config', type=Path)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if args.operation == 'prepare':
        print(prepare_work_orders(config, args.project))
    else:
        result = check_delivery(config, args.project)
        content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.write_text(content, encoding='utf-8')
        print(content)
        raise SystemExit(0 if result['ready'] else 2)
