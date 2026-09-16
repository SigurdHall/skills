"""Utleder observerte svartider fra råhendelser uten å endre måleloggen."""

import argparse
import json
from pathlib import Path


def content_times(events, answer):
    first_provisional = None
    provisional_text = None
    final_content = None
    completed = None
    invalid_records = 0
    for record in events:
        event = record.get('event')
        if not isinstance(event, dict):
            invalid_records += 1
            continue
        if event.get('type') == 'turn.completed':
            completed = record['elapsed_s']
        item = event.get('item', {})
        if event.get('type') != 'item.completed' or item.get('type') != 'agent_message':
            continue
        text = item.get('text', '')
        try:
            structured = json.loads(text)
        except json.JSONDecodeError:
            structured = None
        summary = structured.get('summary', text) if isinstance(structured, dict) else text
        if first_provisional is None and summary.lstrip().startswith(('FORELOPIG:', 'FØRSTE VURDERING:')):
            first_provisional = record['elapsed_s']
            provisional_text = summary
        if answer is not None and structured == answer:
            final_content = record['elapsed_s']
    basis = 'matching_final_answer_event' if final_content is not None else None
    if final_content is None and answer is not None and completed is not None:
        final_content, basis = completed, 'turn_completed_upper_bound'
    return {'first_provisional_s': first_provisional, 'first_provisional_text': provisional_text,
            'final_content_s': final_content, 'final_time_basis': basis,
            'invalid_event_records': invalid_records}


def review_times(draft, review):
    result = {'review_wait_from_draft_s': None, 'review_after_draft_s': None,
              'pipeline_total_s': None, 'review_within_300s_of_draft': False,
              'review_after_provisional_s': None, 'review_within_300s_of_provisional': False}
    if draft.get('final_content_s') is None or review.get('final_content_s') is None:
        return result
    draft_ready = draft['started_monotonic_s'] + draft['final_content_s']
    review_done = review['started_monotonic_s'] + review['final_content_s']
    result.update({
        'review_wait_from_draft_s': review['started_monotonic_s'] - draft_ready,
        'review_after_draft_s': review_done - draft_ready,
        'pipeline_total_s': review_done - draft['started_monotonic_s'],
        'review_within_300s_of_draft': draft['status'] == review['status'] == 'succeeded' and review_done - draft_ready <= 300,
    })
    if draft.get('first_provisional_s') is not None:
        provisional = draft['started_monotonic_s'] + draft['first_provisional_s']
        result['review_after_provisional_s'] = review_done - provisional
        result['review_within_300s_of_provisional'] = draft['status'] == review['status'] == 'succeeded' and review_done - provisional <= 300
    return result


def pair_times(drafts, review):
    """Måler fra første svar i paret, uansett hvilken modell som leverte det."""
    result = {'first_draft_job_id': None, 'pair_first_draft_s': None,
              'pair_first_provisional_s': None, 'pair_review_total_s': None,
              'review_after_first_draft_s': None, 'review_after_first_provisional_s': None,
              'review_wait_from_both_drafts_s': None,
              'review_within_300s_of_first_draft': False,
              'review_within_300s_of_first_provisional': False}
    started = [job['started_monotonic_s'] for job in drafts if job.get('started_monotonic_s') is not None]
    if not started:
        return result
    pair_start = min(started)
    ready = [(job['started_monotonic_s'] + job['final_content_s'], job['job_id'])
             for job in drafts if job.get('final_content_s') is not None and job['status'] == 'succeeded']
    provisional = [job['started_monotonic_s'] + job['first_provisional_s']
                   for job in drafts if job.get('first_provisional_s') is not None]
    if provisional:
        result['pair_first_provisional_s'] = min(provisional) - pair_start
    if ready:
        first_ready, first_job = min(ready)
        result.update({'first_draft_job_id': first_job, 'pair_first_draft_s': first_ready - pair_start})
    if len(ready) != len(drafts) or review['status'] != 'succeeded' or review.get('final_content_s') is None:
        return result
    review_done = review['started_monotonic_s'] + review['final_content_s']
    after_first = review_done - first_ready
    result.update({'pair_review_total_s': review_done - pair_start,
                   'review_after_first_draft_s': after_first,
                   'review_wait_from_both_drafts_s': review['started_monotonic_s'] - max(time for time, _ in ready),
                   'review_within_300s_of_first_draft': after_first <= 300})
    if provisional:
        after_provisional = review_done - min(provisional)
        result.update({'review_after_first_provisional_s': after_provisional,
                       'review_within_300s_of_first_provisional': after_provisional <= 300})
    return result


