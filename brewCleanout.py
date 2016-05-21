# Copyright Eric Mikulin, 2016

import subprocess
from os import system

def main():
    # Find all the packages the user has installed by calling 'brew list'
    print("Finding installed packages")
    packages = []
    proc = subprocess.Popen(["brew", "list"], stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    tmp = tmp.split()
    for item in tmp:
        packages.append(item)
    print(packages)

    # Read the keep file if it exists, and add those to a list of formulas to keep
    print("Reading file for packages marked to keep")
    keeping = []
    try:
        with open("formulas.keep", 'r') as keep_file:
            for line in keep_file:
                keeping.append(line.strip())
    except:
        print("Keep file does not exist")

    # Determine which packages are deletable candidates
    possibles = []
    for formula in packages:
        if formula in keeping:  # If the file is marked to keep, ignore it and tell user
            print(formula+" is marked to keep")
        else:
            print("Finding uses and dependencies for "+formula)
            proc2 = subprocess.Popen(["brew", "uses", formula], stdout=subprocess.PIPE)
            tmp2 = proc2.stdout.read()

            tmp2 = tmp2.split("\n")  # tmp2 is now a list of formulas that use this one

            # This bit determines if one of the installed packages on the systm uses this formula
            inter = []
            for dep in tmp2:
                if dep in packages:
                    inter.append(dep)

            # If the formula is a dependency, and is not being used currently...
            if len(inter) == 0 and not tmp2[0] == '':
                possibles.append(formula)
                print("Adding "+formula+" as deletion candidate")

    # Ensure there are actually packages to delete
    if len(possibles) == 0:
        print("No unused dependencies found")
        return
    print("Unused dependencies found")

    # Find descriptions of the packages for use when deleting
    print("Finding package descriptions")
    deps = {}
    command = ["brew", "desc"] + possibles
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    tmp = tmp.split("\n")
    del tmp[-1]  # List contains trailing empty element, delete it
    for line in tmp:  # Form dictionary based on descriptions
        tups = line.split(":")
        deps[tups[0]] = tups[1].strip()

    # Ask for deletion of each of the packages
    print("")
    to_delete = []
    to_keep = []
    for formula in deps:
        print(formula + ": " + deps[formula])
        value = raw_input("Delete %s? [Y/n/k]" % formula)
        if "k" in value:
            to_keep.append(formula) 
        elif "n" not in value:
            to_delete.append(formula)
        print("")

    # Write keep-ed packages to file
    if len(to_keep) > 0:
        with open("formulas.keep", 'a') as keep_file:
            for keep in to_keep:
                print("Marking "+keep+" to keep")
                keep_file.write(keep+"\n")

    # Delete marked packages
    for package in to_delete:
        print("DELETING: " + package)
        system("brew uninstall %s" % package)
        print("Done\n")

    # Ask to run 'brew cleanup'
    value = raw_input("Perform 'brew cleanup -s -force'? [Y/n]")
    if "n" not in value:
        print("Performing cleanup")
        system("brew cleanup -s -force")
    else:
        value = raw_input("Perform 'brew cleanup'? [Y/n]")
        if "n" not in value:
            print("Performing cleanup")
            system("brew cleanup")

    # Ask to run 'brew doctor'
    value = raw_input("Perform 'brew doctor'? [Y/n]")
    if "n" not in value:
        print("Performing doctor")
        system("brew doctor")


if __name__ == "__main__":
    main()
    print("Homebrew Cleanout complete, exiting....")
