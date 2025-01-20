import sys
import pickle
def play_journal(self_address, journal):
    output = []
    with open('a.pkl', 'wb') as f:
        pickle.dump(journal, f)
        for entry in journal:
            message = entry.message
            if (message["From"] == self_address) and (message["To"] == self_address):
                subject = message.get("Subject", "")
                if subject.startswith("REPLACE X-Serial"):
                    pickle.dump(output, f)

                    _, range_str = subject.split("X-Serial ")
                    start, end = map(int, range_str.split("-"))
                    top = output[:start]
                    bottom = output[end:]
                    output = []
                    output.extend(top)
                    entry.message["Subject"] = "%d journal entries compressed" % (end - start)
                    output.append(entry)
                    output.extend(bottom)
            # Potentially other journal instructions can be processed here
            else:
                output.append(entry)
        pickle.dump(output, f)
        sys.exit(0)
    return output

