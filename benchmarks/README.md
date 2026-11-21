# Security benchmark gateway (CyberChainBench + ReEVMBench)

Both upstream case datasets are selectable through **one manual GitHub Actions workflow**:
`Actions → Security benchmark gateway → Run workflow`.
There are no scheduled runs, no automatic model calls, and no paid RPC/API provisioning.

## Usage

- CyberChainBench: `source=cyberchainbench`, `case_id=bench-01`.
- ReEVMBench: `source=reevmbench`, `case_id=2023-07-pooltogether`.
- `operation=prepare`, `phase=detect`: emits a **sanitized** `brief.json` in a downloadable Actions artifact. Give only this brief to Freebuff V7.
- ReEVMBench: retrieve the target repository at `source_commit`, *not* the benchmark's audit config containing findings. CyberChainBench: retrieve verified contract sources from the indicated chain/address; an explorer API may be needed.
- Freebuff should freeze its findings and reproducible evidence before any evaluation. Submission JSON shape: `{"findings":[{"type":"...","function":"...","finding_id":"...","evidence_path":"..."}],"notes":"..."}`.
- To make an **indicative post-freeze label comparison**, put the frozen report as JSON in `benchmarks/submissions/` via a reviewed PR. Then run `operation=grade`, `submission=filename.json`. The evaluator fetches upstream ground truth at this later phase; it does not execute an exploit.
- `phase=reproduce` makes historical block information available if applicable, but never the known attack transactions. For actual historical fork replay, an archival RPC and a separate Foundry execution environment are necessary; neither is silently provisioned.

## Provenance

`sources.json` pins both upstream public datasets to specific commits, not moving `main`. Updates require deliberate review.

## Limits and safeguards

- **Not perfectly blind:** Public case datasets and incident reports are accessible on the internet. This gateway prevents *accidental* answer leakage by omitting incident names, affected functions, vulnerability classes, fix descriptions, attack transactions, and reference finding IDs. It cannot prevent a Freebuff agent with unrestricted web access from seeking solutions.
- **No official benchmark score:** CyberChainBench grade compares type plus function, ReEVMBench grade compares finding IDs. These are preliminary metadata checks, not validated exploitability, benchmark leaderboard scores or full official Harbor/EVMbench evaluations.
- **Freebuff executes outside GitHub Actions.** The workflow prepares its input and checks a submitted answer; it does not run the Freebuff desktop agent.
- No third-party Dockerfiles or submitted Solidity code are executed by this Actions workflow. No SSH, Tailscale, system services, account skills or existing `~/ctf-skills/` resources are modified.
- Actions has `workflow_dispatch` only. No runs are started by the commit; manual runs consume the account's applicable Actions minutes. The upstream raw-content endpoint can rate-limit.
- Mind benchmark case data redistribution licenses; CyberChainBench's data includes AGPL-3.0-derived cases.

## Test

`python3 -m unittest discover -s benchmarks/tests -v`
