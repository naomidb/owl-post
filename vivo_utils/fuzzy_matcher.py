from vivo_queries import name_cleaner

def compare(original, other):
    # clean all special characters and lowercase everything
    title = full_clean(original.lower())
    alt = full_clean(other.lower())

    # break down titles into lists of words
    title_words = title.split(' ')
    title_length = len(title_words)

    alt_words = alt.split(' ')
    alt_length = len(alt_words)

    # check how many vivo words in other
    match_count = 0
    for word in title_words:
        if word in alt_words:
            match_count += 1

    # formula
    match_num = (match_count/(abs(alt_length - title_length) + 1)) * (1/title_length)