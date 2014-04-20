"""py-unit tests for GnuPG

COPYRIGHT:

Copyright (C) 2001  Frank J. Tobin, ftobin@neverending.org

LICENSE:

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see http://www.gnu.org/copyleft/lesser.html
"""

import unittest

import tempfile
import sys

from duplicity import gpginterface

__author__   = "Frank J. Tobin, ftobin@neverending.org"
__version__  = "0.2.2"
__revision__ = "$Id: GnuPGInterfacetest.py,v 1.11 2009/06/06 17:35:19 loafman Exp $"

class BasicTest(unittest.TestCase):
    """an initializer superclass"""

    def __init__(self, methodName=None):
        self.gnupg = gpginterface.GnuPG()
        unittest.TestCase.__init__(self, methodName)


class GnuPGTests(BasicTest):
    """Tests for GnuPG class"""

    def __init__(self, methodName=None):
        BasicTest.__init__(self, methodName)

        self.gnupg.passphrase = "Three blind mice"
        self.gnupg.options.armor = 1
        self.gnupg.options.meta_interactive = 0
        self.gnupg.options.extra_args.append('--no-secmem-warning')

    def do_create_fh_operation(self, args, input,
                               passphrase=None):
        creations = ['stdin', 'stdout']

        # Make sure we're getting the passphrase to GnuPG
        # somehow!
        assert passphrase != None or self.gnupg.passphrase != None, \
               "No way to send the passphrase to GnuPG!"

        # We'll handle the passphrase manually
        if passphrase != None: creations.append('passphrase')

        proc = self.gnupg.run( args, create_fhs=creations )

        if passphrase != None:
            proc.handles['passphrase'].write(passphrase)
            proc.handles['passphrase'].close()

        proc.handles['stdin'].write(input)
        proc.handles['stdin'].close()

        ciphertext = proc.handles['stdout'].read()
        proc.handles['stdout'].close()

        # Checking to make sure GnuPG exited successfully
        proc.wait()

        return ciphertext


    def do_attach_fh_operation(self, args, stdin, stdout,
                               passphrase=None):

        # Make sure we're getting the passphrase to GnuPG
        # somehow!
        assert passphrase != None or self.gnupg.passphrase != None, \
               "No way to send the passphrase to GnuPG!"

        creations = []
        # We'll handle the passphrase manually
        if passphrase != None: proc.handles.append('passphrase') #@UndefinedVariable

        attachments = { 'stdin': stdin, 'stdout': stdout }

        proc = self.gnupg.run( args, create_fhs=creations,
                               attach_fhs=attachments )

        if passphrase != None:
            proc.handles['passphrase'].write(passphrase)
            proc.handles['passphrase'].close()

        # Checking to make sure GnuPG exited successfully
        proc.wait()


    def test_create_fhs_solely(self):
        """Do GnuPG operations using solely the create_fhs feature"""
        plaintext = "Three blind mice"

        ciphertext = self.do_create_fh_operation( ['--symmetric'],
                                                  plaintext )

        decryption = self.do_create_fh_operation( ['--decrypt'],
                                                  ciphertext,
                                                  self.gnupg.passphrase )
        assert decryption == plaintext, \
               "GnuPG decrypted output does not match original input"


    def test_attach_fhs(self):
        """Do GnuPG operations using the attach_fhs feature"""
        plaintext_source = __file__

        plainfile = open(plaintext_source)
        temp1 = tempfile.TemporaryFile()
        temp2 = tempfile.TemporaryFile()

        self.do_attach_fh_operation( ['--symmetric'],
                                     stdin=plainfile, stdout=temp1 )

        temp1.seek(0)

        self.do_attach_fh_operation( ['--decrypt'],
                                     stdin=temp1, stdout=temp2 )

        plainfile.seek(0)
        temp2.seek(0)

        assert fh_cmp(plainfile, temp2), \
               "GnuPG decrypted output does not match original input"


class OptionsTests(BasicTest):
    """Tests for Options class"""

    def __init__(self, methodName=None):
        BasicTest.__init__(self, methodName)
        self.reset_options()

    def reset_options(self):
        self.gnupg.options = gpginterface.Options()

    def option_to_arg(self, option):
        return '--' + option.replace('_', '-')

    def test_boolean_args(self):
        """test Options boolean options that they generate
        proper arguments"""

        booleans = [ 'armor',      'no_greeting',  'no_verbose',
                     'batch',      'always_trust', 'rfc1991',
                     'quiet',      'openpgp',      'force_v3_sigs',
                     'no_options', 'textmode' ]

        for option in booleans:
            self.reset_options()
            setattr(self.gnupg.options, option, 1)
            arg = self.option_to_arg(option)

            should_be = [arg]
            result    = self.gnupg.options.get_args()

            assert should_be == result, \
                   "failure to set option '%s'; should be %s, but result is %s" \
                   % (option, should_be, result)

    def test_string_args(self):
        """test Options string-taking options that they generate
        proper arguments"""

        strings = [ 'homedir', 'default_key', 'comment', 'compress_algo',
                    'options' ]

        string_value = 'test-argument'

        for option in strings:
            self.reset_options()
            setattr(self.gnupg.options, option, string_value)
            arg = self.option_to_arg(option)

            should_be = [arg, string_value]
            result    = self.gnupg.options.get_args()

            assert should_be == result, \
                   "failure to set option '%s'; should be %s, but result is %s" \
                   % (option, should_be, result)

    def test_list_args(self):
        """test Options string-taking options that they generate
        proper arguments"""

        lists = [ 'recipients', 'encrypt_to' ]
        list_value = ['test1', 'test2']

        for option in lists:
            self.reset_options()
            setattr(self.gnupg.options, option, list_value)

            # special case for recipients, since their
            # respective argument is 'recipient', not 'recipients'
            if option == 'recipients': arg = '--recipient'
            else: arg = self.option_to_arg(option)

            should_be = []
            for v in list_value: should_be.extend([arg, v])

            result = self.gnupg.options.get_args()

            assert should_be == result, \
                   "failure to set option '%s'; should be %s, but result is %s" \
                   % (option, should_be, result)


class PipesTests(unittest.TestCase):
    """Tests for Pipes class"""

    def test_constructor(self):
        self.pipe = gpginterface.Pipe(1, 2, 0)
        assert self.pipe.parent == 1
        assert self.pipe.child  == 2
        assert not self.pipe.direct

########################################################################

def fh_cmp(f1, f2, bufsize=8192):
    while 1:
        b1 = f1.read(bufsize)
        b2 = f2.read(bufsize)
        if b1 != b2: return 0
        if not b1:   return 1

########################################################################

if __name__ == "__main__":
    unittest.main()
