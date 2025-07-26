With [cProfile](https://docs.python.org/3/library/profile.html) one can benchmark Python programs `python3 -m cProfile -o <out>.prof <py_script>`.
When doing so, the benchmark scripst expect the user to run this fromt he workspace root.

Visualizing this data as flamgraph can be done with [flameprof](https://pypi.org/project/flameprof/).
