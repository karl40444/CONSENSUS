# Run CONSENSUS on Windows

This runner administers three-round fixed-comment exercises and saves transcripts.
Substantive marking is still human-reviewed; there is no automatic leaderboard.

## Download and install

Download the ZIP from this pull request's branch using GitHub's **Code** button.
Extract it. Open that folder in Terminal (right-click > Open in Terminal).
Install Python 3.11 or later from python.org if needed. A terminal accepts the
commands below; `py` starts Python and `.venv` keeps project packages separate.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No environment activation or PowerShell execution-policy change is required.

## Free checks first

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe run.py --dry-run
```

This parses both YAML files and saves three public prompts per variant under
`results`. It makes no model calls. Inspect the prompts. Examiner snapshots
contain hidden rules and must never be supplied to the candidate model.

## Connect your model account

API keys authorise paid requests; billing is separate from chat subscriptions.
Enter a key without placing it in command history:

```powershell
$providerKey = Read-Host 'API key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $providerKey).Password
Remove-Variable providerKey
```

For Anthropic replace `OPENAI_API_KEY` with `ANTHROPIC_API_KEY`; for Google use
`GOOGLE_API_KEY`. These settings last for this terminal session only. Never
commit keys. The runner does not load `.env` files.

## One live negotiation

Replace `YOUR_MODEL_ID` with an exact model identifier from your provider account.

```powershell
.\.venv\Scripts\python.exe run.py --models openai/YOUR_MODEL_ID --variants impossible --repeats 1
```

This makes three drafting requests. Review the transcript and provider usage
dashboard before a larger run. The default 4096-token output limit is per
response, not a monetary cap. Change it with `--max-tokens` if responses truncate.
No browsing, tools or judge calls are enabled. Provider default sampling and
reasoning settings apply; Inspect logs record the effective configuration.

## Several models

```powershell
.\.venv\Scripts\python.exe run.py --models openai/YOUR_OPENAI_MODEL anthropic/YOUR_ANTHROPIC_MODEL google/YOUR_GOOGLE_MODEL --variants base impossible --repeats 5
```

This runs 30 negotiations sequentially: 90 drafting responses plus possible
provider retries. Failed runs remain recorded. A nonzero exit code means at
least one failed. Restarting makes a new batch; automatic resume is not provided.

## Read results

Each timestamped batch contains a manifest with model names and scenario hashes,
public prompts, examiner snapshots and a `runs.csv` completion record. Each
run has an Inspect log, a readable Markdown transcript and a blank marking form.
The authoritative record is the Inspect log, including errors and usage.
Completion status is not a diplomatic performance score. Exports include visible
text, not private reasoning. Fill marking forms with evidence quotations.

```powershell
.\.venv\Scripts\inspect.exe view --log-dir results
```

Save your installed versions after setup succeeds:

```powershell
.\.venv\Scripts\python.exe -m pip freeze > results\installed-packages.txt
```

Results, virtual environments and credentials are ignored by Git. No cost
calculation or automatic substantive judge is included in this implementation.
