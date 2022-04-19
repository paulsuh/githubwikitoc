from os import chdir
import githubwikitoc


if __name__ == "__main__":

    chdir( "../wikitemp/wikitest.wiki" )

    # print(githubwikitoc.scan_files())
    githubwikitoc.generate_toc()