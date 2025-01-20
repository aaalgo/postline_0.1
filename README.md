Postline: The Ann Arbor Agent Operating System
==============================================

To reproduce:

1. cd into docker, run `docker compose up`.
2. Start the server: `cd postline; ./agents_processor`
3. Start the cnosole: `cd postline; ./console.sh`

To export trace to mbox: `./export_mbox.py ai_30@agents.localdomain >
mbox_file`.

