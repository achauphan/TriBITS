# @HEADER
# ************************************************************************
#
#            TriBTS: Tribal Build, Integrate, and Test System
#                    Copyright 2013 Sandia Corporation
#
# Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the Corporation nor the names of the
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SANDIA CORPORATION "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SANDIA CORPORATION OR THE
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ************************************************************************
# @HEADER

import os
import shutil
import unittest
import stat
import tempfile

from FindCISupportDir import *
import CDashQueryAnalyzeReport as CDQAR
from cdash_analyze_and_report_random_failures import *
from CDashQueryAnalyzeReportUnitTestHelpers import *

# Base test directory in the build tree
g_baseTestDir = "cdash_analyze_and_report_random_failures"


def cdash_analyze_and_report_random_failures_setup_test_dir(testCaseName):
    testInputDir = testCiSupportDir + "/" + g_baseTestDir + "/" + testCaseName
    testOutputDir = os.getcwd()
    for f in os.listdir(testInputDir):
        thing = os.path.join(testInputDir, f)
        if os.path.isdir(thing):
            shutil.copytree(thing, os.path.join(testOutputDir, f))
        else:
            shutil.copy(thing, testOutputDir)
    return testOutputDir


def remove_dirs(dirname):
    walk_gen = os.walk(dirname, topdown=False)
    for dirpath, dirnames, filenames in walk_gen:
        os.chmod(dirpath, stat.S_IRWXU)
    shutil.rmtree(dirname)


def create_file(fpath, perms=0o600, content=""):
    path = os.path.split(fpath)[0]
    if path and not path == "." and not os.path.isdir(path):
        os.makedirs(path)
    with open(fpath, "w+") as fptr:
        fptr.write(content)
    os.chmod(fpath, perms)
    return os.path.abspath(fpath)


