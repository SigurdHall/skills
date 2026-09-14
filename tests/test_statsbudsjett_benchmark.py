import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest


SCRIPT = (
    Path(__file__).parents[1]
    / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/benchmark_models.py"
)


@pytest.fixture
def benchmark():
    spec = importlib.util.spec_from_file_location("statsbudsjett_benchmark", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # En test uten eksplisitt fake skal aldri kunne starte den virkelige klienten.
    module.CODEX_BINARY = str(Path(__file__).parent / "no-real-codex-in-tests")
    return module


@pytest.fixture
def fake_codex(tmp_path, benchmark):
    executable = tmp_path / "fake-codex"
    executable.write_text(
        """#!/opt/az/bin/python3
import json
from pathlib import Path
import sys
import time

args = sys.argv[1:]
prompt = sys.stdin.read()
answer_path = Path(args[args.index('--output-last-message') + 1])
if 'FAIL_AFTER_ANSWER' in prompt:
    answer_path.write_text(json.dumps({'answer': 'unfinished'}), encoding='utf-8')
    print(json.dumps({'type': 'turn.failed'}), flush=True)
    raise SystemExit(7)
if 'FAIL' in prompt:
    print(json.dumps({'type': 'thread.started', 'thread_id': 'failed'}), flush=True)
    print('simulert feil', file=sys.stderr, flush=True)
    raise SystemExit(7)
if 'HANG' in prompt:
    time.sleep(5)
if 'GENERATE A' in prompt:
    time.sleep(0.04)
    answer = {'answer': 'candidate-A'}
elif 'GENERATE B' in prompt:
    time.sleep(0.20)
    answer = {'answer': 'candidate-B'}
elif 'GENERATE C' in prompt:
    answer = {'answer': 'candidate-C'}
elif 'BEGIN CANDIDATE OUTPUT' in prompt:
    answer = {'answer': 'review-complete'}
else:
    answer = {'answer': 'ordinary-answer'}
events = [
    {'type': 'thread.started', 'thread_id': 'test-thread'},
    {'type': 'turn.started'},
    {'type': 'item.completed', 'item': {
        'type': 'tool_call', 'result': {'service_tier': 'model-invented'}}},
    {'type': 'item.completed', 'item': {
        'id': 'item-1', 'type': 'agent_message',
        'text': 'FORELOPIG: første nyttige vurdering'}},
    {'type': 'turn.completed', 'usage': {
        'input_tokens': 101, 'cached_input_tokens': 11,
        'output_tokens': 23, 'reasoning_output_tokens': 7}},
]
if 'WARN' in prompt:
    events.insert(3, {'type': 'item.completed', 'item': {
        'type': 'error', 'message': 'Skill descriptions were shortened'}})
for event in events:
    print(json.dumps(event), flush=True)
    time.sleep(0.005)
answer_path.write_text(json.dumps(answer), encoding='utf-8')
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    benchmark.CODEX_BINARY = str(executable)
    return executable


def write_suite(tmp_path, jobs):
    inputs = tmp_path / "case-inputs"
    inputs.mkdir()
    (inputs / "source.txt").write_text("blind input", encoding="utf-8")
    schema = tmp_path / "answer.schema.json"
    schema.write_text(
        json.dumps({"type": "object", "additionalProperties": True}),
        encoding="utf-8",
    )
    for job in jobs:
        prompt_file = tmp_path / job.pop("prompt_text", f"{job['id']}.txt")
        prompt_file.write_text(job.pop("prompt", "ANALYSE"), encoding="utf-8")
        job.setdefault("inputs_dir", inputs.name)
        job.setdefault("prompt_file", prompt_file.name)
        job.setdefault("schema_file", schema.name)
        job.setdefault("model", "gpt-5.6-luna")
        job.setdefault("effort", "max")
        job.setdefault("service_tier", "priority")
        job.setdefault("repeat", 1)
    suite = tmp_path / "suite.json"
    suite.write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
    return suite


def test_run_records_command_events_usage_and_isolated_inputs(
    tmp_path, benchmark, fake_codex
):
    suite = write_suite(tmp_path, [{"id": "luna", "case_id": "case-1"}])
    output = tmp_path / "results"

    summary = benchmark.run_suite(suite, output, max_parallel=3)

    metrics = summary["jobs"][0]
    job_dir = output / "jobs/luna"
    assert metrics["status"] == "succeeded"
    assert metrics["requested"] == {
        "model": "gpt-5.6-luna",
        "effort": "max",
        "service_tier": "priority",
        "fast_mode": True,
    }
    assert metrics["actual_service_tier"] is None
    assert metrics["usage"] == {
        "input_tokens": 101,
        "cached_input_tokens": 11,
        "output_tokens": 23,
        "reasoning_output_tokens": 7,
    }
    command = metrics["command"]
    assert command[:5] == [
        str(fake_codex),
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-user-config",
    ]
    assert command[command.index("-C") + 1] == str(job_dir.resolve())
    assert command[command.index("-s") + 1] == "read-only"
    assert 'model_reasoning_effort="max"' in command
    assert 'service_tier="priority"' in command
    assert command[-1] == "-"
    assert (job_dir / "input/source.txt").read_text() == "blind input"
    assert not (job_dir / "input/source.txt").is_symlink()
    assert json.loads((job_dir / "answer.txt").read_text()) == {"answer": "ordinary-answer"}
    raw_lines = (job_dir / "stdout.jsonl").read_text().splitlines()
    timestamped = [
        json.loads(line)
        for line in (job_dir / "events.timestamped.jsonl").read_text().splitlines()
    ]
    assert len(raw_lines) == len(timestamped) == 5
    assert all("received_at_utc" in record for record in timestamped)
    assert all(record["elapsed_s"] >= 0 for record in timestamped)
    assert metrics["first_event_elapsed_s"] <= metrics["first_agent_text_elapsed_s"]
    assert metrics["first_agent_text_elapsed_s"] == metrics["first_useful_elapsed_s"]
    assert metrics["first_useful_within_300s"] is True
    assert metrics["completed_within_300s"] is True
    assert metrics["queued_at_utc"]
    assert metrics["ready_at_utc"]
    assert metrics["started_at_utc"]
    assert metrics["ended_at_utc"]
    assert json.loads((output / "results.json").read_text()) == summary
    csv_text = (output / "results.csv").read_text()
    assert "actual_service_tier" in csv_text
    assert "null" in csv_text


def test_reserves_capacity_for_review_instead_of_filling_with_generation(tmp_path, benchmark, fake_codex):
    jobs = [
        {'id':'gen-a','case_id':'a','prompt':'GENERATE A'},
        {'id':'gen-b','case_id':'b','prompt':'GENERATE B'},
        {'id':'review-a','case_id':'a','prompt':'REVIEW','review_of':'gen-a','model':'gpt-5.6-sol','effort':'high'},
    ]
    suite = write_suite(tmp_path, jobs)
    config = json.loads(suite.read_text())
    config['max_active_generations'] = 1
    suite.write_text(json.dumps(config))
    result = benchmark.run_suite(suite, tmp_path / 'out', max_parallel=2)
    by_id = {job['job_id']:job for job in result['jobs']}
    assert by_id['gen-b']['started_monotonic_s'] >= by_id['gen-a']['started_monotonic_s'] + by_id['gen-a']['process_exit_elapsed_s']
    assert by_id['review-a']['started_monotonic_s'] < by_id['gen-b']['started_monotonic_s'] + by_id['gen-b']['process_exit_elapsed_s']


def test_structured_provisional_message_is_timed(benchmark):
    observations = benchmark.initial_observations()
    event = {'type':'item.completed','item':{'type':'agent_message','text':json.dumps({'summary':'FORELOPIG: Kilden bekrefter beløpet','facts':[]})}}
    benchmark.inspect_event(event, 14.2, observations)
    assert observations['first_useful_elapsed_s'] == 14.2


def test_comparison_review_waits_for_both_independent_answers(tmp_path, benchmark, fake_codex):
    jobs = [
        {'id':'luna','case_id':'a','prompt':'GENERATE A'},
        {'id':'sol','case_id':'a','prompt':'GENERATE B','model':'gpt-5.6-sol','effort':'high'},
        {'id':'review','case_id':'a','prompt':'REVIEW','review_of':'luna','compare_with':'sol','model':'gpt-5.6-sol','effort':'high'},
    ]
    suite = write_suite(tmp_path, jobs)
    result = benchmark.run_suite(suite, tmp_path/'out', max_parallel=3)
    by_id = {job['job_id']:job for job in result['jobs']}
    assert by_id['review']['started_monotonic_s'] >= by_id['sol']['started_monotonic_s'] + by_id['sol']['process_exit_elapsed_s']
    prompt = (tmp_path/'out/jobs/review/prompt.txt').read_text()
    assert 'candidate-A' in prompt and 'candidate-B' in prompt


def test_review_uses_actual_answer_and_is_prioritized_over_waiting_generation(
    tmp_path, benchmark, fake_codex
):
    jobs = [
        {"id": "gen-a", "case_id": "a", "prompt": "GENERATE A"},
        {"id": "gen-b", "case_id": "b", "prompt": "GENERATE B"},
        {"id": "gen-c", "case_id": "c", "prompt": "GENERATE C"},
        {
            "id": "review-a",
            "case_id": "a",
            "prompt": "REVIEW",
            "model": "gpt-5.6-sol",
            "effort": "high",
            "review_of": "gen-a",
        },
    ]
    suite = write_suite(tmp_path, jobs)
    output = tmp_path / "results"

    summary = benchmark.run_suite(suite, output, max_parallel=2)

    by_id = {job["job_id"]: job for job in summary["jobs"]}
    assert by_id["review-a"]["status"] == "succeeded"
    assert by_id["review-a"]["started_monotonic_s"] < by_id["gen-c"]["started_monotonic_s"]
    assert by_id["review-a"]["review_of_job_id"] == "gen-a"
    assert by_id["review-a"]["review_age_s"] >= 0
    review_prompt = (output / "jobs/review-a/prompt.txt").read_text()
    assert "Kontroller kandidatens fakta mot originalkildene i input/" in review_prompt
    assert "samme output.schema.json" in review_prompt
    assert "Bevar fakta" in review_prompt
    assert "changes" in review_prompt
    assert "BEGIN CANDIDATE OUTPUT" in review_prompt
    assert "candidate-A" in review_prompt
    assert "END CANDIDATE OUTPUT" in review_prompt


def test_repeat_fans_out_and_pairs_review_with_matching_upstream_repeat(
    tmp_path, benchmark, fake_codex
):
    suite = write_suite(
        tmp_path,
        [
            {"id": "luna", "case_id": "one", "repeat": 2},
            {
                "id": "sol-review",
                "case_id": "one",
                "model": "gpt-5.6-sol",
                "effort": "high",
                "repeat": 2,
                "review_of": "luna",
            },
        ],
    )

    summary = benchmark.run_suite(suite, tmp_path / "results", max_parallel=3)

    by_id = {job["job_id"]: job for job in summary["jobs"]}
    assert set(by_id) == {"luna-r01", "luna-r02", "sol-review-r01", "sol-review-r02"}
    assert by_id["sol-review-r01"]["review_of_job_id"] == "luna-r01"
    assert by_id["sol-review-r02"]["review_of_job_id"] == "luna-r02"
    assert all(job["status"] == "succeeded" for job in by_id.values())


def test_failed_dependency_skips_review_and_writes_visible_artifacts(
    tmp_path, benchmark, fake_codex
):
    suite = write_suite(
        tmp_path,
        [
            {"id": "failed", "case_id": "one", "prompt": "FAIL"},
            {
                "id": "review",
                "case_id": "one",
                "prompt": "REVIEW",
                "review_of": "failed",
            },
        ],
    )

    summary = benchmark.run_suite(suite, tmp_path / "results", max_parallel=2)

    by_id = {job["job_id"]: job for job in summary["jobs"]}
    assert by_id["failed"]["status"] == "failed"
    assert by_id["failed"]["exit_code"] == 7
    assert by_id["review"]["status"] == "skipped_dependency_failed"
    assert "failed" in by_id["review"]["skip_reason"]
    review_dir = tmp_path / "results/jobs/review"
    assert (review_dir / "metrics.json").exists()
    assert (review_dir / "answer.txt").read_text() == ""
    assert (review_dir / "stdout.jsonl").read_text() == ""


def test_timeout_is_a_failure_and_never_a_pass(tmp_path, benchmark, fake_codex):
    suite = write_suite(
        tmp_path,
        [{"id": "hung", "case_id": "one", "prompt": "HANG", "timeout_s": 0.05}],
    )

    summary = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)

    metrics = summary["jobs"][0]
    assert metrics["status"] == "failed"
    assert metrics["timed_out"] is True
    assert metrics["timeout_s"] == 0.05
    assert metrics["first_useful_within_300s"] is False


def test_failed_process_with_answer_never_counts_as_completed(tmp_path, benchmark, fake_codex):
    suite = write_suite(
        tmp_path,
        [{"id": "failed-after-answer", "case_id": "one", "prompt": "FAIL_AFTER_ANSWER"}],
    )
    result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
    metrics = result["jobs"][0]
    assert metrics["status"] == "failed"
    assert metrics["exit_code"] == 7
    assert metrics["turn_failed"] is True
    assert metrics["completed_within_300s"] is False


def test_timeout_also_bounds_sending_a_large_prompt(tmp_path, benchmark):
    executable = tmp_path / "never-reads-stdin"
    executable.write_text("#!/opt/az/bin/python3\nimport time\ntime.sleep(2)\n")
    executable.chmod(0o755)
    benchmark.CODEX_BINARY = str(executable)
    suite = write_suite(
        tmp_path,
        [{"id": "stdin-blocked", "case_id": "one", "prompt": "x" * 1000000, "timeout_s": 0.05}],
    )
    started = time.monotonic()
    result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
    elapsed = time.monotonic() - started
    assert result["jobs"][0]["timed_out"] is True
    assert result["jobs"][0]["status"] == "failed"
    assert elapsed < 1


def test_truncated_prompt_is_a_failure_even_with_zero_exit_and_answer(tmp_path, benchmark):
    executable = tmp_path / "reads-only-one-character"
    executable.write_text(
        "#!/opt/az/bin/python3\n"
        "import json, sys\nfrom pathlib import Path\n"
        "sys.stdin.read(1)\n"
        "answer = Path(sys.argv[sys.argv.index('--output-last-message') + 1])\n"
        "answer.write_text(json.dumps({'answer':'incomplete input'}))\n"
        "print(json.dumps({'type':'turn.completed'}), flush=True)\n"
    )
    executable.chmod(0o755)
    benchmark.CODEX_BINARY = str(executable)
    suite = write_suite(
        tmp_path,
        [{"id": "truncated", "case_id": "one", "prompt": "x" * 1000000}],
    )
    result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
    metrics = result["jobs"][0]
    assert metrics["exit_code"] == 0
    assert metrics["status"] == "failed"
    assert metrics["completed_within_300s"] is False
    assert "prompten" in metrics["error"]


def test_cleanup_timeout_fails_only_its_job_and_suite_continues(
    tmp_path, benchmark, fake_codex, monkeypatch
):
    original_cleanup = benchmark.stop_process_group
    calls = []

    def cleanup_timeout_once(process):
        result = original_cleanup(process)
        calls.append(process.pid)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired("synthetic cleanup", 0.01)
        return result

    monkeypatch.setattr(benchmark, "stop_process_group", cleanup_timeout_once)
    suite = write_suite(tmp_path, [{"id": "first", "case_id": "one"}, {"id": "second", "case_id": "one"}])
    result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
    first, second = result["jobs"]
    assert first["status"] == "failed"
    assert "opprydding" in first["error"]
    assert first["completed_within_300s"] is False
    assert second["status"] == "succeeded"
    assert (tmp_path / "results/results.json").exists()


def test_later_io_failure_cleans_up_process_and_suite_continues(
    tmp_path, benchmark, fake_codex, monkeypatch
):
    original_popen = benchmark.subprocess.Popen
    original_finish = benchmark.finish_process
    processes = []

    def record_process(*args, **kwargs):
        process = original_popen(*args, **kwargs)
        processes.append(process)
        return process

    def io_failure_once(process, timeout_s, started_monotonic):
        if len(processes) == 1:
            raise OSError("syntetisk I/O-feil etter oppstart")
        return original_finish(process, timeout_s, started_monotonic)

    monkeypatch.setattr(benchmark.subprocess, "Popen", record_process)
    monkeypatch.setattr(benchmark, "finish_process", io_failure_once)
    suite = write_suite(tmp_path, [{"id": "first", "case_id": "one", "prompt": "HANG"},
                                  {"id": "second", "case_id": "one"}])
    try:
        result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
        first, second = result["jobs"]
        assert all(process.poll() is not None for process in processes)
        assert first["status"] == "failed"
        assert "kjøring" in first["error"]
        assert "starte Codex" not in first["error"]
        assert second["status"] == "succeeded"
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)


@pytest.mark.parametrize("reader_name", ["read_stdout", "read_stderr"])
def test_stream_thread_error_fails_its_job_and_suite_continues(
    tmp_path, benchmark, fake_codex, monkeypatch, reader_name
):
    original_reader = getattr(benchmark, reader_name)
    calls = []

    def fail_reader_once(*args):
        calls.append(reader_name)
        if len(calls) == 1:
            raise OSError("syntetisk feil i lagring av prosesstrøm")
        return original_reader(*args)

    monkeypatch.setattr(benchmark, reader_name, fail_reader_once)
    suite = write_suite(tmp_path, [{"id": "first", "case_id": "one"}, {"id": "second", "case_id": "one"}])
    result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
    first, second = result["jobs"]
    assert first["exit_code"] == 0
    assert first["status"] == "failed"
    assert first["completed_within_300s"] is False
    assert "I/O" in first["error"]
    assert second["status"] == "succeeded"


@pytest.mark.parametrize("parent_exits", [False, True])
def test_cleanup_stops_own_descendant_holding_stdout_but_not_other_processes(
    tmp_path, benchmark, parent_exits
):
    executable = tmp_path / "starts-child"
    child_code = (
        "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "print('child_ready', flush=True); time.sleep(2)"
    )
    executable.write_text(
        "#!/opt/az/bin/python3\n"
        "import subprocess, sys, time\n"
        f"subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
        + ("time.sleep(0.1)\n" if parent_exits else "time.sleep(2)\n")
    )
    executable.chmod(0o755)
    benchmark.CODEX_BINARY = str(executable)
    timeout_s = 1 if parent_exits else 0.15
    suite = write_suite(
        tmp_path,
        [{"id": "descendant", "case_id": "one", "timeout_s": timeout_s}],
    )
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"])
    try:
        started = time.monotonic()
        result = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)
        elapsed = time.monotonic() - started
        assert unrelated.poll() is None
        assert result["jobs"][0]["timed_out"] is (not parent_exits)
        assert elapsed < 1
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


@pytest.mark.parametrize("answer", [None, [], False, 42, "text"])
def test_non_object_json_is_not_a_valid_answer(tmp_path, benchmark, answer):
    path = tmp_path / "answer.txt"
    path.write_text(json.dumps(answer), encoding="utf-8")
    valid, error = benchmark.valid_answer(path)
    assert valid is False
    assert "JSON-objekt" in error


def test_expanded_job_id_collision_is_rejected_before_output(tmp_path, benchmark, fake_codex):
    suite = write_suite(
        tmp_path,
        [{"id": "draft", "case_id": "one", "repeat": 2},
         {"id": "draft-r01", "case_id": "one"}],
    )
    output = tmp_path / "results"
    with pytest.raises(ValueError, match="utvidede jobb-id"):
        benchmark.run_suite(suite, output)
    assert not output.exists()


def test_agent_item_error_is_a_warning_when_answer_and_turn_succeed(
    tmp_path, benchmark, fake_codex
):
    suite = write_suite(
        tmp_path,
        [{"id": "warning", "case_id": "one", "prompt": "WARN"}],
    )

    summary = benchmark.run_suite(suite, tmp_path / "results", max_parallel=1)

    metrics = summary["jobs"][0]
    assert metrics["status"] == "succeeded"
    assert metrics["warnings"][0]["type"] == "agent_item_error"


def test_only_provider_response_envelope_can_set_actual_service_tier(benchmark):
    observations = benchmark.initial_observations()
    benchmark.inspect_event(
        {"type": "item.completed", "item": {"service_tier": "invented"}},
        1.0,
        observations,
    )
    assert observations["actual_service_tier"] is None

    benchmark.inspect_event(
        {"type": "response.completed", "response": {"service_tier": "priority"}},
        2.0,
        observations,
    )
    assert observations["actual_service_tier"] == "priority"


@pytest.mark.parametrize(
    "change, message",
    [
        ({"repeat": 0}, "repeat"),
        ({"inputs_dir": "../outside"}, "relativ"),
        ({"id": "../unsafe"}, "jobb-id"),
        ({"review_of": "missing"}, "review_of"),
    ],
)
def test_invalid_suite_is_rejected_before_output(
    tmp_path, benchmark, fake_codex, change, message
):
    job = {"id": "job", "case_id": "one", **change}
    suite = write_suite(tmp_path, [job])
    output = tmp_path / "results"

    with pytest.raises(ValueError, match=message):
        benchmark.run_suite(suite, output)

    assert not output.exists()
