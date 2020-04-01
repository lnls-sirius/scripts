#!/usr/bin/env python-sirius



# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
# https://github.com/jml/tree-format
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Library for formatting trees."""

import itertools
from operator import itemgetter


class Options(object):
    """."""

    def __init__(self,
                 FORK=u'\u251c',
                 LAST=u'\u2514',
                 VERTICAL=u'\u2502',
                 HORIZONTAL=u'\u2500',
                 NEWLINE=u'\u23ce'):
        self.FORK = FORK
        self.LAST = LAST
        self.VERTICAL = VERTICAL
        self.HORIZONTAL = HORIZONTAL
        self.NEWLINE = NEWLINE


ASCII_OPTIONS = Options(FORK=u'|',
                        LAST=u'+',
                        VERTICAL=u'|',
                        HORIZONTAL=u'-',
                        NEWLINE=u'\n')


def _format_newlines(prefix, formatted_node, options):
    """
    Convert newlines into U+23EC characters, followed by an actual newline and
    then a tree prefix so as to position the remaining text under the previous
    line.
    """
    replacement = u''.join([
        options.NEWLINE,
        u'\n',
        prefix])
    return formatted_node.replace(u'\n', replacement)


def _format_tree(node, format_node, get_children, options, prefix=u''):
    children = list(get_children(node))
    next_prefix = u''.join([prefix, options.VERTICAL, u'   '])
    for child in children[:-1]:
        yield u''.join([prefix,
                        options.FORK,
                        options.HORIZONTAL,
                        options.HORIZONTAL,
                        u' ',
                        _format_newlines(next_prefix,
                                         format_node(child),
                                         options)])
        for result in _format_tree(child,
                                   format_node,
                                   get_children,
                                   options,
                                   next_prefix):
            yield result
    if children:
        last_prefix = u''.join([prefix, u'    '])
        yield u''.join([prefix,
                        options.LAST,
                        options.HORIZONTAL,
                        options.HORIZONTAL,
                        u' ',
                        _format_newlines(last_prefix,
                                         format_node(children[-1]),
                                         options)])
        for result in _format_tree(children[-1],
                                   format_node,
                                   get_children,
                                   options,
                                   last_prefix):
            yield result


def format_tree(node, format_node, get_children, options=None):
    """."""
    lines = itertools.chain(
        [format_node(node)],
        _format_tree(node, format_node, get_children, options or Options()),
        [u''],
    )
    return u'\n'.join(lines)


def format_ascii_tree(tree, format_node, get_children):
    """Format the tree using only ascii characters."""
    return format_tree(tree,
                       format_node,
                       get_children,
                       ASCII_OPTIONS)


def format_tree_simple(tree):
    """."""
    return format_tree(
        tree, format_node=itemgetter(0), get_children=itemgetter(1))


def print_tree(*args, **kwargs):
    """Print tree."""
    print(format_tree(*args, **kwargs))


# ---


# from tree_format import format_tree_simple
from siriuspy.search import PSSearch
from siriuspy.csdev import get_device_2_ioc_ip


def create_tree():
    """."""
    dev2ip = get_device_2_ioc_ip()
    bbbnames = PSSearch.get_bbbnames()
    tree = ['BeagleBones', []]
    for bbbname in bbbnames:
        # PSSearch.con
        bbbip = dev2ip[bbbname] if bbbname in dev2ip else ''
        bbblist = (bbbname + '  [' + bbbip + ']', [])
        udcnames = PSSearch.conv_bbbname_2_udc(bbbname)
        for udcname in udcnames:
            udclist = [udcname, []]
            devices = PSSearch.conv_udc_2_bsmps(udcname)
            for device in devices:
                psname, bsmp_id = device
                psmodel = PSSearch.conv_psname_2_psmodel(psname)
                if device == devices[0]:
                    udclist[0] += '  (' + psmodel + ')'
                pslist = [psname + '  (' + str(bsmp_id) + ')', []]

                try:
                    dclinks = PSSearch.conv_psname_2_dclink(psname)
                except KeyError:
                    dclinks = []
                if dclinks is None:
                    dclinks = []
                if len(dclinks) > 0:
                    for dclink in dclinks:
                        dclinklist = [dclink, []]
                        pslist[-1].append(dclinklist)

                # print(dclinks)
                udclist[-1].append(pslist)
                # print(psname, bsmp_id)
            bbblist[-1].append(udclist)
        tree[-1].append(bbblist)
    return tree


tree = create_tree()
print(format_tree_simple(tree))