class TemporaryDirectory(object):
    def __init__(self, **kwargs):
        self.orig_dir = os.getcwd()
        self.name = tempfile.mkdtemp(
            suffix=kwargs.get("suffix", ""),
            prefix=kwargs.get("prefix", "tmp"),
            dir=kwargs.get("dir", None),
        )

    def remove(self):
        os.chdir(self.orig_dir)
        if os.path.exists(self.name):
            remove_dirs(self.name)

    def __enter__(self):
        os.chdir(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()

#############################################################################
#
# Unit tests for cdash_analyze_and_report_random_failures.py
#
#############################################################################


class test_getBuildIdFromTest(unittest.TestCase):

    def test_single_slash(self):
        test_dict = { 'buildSummaryLink':'build/somenumber' }
        self.assertEqual(
            getBuildIdFromTest(test_dict), 'somenumber')

    def test_multiple_slash(self):
        test_dict = { 'buildSummaryLink':'build/path/temp/somenumber' }
        self.assertEqual(
            getBuildIdFromTest(test_dict), 'somenumber')

    def test_no_slash(self):
        test_dict = { 'buildSummaryLink':'buildid' }
        self.assertEqual(
            getBuildIdFromTest(test_dict), 'buildid')


#############################################################################
#
# System-level tests for cdash_analyze_and_report_random_failures.py
#
#############################################################################


class test_cdash_analyze_and_report_random_failures(unittest.TestCase):
    def cdash_analyze_and_report_random_failures_run_case(
        self,
        expectedRtnCode,
        stdoutRegexList,
        htmlFileRegexList,
        extraCmndLineOptionsList=None,
        verbose=False,
        debugPrint=False,
    ):
        if not extraCmndLineOptionsList:
            extraCmndLineOptionsList = []

        htmlFileName = "htmlFile.html"
        htmlFileAbsPath = os.getcwd()+"/"+htmlFileName

        cmnd = (
            ciSupportDir
            + "/cdash_analyze_and_report_random_failures.py"
            + " --cdash-project-name='Project Name'"
            + " --group-name='Group Name'"
            + " --cdash-site-url='https://something.com/cdash'"
            + " --reference-date=2018-10-28"
            + " --write-email-to-file="+htmlFileName
            + " "
            + " ".join(extraCmndLineOptionsList)
        )

        stdoutFile = "stdout.out"
        stdoutFileAbsPath = os.getcwd() + "/" + stdoutFile
        rtnCode = CDQAR.echoRunSysCmnd(
            cmnd, throwExcept=False, outFile=stdoutFile, verbose=verbose
        )

        stdout = ""
        try:
            with open(stdoutFile, "r") as inf:
                stdout = inf.read()
        except Exception:
            print("WARNING: No stdout available from this test")

        # UNCOMMENT THIS TO SEE OUTPUT FROM THE SCRIPT (Can use the test to help develop)
        # print(stdout)

        self.assertEqual(rtnCode, expectedRtnCode, "Failed with stdout: " + stdout)

        # Grep stdout for expected list of strings
        assertListOfRegexsFoundInListOfStrs(self, stdoutRegexList,
            stdout.splitlines(), stdoutFileAbsPath, debugPrint=debugPrint)

        # Grep written HTML file for expected strings
        try:
            with open(htmlFileName, 'r') as htmlFile:
                htmlFileStrList = htmlFile.read().split("\n")
        except Exception:
            print("WARNING: HTML file not available for this test: "+htmlFileAbsPath)

        assertListOfRegexsFoundInListOfStrs(self, htmlFileRegexList,
            htmlFileStrList, htmlFileAbsPath, debugPrint=debugPrint)


    def setUp(self):
        self.test_dir = TemporaryDirectory()
        os.chdir(self.test_dir.name)

    def tearDown(self):
        self.test_dir.remove()


    # Test the random failure case of a single initial test containing
    # one passing and one failing test in its test history, both with the same SHA1 pairs
    #
    def test_rft_1_ift_1(self):

        testCaseName = "rft_1_ift_1"
        cdash_analyze_and_report_random_failures_setup_test_dir(testCaseName)

        self.cdash_analyze_and_report_random_failures_run_case(
            expectedRtnCode=0,
            stdoutRegexList=[
                "[*][*][*] CDash random failure analysis for Project Name Group Name from 2018-10-28 to 2018-10-28",
                "Total number of initial failing tests: 1",

                "Found random failing tests: 1",
                "Test name: testname1",
                "Build name: build1",
                "Identical sha1 pairs: \(\'592ea0d5\', \'b07e361c\'\)",
                "Test history browser URL:",
                "  https://something[.]com/cdash/queryTests[.]php[?]project=Project%20Name&begin=2018-10-28&end=2018-10-28&filtercount=3&showfilters=1&filtercombine=and&field1=testname&compare1=63&value1=testname1&field2=groupname&compare2=63&value2=Group%20Name&field3=buildname&compare3=63&value3=buildname1",

                "FAILED \(rft=1, ift=1\): Project Name Group Name on 2018-10-28 to 2018-10-28"
            ],
            htmlFileRegexList=[
                "<h2>FAILED \(rft=1, ift=1\): Project Name Group Name on 2018-10-28 to 2018-10-28</h2>",

                "<h2>Random test failure scan results for Project Name from 2018-10-28 to 2018-10-28</h2>",

                "<p>",
                "<a href=\"https://something[.]com/cdash/queryTests[.]php[?]project=Project%20Name&begin=2018-10-28&end=2018-10-28&filtercount=2&showfilters=1&filtercombine=and&field1=status&compare1=63&value1=Failed&field2=groupname&compare2=63&value2=Pull%20Request\">Nonpassing tests scanned on CDash</a>=1<br>",
                "</p",

                "<p>",
                "Found random failing tests: 1<br>",
                "<br>Build name: build1",
                "<br>Test name: testname1",
                "<br>Test history URL: https://something[.]com/cdash/queryTests[.]php[?]project=Project%20Name&begin=2018-10-28&end=2018-10-28&filtercount=3&showfilters=1&filtercombine=and&field1=testname&compare1=63&value1=testname1&field2=groupname&compare2=63&value2=Group%20Name&field3=buildname&compare3=63&value3=buildname1",
                "<br>Sha1 Pair : \('592ea0d5', 'b07e361c'\)",
                "</p>"
            ],
            extraCmndLineOptionsList=[
            ]
        )
    # TODO: Remove the current "random" test case as this should be the base case

    def test_rft_0_ift_2(self):

        testCaseName = "rft_0_ift_2"
        cdash_analyze_and_report_random_failures_setup_test_dir(testCaseName)

        self.cdash_analyze_and_report_random_failures_run_case(
            expectedRtnCode=0,
            stdoutRegexList=[
                "[*][*][*] CDash random failure analysis for Project Name Group Name from 2018-10-26 to 2018-10-28",
                "Total number of initial failing tests: 2",

                "Found random failing tests: 0",

                "PASSED \(rft=0, ift=2\): Project Name Group Name on 2018-10-26 to 2018-10-28"
            ],
            htmlFileRegexList=[
                "<h2>PASSED \(rft=0, ift=2\): Project Name Group Name on 2018-10-26 to 2018-10-28</h2>",

                "<h2>Random test failure scan results for Project Name from 2018-10-26 to 2018-10-28</h2>",

                "<p>",
                "<a href=\"https://something[.]com/cdash/queryTests[.]php[?]project=Project%20Name&begin=2018-10-26&end=2018-10-28&filtercount=2&showfilters=1&filtercombine=and&field1=status&compare1=63&value1=Failed&field2=groupname&compare2=63&value2=Pull%20Request\">Nonpassing tests scanned on CDash</a>=2<br>",
                "</p>",

                "<p>",
                "Found random failing tests: 0<br>",
                "</p>"
            ],
            extraCmndLineOptionsList=[
                "--days-of-history=3"
            ]
        )


if __name__ == "__main__":
    unittest.main()
