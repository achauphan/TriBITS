#!/usr/bin/env python

import sys
import argparse
import re as regex

import CDashAnalyzeReportRandomFailures as CDARRF


usageHelp = \
r"""trilinos_cdash_analyze_and_report_random_failures.py [options]

This script takes in various CDash URL information along with other command line
arguments to query, analyze, and report randomly failing tests of a CDash project.
Found randomly failing tests are reported in a constructed HTML format
that can be written to a specified file on disk and/or sent via email to
one or more addresses.
"""


def main():

  cdashAnalyzeAndReportRandomFailures = \
    CDARRF.CDashAnalyzeReportRandomFailuresDriver(
      TrilinosVersionInfoStrategy(),
      TrilinosExtractBuildNameStrategy(),
      usageHelp=usageHelp)

  cdashAnalyzeAndReportRandomFailures.runDriver()

class TrilinosVersionInfoStrategy:

  def getTargetTopicSha1s(self, buildData):
    pattern = r"Parent [12]:\n\s+(\w+)"
    matchedList = regex.findall(pattern, buildData)

    if len(matchedList) != 2: return None
    return tuple(matchedList)

  def checkTargetTopicRandomFailure(self, targetTopicPair, knownTargetTopicPairs):
    return targetTopicPair in knownTargetTopicPairs

class TrilinosExtractBuildNameStrategy:

  def getCoreBuildName(self, fullBuildName):
    coreBuildName = fullBuildName.rsplit('-',1)[0]
    return coreBuildName



if __name__ == '__main__':
  sys.exit(main())