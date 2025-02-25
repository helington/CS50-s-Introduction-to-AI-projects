import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # The pages that have links with the current page
    linked_pages = corpus[page]

    # Define a variable for the number of total pages
    total_pages = len(corpus)

    probability_distribution = dict()
    # If the pages hasn's links
    if not linked_pages:
        # The probablity is equal for every
        probability_of_all = 1 / total_pages
        probability_distribution = {key: probability_of_all for key in corpus}
    
    else:
        # Aplicate the damping factor formula
        random_probability = (1 - damping_factor) / (total_pages)
        linked_probability = (damping_factor / len(linked_pages) + random_probability)

        probability_distribution = {
            key: linked_probability if key in linked_pages else random_probability 
            for key in corpus
        }

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {page: 0 for page in corpus}
    sample = None

    # Getting the samples
    for i in range(n):
        # If its the first sample
        if sample is None:
            # Choices the page randomly
            sample = random.choice(list(corpus.keys()))
        else:
            # Next sample will be generate based from the current sample
            model = transition_model(corpus, sample, damping_factor)
            pages = list(model.keys())
            weights = list(model.values())
            sample = random.choices(pages, weights=weights, k=1)[0]
        
        pagerank[sample] += 1
    
    # Get the propabilities
    for page in pagerank:
        pagerank[page] /= n
    
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    total_pages = len(corpus)
    pagerank = {page: 1 / total_pages for page in corpus}

    tolerance = 0.001

    while True:
        new_pagerank = dict()
        # Calculate new rank values based on all of the current rank values
        for page in pagerank:
            rank = (1 - damping_factor)/total_pages
            i = 0

            for p in corpus:
                # Considering i as all pages that link to page p
                if page in corpus[p] and corpus[p]:  
                    i += pagerank[p] / len(corpus[p])

                # If i hasn't links we consider it as having one link for every pages
                elif not corpus[p]:
                    i += pagerank[p] / total_pages

            iterative_algorithm = rank + damping_factor * i
            new_pagerank[page] = iterative_algorithm
        
        # If all values changes by less than the tolerance, break the loop 
        if all(abs(new_pagerank[p] - pagerank[p]) < tolerance for p in pagerank):
            break

        pagerank = new_pagerank

    return pagerank


if __name__ == "__main__":
    main()