def analyze_run(run):
    jobs = []
    for folder in sorted((Path(run) / 'jobs').iterdir()):
        metrics_path = folder / 'metrics.json'
        if not metrics_path.exists():
            continue
        metrics = json.loads(metrics_path.read_text(encoding='utf-8'))
        events_path = folder / 'events.timestamped.jsonl'
        events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines() if line] if events_path.exists() else []
        answer_path = folder / 'answer.txt'
        try:
            answer = json.loads(answer_path.read_text(encoding='utf-8')) if answer_path.exists() else None
        except json.JSONDecodeError:
            answer = None
        jobs.append({**metrics, **content_times(events, answer)})
    by_id = {job['job_id']: job for job in jobs}
    for job in jobs:
        upstream = by_id.get(job.get('review_of_job_id'))
        if upstream:
            job.update(review_times(upstream, job))
            comparison = by_id.get(job.get('compare_with_job_id'))
            if comparison:
                job.update(pair_times([upstream, comparison], job))
    return {'jobs': jobs, 'method': 'Observer-timestamps. Structured summary markers accepted; raw logs unchanged. Actual backend tier is never inferred.'}


def timing_table(data):
    """Viser målinger i en lesbar tabell uten å gjøre dem til kvalitetsdommer."""
    lines = ['# Observerte svartider', '',
             'Sekunder fra faktisk jobbstart. Foreløpig betyr en markert FORELOPIG-melding; ferdig betyr observert sluttinnhold. Tider er ikke kvalitetsgodkjenning.', '',
             '| Jobb | Modell / effort | Forespurt nivå | Observert nivå | Foreløpig | Ferdig | Status |',
             '|---|---|---|---|---:|---:|---|']
    for job in data['jobs']:
        profile = job['requested']
        times = ['—' if job.get(key) is None else f'{job[key]:.1f}'
                 for key in ['first_provisional_s', 'final_content_s']]
        lines.append(f'| {job["job_id"]} | {profile["model"]} / {profile["effort"]} | {profile["service_tier"]} | '
                     f'{job.get("actual_service_tier") or "ukjent"} | {times[0]} | {times[1]} | {job["status"]} |')
    lines += ['', '## Ventetid til sammenlignende kontroll', '',
              'Begge modellstarter og all venting inngår. «Etter Luna» og «etter første utkast» er ulike klokker.', '',
              '| Review | Etter Luna | Etter første utkast | Etter første foreløpige | Hele paret | Under 300 s etter første utkast |',
              '|---|---:|---:|---:|---:|---|']
    for job in data['jobs']:
        if not job.get('compare_with_job_id'):
            continue
        times = ['—' if job.get(key) is None else f'{job[key]:.1f}' for key in
                 ['review_after_draft_s', 'review_after_first_draft_s', 'review_after_first_provisional_s', 'pair_review_total_s']]
        within = 'ja' if job.get('review_within_300s_of_first_draft') else 'nei'
        lines.append(f'| {job["job_id"]} | ' + ' | '.join(times) + f' | {within} |')
    lines += ['', '## Tokenbruk', '',
              'Summerte kall i hver agentjobb; cache er en del av input, og reasoning er en del av output. Dette er ikke en faktura.', '',
              '| Jobb | Input | Cached input | Output | Reasoning output |', '|---|---:|---:|---:|---:|']
    for job in data['jobs']:
        usage = job.get('usage') or {}
        values = [str(usage.get(key, '—')) for key in ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']]
        lines.append(f'| {job["job_id"]} | ' + ' | '.join(values) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--table', type=Path, help='Valgfri Markdown-tabell med tider og tokenbruk.')
    args = parser.parse_args()
    result = analyze_run(args.run)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.table:
        args.table.write_text(timing_table(result), encoding='utf-8')
    print(f'{len(result["jobs"])} ferdige jobber analysert; rålogger uendret.')
