import sys
import pickle
from postline import Message, Entry
def play_journal(self_address, journal):
    output = []
    for entry in journal:
        message = entry.message
        if message["To"] == 'system@localdomain':
            subject = message.get("Subject", "")
            if subject.startswith("MSR "):
                _, range_str = subject.split(" ")
                start, end = map(int, range_str.split("-"))
                print(start, end)
                top = [a for a in output[:start]]
                bottom = [a for a in output[(end+1):]]
                output = []
                output.extend(top)
                entry.message.replace_header("Subject", "%d entries rewritten" % (end - start+1))
                output.append(entry)
                output.extend(bottom)
            else:
                assert False
        else:
            output.append(entry)
    return output

