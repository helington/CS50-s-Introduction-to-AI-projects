import nltk
import sys

from nltk.tokenize import word_tokenize

from itertools import islice


TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | VP | S Conj S | Adv S | S Adv

NP -> N | Det NP | Adj NP | P NP | NP P NP
VP -> V | V NP | Adv VP

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Initial tokenization
    tokens = word_tokenize(sentence)

    # Transform all strings in lowercased
    tokens = [word.lower() for word in tokens]

    # Remove non-alphabetical characteres
    tokens = [word for word in tokens if any(char.isalpha() for char in word)]

    return tokens


def is_np_chunk(tree):
    """
    Return True if a Tree is a Noun Phrase Chunk, Otherwise, return false.
    """
    # Check if the label is a Noun Phrase
    if tree.label() == 'NP':

        # Chekc if that NP doens't contains other NP within it
        if all(subtree.label() != 'NP' for subtree in islice(tree.subtrees(), 1, None)):
            return True
    
    return False


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # Initialize NP chunks list
    np_chunks = list()

    # Loop through all subtrees in tree
    for subtree in tree.subtrees():

        # Add subtrees that are NP chunk
        if is_np_chunk(subtree):
            np_chunks.append(subtree)
        
    return np_chunks


if __name__ == "__main__":
    main()
