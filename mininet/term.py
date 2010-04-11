"""
Terminal creation and cleanup.
Utility functions to run a term (connected via screen(1)) on each host.

Requires GNU screen(1) and xterm(1).
Optionally uses gnome-terminal.
"""

import re
from subprocess import Popen

from mininet.log import error
from mininet.util import quietRun

def joinCmd( args ):
    "Join args into a string, single-quoting items with spaces."
    result = ''
    for arg in args:
        if ' ' in item:
            result += " '%s'" % arg
        else:
            result += " %s" % arg
    return result

def makeTerm( node, title = '', term = 'xterm' ):
    """Run screen on a node, and hook up a terminal.
       node: Node object
       title: base title
       term: 'xterm' or 'gterm'
       returns: process created"""
    title += ': ' + node.name
    if not node.inNamespace:
        title += ' (root)'
    cmds = {
        'xterm': [ 'xterm', '-title', title, '-e' ],
        'gterm': [ 'gnome-terminal', '--title', title, '-e' ]
    }
    if term not in cmds:
        error( 'invalid terminal type: %s' % term )
        return
    if not node.execed:
        node.cmd( 'screen -dmS ' + node.name)
        args = [ 'screen', '-D', '-RR', '-S', 'mininet.' + node.name ]
    else:
        args = [ 'sh', '-c', 'exec tail -f /tmp/' + node.name + '*.log' ]
    if term == 'gterm':
        # Compress these for gnome-terminal, which expects one token to follow
        # the -e option    .
        args = joinCmd( args )
    return Popen( cmds[ term ] + args )

def cleanUpScreens():
    "Remove moldy old screen sessions."
    r = r'(\d+\.mininet\.[hsc]\d+)'
    output = quietRun( 'screen -ls' ).split( '\n' )
    for line in output:
        m = re.search( r, line )
        if m:
            quietRun( 'screen -S ' + m.group( 1 ) + ' -X quit' )

def makeTerms( nodes, title = '', term = 'xterm' ):
    """Create terminals.
       nodes: list of Node objects
       title: base title for each
       returns: list of created terminal processes"""
    return [ makeTerm( node, title, term ) for node in nodes ]
