#!/usr/local/cs/bin/python3

import os
import sys
import zlib

# I used the command: strace -f -e execve topo_order_commits.py
# This command uses strace to follow system calls. The -e flag
# and the execve that follows it tells strace to focus only on
# execve calls and ignore the rest. The execve system call denotes
# executable programs and shell commands. Whenever they are invoked
# by a process, there will be an execve system call. Since the output
# of the command above was only:
# execve("/u/cs/ugrad/yangd/assign6/topo_order_commits.py", ["topo_order_commits.py"], 0x7fff79853e98 /* 41 vars */) = 0
# this means that besides the topo_order_commits.py executable running
# no other shell commands are called.

class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()
    # returns a CommitNode with the same properties
    def copy(self):
        copy_node = CommitNode(self.commit_hash)
        copy_node.parents = self.parents.copy()
        copy_node.children = self.children.copy()
        return copy_node

# gets the parent hashes of the provided commit_hash
def get_parents(current_directory, commit_hash):
    commit_dir = commit_hash[0:2]
    commit_file = commit_hash[2:]
    current_directory = current_directory + '/objects/' + commit_dir
    file_path = current_directory + '/' + commit_file
    compressed_contents = open(file_path, 'rb').read()
    decompressed_contents = zlib.decompress(compressed_contents)
    parents = set()
    for i in decompressed_contents.split(b'\n'):
        if (i.find(str.encode('parent')) == 0):
            parents.add(i[7:].decode('utf-8'))
    return parents

# <str, str[]>: builds a graph and returns as a dictionary of {hash: CommitNode()}
def build_commit_graph(current_directory, root_commits):
    commit_nodes = {} # dictionary of nodes
    visited = set() # string of all hashes visited
    stack = root_commits # str array of leaf hashes
    while stack:
        commit_hash = stack.pop()
        if commit_hash in visited:
            continue
        visited.add(commit_hash)
        if commit_hash not in commit_nodes:
            commit_nodes[commit_hash] = CommitNode(commit_hash)
        commit = commit_nodes[commit_hash]
        commit.parents = get_parents(current_directory, commit_hash)
        for p in commit.parents:
            if p not in visited:
                stack.append(p)
            if p not in commit_nodes:
                commit_nodes[p] = CommitNode(p)
            commit_nodes[p].children.add(commit_hash)
    return commit_nodes

# copies the commit_node dictionary
def deep_copy(commit_nodes):
    copy_nodes = {}
    for i in commit_nodes:
        copy_nodes[i] = commit_nodes[i].copy()
    return copy_nodes

# sorts the commit_nodes in topological order
def topo_sort(commit_nodes):
    result = []
    no_children = []
    copy_graph = deep_copy(commit_nodes)

    for commit_hash in copy_graph:
        if len(copy_graph[commit_hash].children) == 0:
            no_children.append(commit_hash)
    
    while len(no_children) > 0:
        commit_hash = no_children.pop(0)
        result.append(commit_hash)
        for parent_hash in list(copy_graph[commit_hash].parents):
            copy_graph[commit_hash].parents.remove(parent_hash)
            copy_graph[parent_hash].children.remove(commit_hash)
            if len(copy_graph[parent_hash].children) == 0:
                no_children.append(parent_hash)
    
    if len(result) < len(commit_nodes):
        raise Exception("cycle detected")
    return result

# <dict, list, dict>: prints out the commit_nodes in the format
def print_commits(commit_nodes, sorted_commits, branch_names):
    empty_printed = False
    for i in range(len(sorted_commits)):
        commit_hash = sorted_commits[i]
        if empty_printed:
            sticky_start = "=" + " ".join(str(child) for child in commit_nodes[sorted_commits[i]].children)
            print(sticky_start)
            empty_printed = False
        branches = sorted(branch_names[commit_hash]) if commit_hash in branch_names else []
        branch_string = " ".join(str(name) for name in branches)
        print(commit_hash + (" " if len(branch_string) != 0 else "") + branch_string)
        if i + 1 < len(sorted_commits) and sorted_commits[i + 1] not in commit_nodes[commit_hash].parents:
            sticky_end = " ".join(str(parent) for parent in commit_nodes[sorted_commits[i]].parents)
            sticky_end = sticky_end + '='
            print(sticky_end + '\n')
            empty_printed = True

# recursively checks for branch heads and adds them to root_commits and branch_names
def directory_recursion(current_directory, path_string, root_commits, branch_names):
    for i in os.listdir(current_directory + "/refs/heads/" + path_string):
        path = current_directory + "/refs/heads/" + path_string + i
        if (os.path.isdir(path)):
            directory_recursion(current_directory, path_string + i + '/', root_commits, branch_names)
            continue
        commit_hash = open(path).read().strip("\n")
        root_commits.append(commit_hash)
        if commit_hash in branch_names:
            branch_names[commit_hash].append(path_string + i)
        else:
            branch_names[commit_hash] = [path_string + i]

def topo_order_commits():
    # navigate to .git directory
    current_directory = os.getcwd()
    while (not os.path.isdir(current_directory+"/.git")):
        if current_directory == "/":
            print("Not inside a Git repository", file=sys.stderr)
            exit(1)
        current_directory = os.path.dirname(current_directory)
    # current_directory is the .git folder
    current_directory = current_directory + ".git" if current_directory == "/" else current_directory + "/.git"
    # root_commits is array of leaf nodes
    root_commits = []
    branch_names = {}
    directory_recursion(current_directory, '', root_commits, branch_names)
    commit_nodes = build_commit_graph(current_directory, root_commits)
    #sorted
    sorted_commits = topo_sort(commit_nodes)
    # print
    print_commits(commit_nodes, sorted_commits, branch_names)


if __name__ == "__main__":
    topo_order_commits()