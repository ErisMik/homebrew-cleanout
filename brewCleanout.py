# Copyright Eric Mikulin, 2016

import subprocess
from os import system

def main():
    # Find all the packeges the user has installed
    packages = []
    proc = subprocess.Popen(["brew", "list"], stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    tmp = tmp.split()
    for item in tmp:
        packages.append(item)
    print packages

    # Determine wich ones are deletable candidates
    possibles = []
    for formula in packages:
        # proc = subprocess.Popen(["brew", "uses", "--installed", formula], stdout=subprocess.PIPE)
        # tmp = proc.stdout.read()

        proc2 = subprocess.Popen(["brew", "uses", formula], stdout=subprocess.PIPE)
        tmp2 = proc2.stdout.read()

        inter = list(set(packages) & set(tmp2))

        # if tmp == "" and not tmp2 == "":
        if len(inter) == 0 and not tmp2 == "":
            possibles.append(formula)

    # Ensure there are packages to delete
    if len(possibles) == 0:
        return

    # Find descriptions of the packages
    deps = {}
    command = ["brew", "desc"] + possibles
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    tmp = tmp.split("\n")
    del tmp[-1]
    for line in tmp:
        tups = line.split(":")
        deps[tups[0]] = tups[1].strip()

    # Ask for deletion of all the packages
    toDelete = []
    for formula in deps:
        print formula + ": " + deps[formula]
        value = raw_input("Delete %s ? [Y/n]" % formula)
        if "n" not in value:
            toDelete.append(formula)

    # delete packages
    for package in toDelete:
        print "DELETING: " + package
        system("brew uninstall %s" % package)

    # Ask for cleanup
    value = raw_input("Perform 'brew cleanup' ? [Y/n]")
    if "n" not in value:
        print "Performing cleanup"
        system("brew cleanup")


if __name__ == "__main__":
    main()
