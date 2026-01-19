import argparse

def main(args):
    linelist = []
    with open(args.file_in, "r") as file_in:
        g = file_in.readlines()
        for line in g:
            line = line.replace('\n', '')
            if line not in linelist:
                linelist.append(line)
        print("{} lines".format(len(g)))
    with open(args.file_in, "w") as file_in:
        for line in linelist:
            file_in.write("{}\n".format(line))
        print("{} lines".format(len(linelist)))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("filter_doubles")
    argparser.add_argument("file_in")
    args = argparser.parse_args()
    main(args)