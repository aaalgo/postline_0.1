Postline 0.1
============
Wei Dong
wdong@aaalgo.com

This is an early version of Postline used in the experiments reported
in the paper.

To reproduce:

`pip install pika openai`

1. cd into docker, run `docker compose up`.
2. Start the server: `cd postline; ./agents_processor`
3. Start the cnosole: `cd postline; ./console.sh`
   By default you talk to `ai_30`.  Modify `console.sh` to select a
   different agent.

To export trace to mbox: `./export_mbox.py ai_30@agents.localdomain >
mbox_file`.

