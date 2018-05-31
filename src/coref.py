from pynlp import StanfordCoreNLP
import anaphora

print("+---------------- N.A.R.U.T.O. Module ---------------------+")
print("|                                                          |")
print("| Performing Natural Anaphoric Resolution Understanding... |")
print("|                                                          |")

# text = "This is a sentence. It is good. Please resolve it."

# openfile = open(PATH/TO/PLAIN/TEXT/FILE)
# text = openfile.read()

anaphora_data = anaphora.res(text)

print("|                                                          |")
print("| ------------------ Coreference Chains -------------------|")
print("|                                                          |")

count = 0
for s in anaphora_data[0]:
    count += 1

    print("[", count, "] ---------------------\n\n")

    for sentence in s:
        print(sentence)

print("|                                                          |")
print("| Terminating  Module...                                   |")
print("|                                                          |")
print("+---------------- N.A.R.U.T.O. Module ---------------------+")
