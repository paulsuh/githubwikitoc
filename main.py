from os import chdir
import wikitoc


if __name__ == "__main__":

    chdir( "../wikitemp/wikitest.wiki" )

    # print(wikitoc.scan_files("../wikitemp/wikitest.wiki"))
    wikitoc.generate_toc()