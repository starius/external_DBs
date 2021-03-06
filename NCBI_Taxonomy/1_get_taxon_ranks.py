#! /usr/bin/python

import argparse as ap
import tarfile as tf

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Prepare taxonomy data file.")
    parser.add_argument(
            "taxdump", metavar="TAXDUMP.tgz", type=ap.FileType("rb"),
            help="NCBI taxdump file"
            )
    parser.add_argument(
            "-o", dest="outab", metavar="FILE", required=True,
            type=ap.FileType("w"), help="output file"
            )
    args = parser.parse_args()
    names = dict()
    taxids = set()
    intar = tf.open(fileobj=args.taxdump)
    innames = intar.extractfile("names.dmp")
    for line in innames:
        vals = line.strip("\n\t|").split("\t|\t")
        taxid, name = vals[:2]
        taxids.add(taxid)
        if vals[3] == "scientific name":
            names[taxid] = name
    innames.close()
    print "%d taxons were loaded" % len(taxids)
    missed = len(taxids) - len(names)
    if missed:
        print "%d taxids have no scientific names!" % missed
    ranks = dict()
    innodes = intar.extractfile("nodes.dmp")
    for line in innodes:
        vals = line.strip("\n\t|").split("\t|\t")
        taxid, ptaxid, rank = vals[:3]
        if taxid not in taxids:
            print "Warning: %s has no name at all!" % taxid
        if taxid not in names:
            print "Warning: %s has no scientific name!" % taxid
        ranks[taxid] = (rank, ptaxid)
    innodes.close()
    print "%d nodes were loaded." % len(ranks)
    with args.outab as outab:
        outab.write("taxid\tparent_taxid\tscientific_name\trank\n")
        for taxid in taxids:
            name = names.get(taxid, "?")
            if taxid not in ranks:
                print "%s has no rank and parent_taxid, skipped" % taxid
                continue
            rank, ptaxid = ranks[taxid]
            outab.write("\t".join((taxid, ptaxid, name, rank)) + "\n")

