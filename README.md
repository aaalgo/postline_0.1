Postline 0.1
============
Wei Dong
wdong@aaalgo.com

This is an early version of Postline used to produce the experimental results
reported in the Postline paper. The architecture is very different from the one
presented in the paper.

The full Postline system code is available for licensing to collaborators, with
trial accounts also offered. Please contact the author if you are
interested.


To reproduce:

`pip install pika openai`

1. cd into docker, run `docker compose up`.
2. Start the server: `cd postline; ./agents_processor`
3. Start the cnosole: `cd postline; ./console.sh`
   By default you talk to `ai_30`.  Modify `console.sh` to select a
   different agent.

To export trace to mbox: `./export_mbox.py ai_30@agents.localdomain >
mbox_file`.

Some conversation logs are provided:

- `log/ai_30_transcript.txt`: initial experiments.
- `log/msr-{before,after}.txt`: MSR experiments.
