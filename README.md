In this project, you will be building a simple distributed blog post application that is replicated on
5 servers/nodes to ensure fault tolerance. Each server will have its own storage of blog users and
their corresponding blog posts as well as a replicated log of all the blog operations in the form of
a blockchain. You will be using Multi-Paxos as the protocol for reaching agreement on the next
block to be appended to this replicated blockchain.
None of the nodes are assumed to be malicious, but some might crash, also known as a fail-stop
failure. The network may also exhibit failures. In particular, the network might partition.