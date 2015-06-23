###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import sys
import decimal

from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession


class Calculator(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        self.clear()
        yield self.register(self)
        print("Ok, calculator procedures registered!")

    @wamp.register(u'com.example.calculator.clear')
    def clear(self, arg=None):
        self.op = None
        self.current = decimal.Decimal(0)
        return str(self.current)

    @wamp.register(u'com.example.calculator.calc')
    def calc(self, op, num):
        num = decimal.Decimal(num)
        if self.op:
            if self.op == "+":
                self.current += num
            elif self.op == "-":
                self.current -= num
            elif self.op == "*":
                self.current *= num
            elif self.op == "/":
                self.current /= num
            self.op = op
        else:
            self.op = op
            self.current = num

        res = str(self.current)
        if op == "=":
            self.clear()

        return res


if __name__ == '__main__':

    decimal.getcontext().prec = 20

    import sys
    import argparse

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("--web", type=int, default=8080,
                        help='Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type=str, default=None,
                        help='If given, connect to this WAMP router. Else run an embedded router on 9000.')

    args = parser.parse_args()

    if args.debug:
        from twisted.python import log
        log.startLogging(sys.stdout)

    # import Twisted reactor
    ##
    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))

    # create embedded web server for static files
    ##
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))

    # run WAMP application component
    ##
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or 'ws://localhost:9000'

    runner = ApplicationRunner(router, u"realm1", standalone=not args.router,
                               debug=False,             # low-level logging
                               debug_wamp=args.debug,   # WAMP level logging
                               debug_app=args.debug     # app-level logging
                               )

    # start the component and the Twisted reactor ..
    ##
    runner.run(Calculator)
