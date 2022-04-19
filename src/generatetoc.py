import sys
from os import chdir
from src import githubwikitoc

if __name__ == "__main__":

    chdir( sys.argv[1] )

    # print(githubwikitoc.scan_files())
    githubwikitoc.generate_toc()
