import nltk
import re
from os import listdir
from os.path import isfile, join
from nltk.tokenize import sent_tokenize

# File path for training data
training_root = 'lib/training/'
# File path for untagged data
untagged_root = 'lib/untagged/'

# List of all files in training
training_files = [f for f in listdir(training_root) if isfile(join(training_root, f))]
# List of all files in untagged
untagged_files = [f for f in listdir(untagged_root) if isfile(join(untagged_root, f))]

# Remove Mac specific file
# Remove empty file from untagged causing an error
untagged_files.remove('485.txt')

def main():
    # create list of emails
    files = []
    for file in untagged_files:
        untagged = nltk.data.load(untagged_root + file)
        files.append(untagged)
    times_files = regex_times(files)
    sentences_files = regex_sentences(times_files)
    paragraph_files = regex_paragraphs(sentences_files)
    speaker_files = tag_speaker(paragraph_files)


def regex_times(untagged):
    times_tagged = []
    for email in untagged:
        # search for time in header
        time_line = re.search(r'Time:\s+(.+)', email)
        # time = the time in header
        time = str(time_line.group(1))

        # regex_time = the matched time
        regex_time = re.findall(r'(\d+:\d+)', time)

        # tag start time
        start_time = regex_time[0]
        tagged = tag_start_time(start_time, email)
        if (len(regex_time) > 1):
            end_time = regex_time[1]
            tagged = tag_end_time(end_time, tagged)
        times_tagged.append(tagged)
    return times_tagged

def regex_sentences(times_tagged):
    sentences_tagged = []
    for email in times_tagged:
        splitting = email.split("Abstract: ")
        body = splitting[1]
        subbed = re.sub(r'(([A-Z][\w, \'()\d\t\n:*-]*)((?!\n\n)[.!?]))', r'<sentence>\2</sentence>\3', body)
        sentences_tagged.append(splitting[0] + "Abstract: " +  subbed)
    return sentences_tagged

def regex_paragraphs(sentences_tagged):
    paragraphs_tagged = []
    for email in sentences_tagged:
        splitting = email.split("Abstract: ")
        body = splitting[1]
        start_subbed = re.sub(r'(<sentence>[A-Z][A-Za-z]*.*)', r'<paragraph>\1', body)
        #  [A-Z].* starting para tag
        #  .*[.!?]\n
        subbed = re.sub(r'(.*</sentence>[.!?])', r'\1</paragraph>', start_subbed)
        paragraphs_tagged.append(subbed)
    return paragraphs_tagged

def tag_start_time(time, email):
    time_split = time.split(':')
    hours = time_split[0]
    minutes = time_split[1]
    subbed = re.sub(r'(' + hours + r':' + minutes + r'(\s?[aApP][mM])?)|\s(' + hours + r'\s?([aApP][mM]))',
                    r'<stime>\1\3</stime>', email)
    return subbed

def tag_end_time(time, email):
    time_split = time.split(':')
    hours = time_split[0]
    minutes = time_split[1]
    subbed = re.sub(r'(' + hours + r':' + minutes + r'(\s?[aApP][mM])?)|(\s' + hours + r'(\s?[aApP][mM]))',
                    r'<etime>\1\3</etime>', email)
    return subbed

def tag_speaker(paragraphs_tagged):
    # Use Regex with common phrases to find potential names
    # Use namesTagger along as part of a brill tagger to find PN
    # extract the names from the tagged_text
    # for each name in the tagged_text check if in names files
    # check if the person can be wikified



