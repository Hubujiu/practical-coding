#!/usr/bin/env python3
"""Measure prompt size and independent oracle controls; never fabricate LLM rows."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))
import delivery_cases
from test_delivery_cases import SOLUTIONS
from retrieval_integrity import source_files

ROOT = HERE.parent
BASELINE = "6cf43d758d6f99aa051153edea67d5ac533acfe7"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-root', type=Path, help='optional offline exact source snapshot')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    paths = ['SKILL.md', 'AGENTS.md', 'agents/openai.yaml',
             *[str(path.relative_to(ROOT)).replace('\\','/') for path in sorted((ROOT/'references').rglob('*.md'))]]
    sizes = {}
    for name in paths:
        if args.baseline_root:
            before = (args.baseline_root/name).read_bytes()
        else:
            before = subprocess.run(['git','show',f'{BASELINE}:{name}'], cwd=ROOT, capture_output=True, check=True).stdout
        after = (ROOT/name).read_bytes()
        sizes[name] = {'before_bytes':len(before), 'after_bytes':len(after),
                       'before_sha256':hashlib.sha256(before).hexdigest(), 'after_sha256':hashlib.sha256(after).hexdigest(),
                       'reduction_percent':round((1-len(after)/len(before))*100, 2) if before else None}
    controls = []
    for item in delivery_cases.CASES:
        with tempfile.TemporaryDirectory(prefix='oracle-control-') as directory:
            workspace = Path(directory)/'work'
            delivery_cases.prepare_workspace(workspace, item)
            original = delivery_cases.score_workspace(workspace, item)
            (workspace/item['filename']).write_text(SOLUTIONS[item['task_id']], encoding='utf-8')
            fixed = delivery_cases.score_workspace(workspace, item)
            controls.append({'task_id':item['task_id'], 'original_bug_rejected':original['passed'] is False,
                             'reference_fix_accepted':fixed['passed'] is True, 'reference_checks':fixed['oracle_checks']})
    before = sum(row['before_bytes'] for row in sizes.values())
    after = sum(row['after_bytes'] for row in sizes.values())
    report = {'benchmark_kind':'deterministic-readiness-controls', 'model_executed':False,
              'baseline_ref':BASELINE, 'baseline_source':'offline-snapshot' if args.baseline_root else 'git-object',
              'candidate_sources':source_files(ROOT), 'prompt_bytes':sizes,
              'prompt_bundle':{'before_bytes':before,'after_bytes':after,'reduction_percent':round((1-after/before)*100,2)},
              'oracle_controls':controls,
              'oracle_control_passes':sum(row['original_bug_rejected'] and row['reference_fix_accepted'] for row in controls),
              'oracle_control_tasks':len(controls),
              'environment':{'python':sys.version.split()[0], 'binaries_available':{name:shutil.which(name) is not None
                              for name in ('codex','zg','codebase-memory-mcp','rtk','git','python','node','npm','mvn')}},
              'model_measurements':None,
              'limitations':'Static UTF-8 bytes are not token costs. Oracle controls are reference programs, not agent solutions. No external providers or model are simulated as benchmark results.'}
    value = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(value, encoding='utf-8')
    print(value, end='')
    return 0 if report['oracle_control_passes'] == report['oracle_control_tasks'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
