# Copyright 2017 Numenta Inc.
#
# Copyright may exist in Contributors' modifications
# and/or contributions to the work.
#
# Use of this source code is governed by the MIT
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import sys



class DotRenderer(object):
  """
  Network visualization "renderer" implementation to render a network to a
  dot-formatted document, suitable for use w/ graphviz.

  :param outp: File-like obj to which rendered graph is written (defaults to
         sys.stdout)
  :param node_attrs: Node attributes to apply to all nodes in graph
  """

  # Default node attributes to apply to all nodes in graph.
  defaultNodeAttrs = {"shape": "record"}


  def __init__(self, outp=sys.stdout, node_attrs=None):
    self.outp = outp
    self.node_attrs = node_attrs or self.defaultNodeAttrs


  def render(self, graph):

    self.outp.write(u"digraph structs {\n")
    self.outp.write(u'rankdir = "LR";\n')


    lookup = {}

    for edge in graph.edges():
      data = graph.get_edge_data(*edge)

      lookup.setdefault(edge[0], {"inputs": set(), "outputs": set()})
      lookup.setdefault(edge[1], {"inputs": set(), "outputs": set()})

      for labels in data.values():
        lookup[edge[0]]["outputs"].add(labels["src"])
        lookup[edge[1]]["inputs"].add(labels["dest"])
        self.outp.write(u'"{}":{} -> "{}":{};\n'.format(edge[0],
                                                        labels["src"],
                                                        edge[1],
                                                        labels["dest"]))

    def _renderPorts(ports):
      return "{" + "|".join("<{}>{}".format(port, port) for port in ports) + "}"

    for node, ports in lookup.items():
      def _renderNode():
        nodeAttrs = ",".join("{}={}".format(key, value)
                             for key, value in self.node_attrs.items())
        nodeAttrs += "," if nodeAttrs else ""

        return ('{} [{}label="{}"];\n'
                .format(node,
                        nodeAttrs,
                        "{" + "|".join([_renderPorts(ports["inputs"]),
                                        node,
                                        _renderPorts(ports["outputs"])]) + "}"))

      self.outp.write(unicode(_renderNode()))

    self.outp.write(u"}\n")
