import sys
import pickle
def play_journal(self_address, journal):
    output = []
    for entry in journal:
        message = entry.message
        if (message["From"] == self_address) and (message["To"] == self_address):
            subject = message.get("Subject", "")
            if subject.startswith("REPLACE X-Serial"):
                _, range_str = subject.split("X-Serial ")
                start, end = map(int, range_str.split("-"))
                print(start, end)
                top = [a for a in output[:start]]
                bottom = [a for a in output[end:]]
                output = []
                output.extend(top)
                entry.message.replace_header("Subject", "%d journal entries compressed" % (end - start))
                output.append(entry)
                output.extend(bottom)
                entry.message.replace_header("Subject", "memory compression done %d-%d" % (start, end))
                entry.message.replace_content("")
                output.append(entry)
        # Potentially other journal instructions can be processed here
        else:
            output.append(entry)
    return output

