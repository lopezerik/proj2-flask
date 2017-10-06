"""
Pre-process a syllabus (class schedule) file. 

"""
import arrow   # Dates and times
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

base = arrow.now()   # Default, replaced if file has 'begin: ...'
weekBeginnings = []  # holds week beginning dates


def process(raw):
    """
    Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  If # is the first
    non-blank character on a line, it is a comment ad skipped. 
    """
    field = None
    entry = {}
    cooked = []
    for line in raw:
        log.debug("Line: {}".format(line))
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            log.debug("Skipping")
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + line + " "
            continue
        if len(parts) == 2:
            field = parts[0]
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) +
                             "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                base = arrow.get(content, "MM/DD/YYYY")
            except:
                raise ValueError("Unable to parse date {}".format(content))

        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = {}
            entry['topic'] = ""
            entry['project'] = ""
            entry['week'] = "Week\n" + content
            factor = int(content) - 1	# calculates factor to multiply week start date
            week = base.replace(days=(7*factor))    # begining of certain week
            weekBeginnings.append( week)     #add to a list of week beginnings
            weekBegin = base.replace(days=(7*factor)).format("MM/DD")   # format for schedule
            entry['start'] = "Week of\n" + weekBegin    # added a new entry for schedule
        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    if entry:
        cooked.append(entry)
    return cooked

# Determines whether it is the current week or not
def currWeek():
    today = arrow.now()
    today.format('MM/DD')
    i = 0
    # loop until we find what week we're in
    while( i < len(weekBeginnings)):
        beginning = arrow.get(weekBeginnings[i])
	
        endOfWeek = beginning.replace(days=7)
        if(beginning <= today <= endOfWeek):
            return (i + 1)
        i+=1
    return 0

def main():
    f = open("data/schedule.txt")
    parsed = process(f)
    print(parsed)


if __name__ == "__main__":
    main()
