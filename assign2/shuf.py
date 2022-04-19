#!/usr/bin/python3
import argparse, random

def randomize(collection):
    random.shuffle(collection)

def printRList(collection, n=-1):
    if collection is None or len(collection) == 0:
        raise Exception("shuf: no lines to repeat")
    while n > 0:
        print(random.choice(collection))
        n -= 1
    if n == -1:
        while True:
            print(random.choice(collection))

def printList(collection):
    for i in collection:
        print(i)

def printNList(collection, n):
    for i in range(n):
        if i < len(collection):
            print(collection[i])

def parseRange(itemRange, bounds):
    errMsg = "shuf: invalid input range: '" + itemRange + "'";
    if not(itemRange[0].isdigit() and itemRange[len(itemRange)-1].isdigit()):
        raise Exception(errMsg)
    start = '';
    end = '';
    delimited = False;
    for i in range(len(itemRange)):
        if itemRange[i] == '-':
            if not delimited:
                delimited = True
                continue
            else:
                raise Exception(errMsg)

        if itemRange[i].isdigit() and not delimited:
            start += itemRange[i]
            continue
        elif itemRange[i].isdigit() and delimited:
            end += itemRange[i]
            continue
        else:
            raise Exception(errMsg)
    if not delimited:
        raise Exception(errMsg)
    bounds[0] = int(start)
    bounds[1] = int(end)

def main():
    parser = argparse.ArgumentParser(description='generate random permutations')
    parser.add_argument('-e', '--echo', default=argparse.SUPPRESS, dest='itemList', nargs='*',
                        help = 'treat each ARG as an input line')
    parser.add_argument('-i', '--input-range', default=argparse.SUPPRESS, dest='itemRange', type=str,
                        help = 'treat each number LO through HI as an  input line')
    parser.add_argument('-n', '--head-count', default=argparse.SUPPRESS, dest='headCount', type=int,
                        help = 'output at most COUNT lines')
    parser.add_argument('-r', '--repeat', action='store_true',
                        help = 'output lines can be repeated')
    args = parser.parse_args()

    if 'itemList' in args and 'itemRange' in args:
        raise Exception('shuf: cannot combine -e and -i options')
    if 'headCount' in args and args.headCount < 0:
        raise Exception("shuf: invalid line count: '" + str(args.headCount) + "'")

    collection = [];
    if 'itemList' in args:
        randomize(args.itemList)
        collection = args.itemList

    if 'itemRange' in args:
        bounds = [0, 0]
        parseRange(args.itemRange, bounds)
        collection = [i for i in range(bounds[0], bounds[1] + 1)]
        randomize(collection)

    flags = []
    if 'headCount' in args:
        flags.append(True)
    else:
        flags.append(False)
    if args.repeat:
        flags.append(True)
    else:
        flags.append(False)

    match flags:
        case [True, True]:
            printRList(collection, args.headCount)
        case [True, False]:
            printNList(collection, args.headCount)
        case [False, True]:
            printRList(collection)
        case [False, False]:
            printList(collection)

if __name__ == "__main__":
    main()
