----------------------------------------
ChangeLog for TriBITS
----------------------------------------

## 2022-03-02:

* **Added:** Added project-level cache varaible `<Project>_IMPORTED_NO_SYSTEM`
  to set the `IMPORTED_NO_SYSTEM` property on the exported IMPORTED library
  targets in the installed `<Package>Config.cmake` files (see updated TriBITS
  documentation for `<Project>_IMPORTED_NO_SYSTEM`).

## 2021-11-18:

* **Changed:** The default `<Project>_GENERATE_REPO_VERSION_FILE_DEFAULT` will
  be overridden to `OFF` if the 'git' executable cannot be found at configure
  time.  See updated TriBITS Developer's Guide documentation.

* **Changed:** The default value for `<Project>_ENABLE_Fortran` is set to
  `OFF` on WIN32 systems.  (Getting a Fortran compiler for native Windows is
  not typically very easy.)

## 2021-10-11

* **Changed:** The `<Package>Config.cmake` for each enabled package generated
  in the build directory tree have been moved from
  `<buildDir>/packages/<packageDir>/` to
  `<buildDir>/cmake_packages/<PackageName>/`.  (This makes it easy for
  `find_package(<PackageName>)` to find these files by simply adding the
  directory `<buildDir>/cmake_packages` to `CMAKE_PREFIX_PATH` and then
  `<Package>Config.cmake` for any enabled package will be found automatically
  found by CMake.)

* **Added/Changed:** Added the include directories for each library target
  with `target_include_directories()`.  This makes the usage of the variables
  `<Package>_INCLUDE_DIRS`, `<Package>_TPL_INCLUDE_DIRS`,
  `<Project>_INCLUDE_DIRS`, and `<Project>_TPL_INCLUDE_DIRS` unnecessary by
  downstream CMake projects. (See the changes to the
  `TribitsExampleApp/CmakeLists.txt` file that remove calls to
  `include_directories()`.)  However, this change will also cause downstream
  CMake projects to pull in include directories as `SYSTEM` (e.g. using
  `-isystem` instead of `-I`) from IMPORTED library targets.  This changes how
  these include directories are searched and could break some fragile build
  environments that have the same header file names in multiple include
  directories searched by the compiler.  Also, this will silence any regular
  compiler warnings from headers found under these include
  directories. ***Workarounds:*** One workaround for this is for the
  downstream CMake project to set the cache variable
  `CMAKE_NO_SYSTEM_FROM_IMPORTED=TRUE` which will restore the include
  directories for the IMPORTED library targets for the TriBITS project as
  non-SYSTEM include directories (i.e. `-I`) but it will also cause all
  include directories for all IMPORTED library targets to be non-SYSTEM
  (i.e. `-I`) even if they were being handled as SYSTEM include directories
  before.  Therefore, that could still break the downstream project as it
  might change what header files are found for these other IMPORTED library
  targets and may expose many new warnings (which may have been silenced by
  their include directories being pulled in using `-isystem`).  The other
  workaround would be to clean up the list of include directories or delete
  some header files in those include directories so that only the correct
  header files can be found (regardless of the search order).  For more
  details, see
  [TriBITSPub/TriBITS#443](https://github.com/TriBITSPub/TriBITS/issues/443).

## 2021-09-13

* **Removed:** Support for generation and installation of `Makefile.export.*`
  files has been removed along with the cache variable
  `<Project>_ENABLE_EXPORT_MAKEFILES`.  This is to allow the refactoring of
  TriBITS to use modern CMake targets that propagate all information and
  removing complex dependency tracking information from TriBITS (see
  TriBITSPub/TriBITS#63 and TriBITSPub/TriBITS#299).

## 2021-06-17

* **Added:** Added tool `tribits/python_utils/lower_case_cmake.py` and driver
  `tribits/refactoring/lower-case-cmake-tree.sh` that can make CMake command
  calls lower-case and make macro and function definition names lower case.
  This was applied to the entire TriBITS repository (and then minor
  modifications to fix a few issues).  This should not impact users of TriBITS
  but it does change the case of commands in the TriBITS error messages.  (See
  TriBITSPub/TriBITS#274)

## 2021-05-15

* **Changed/Fixed:** Changed so that all arguments passed to `ctest -S`
  command in 'dashboard' target are passed if their value is non-empty instead
  of `TRUE`.  Also, `CTEST_BUILD_NAME`, `TRIBITS_2ND_CTEST_DROP_SITE` and
  `TRIBITS_2ND_CTEST_DROP_LOCATION` can now be set and overridden in the CMake
  configure and will get passed to the `ctest -S` command by the 'dashboard'
  target.  This now allows setting these latter vars to `OFF` or `FALSE` which
  allows skipping a submit to a secondary CDash site if the underlying project
  is set up to submit to a secondary CDash site by default (see
  trilinos/Trilinos#9079).  These changes technically break backward
  compatibility because now setting some vars in the CMake configure will now
  get passed on to `ctest -S` command in the 'dashboard' target and some vars
  set in the env when calling 'make dashboard' will now be ignored if they
  were set in the CMake cache.  But many of these vars are only forwarded to
  the ctest -S command in the env if they are set to non-empty in the
  configure.  So existing processes that set `CTEST_BUILD_NAME` in the env
  when running `make dashboard` but not in the CMake configure will still
  behave the same (which is why no existing TriBITS tests had to change).  For
  these reasons, the chance of these changes causing a problem for most users
  should be very small and in fact it restores what most people would consider
  to be logical and useful behavior.

## 2021-03-12

* **Changed:** Upgrade minimum required CMake version from 3.10 to 3.17.  Existing
  TriBITS projects that have already upgraded to require CMake 3.17+ should not
  notice any major changes due to this change.

## 2020-11-12

* **Changed:** The default for `<Project>_ENABLE_EXPLICIT_INSTANTIATION` (ETI)
  was changed from `OFF` to `ON`.  This was turned on in practice for almost
  all users of Trilinos so while this change technically breaks backward
  compatibility of TriBITS, in practice, this will likely not impact any
  important customers.  (And new customers of Trilinos and related TriBITS
  projects will enjoy the benefits of ETI by default.  See
  trilinos/Trilinos#8130.)

## 2020-10-08

* **Changed:** Tests defined with `TRIBITS_ADD_TEST()` and
  `TRIBITS_ADD_ADVANCED_TEST()` with `NUM_MPI_PROCS > 1` will now not be
  added for non-MPI (`TPL_ENABLE_MPI=OFF`) configurations.  Before, the test
  would get added and basically ignore the value of `NUM_MPI_PROCS`.  This
  change together with the change to move to using `add_test(NAME <name>
  COMMAND <command>)` mostly restores backward compatibility for projects
  using TriBITS.  For more details, see trilinos/Trilinos#8110.

## 2020-09-28

* **Changed/Fixed:** Tests defined with `TRIBITS_ADD_TEST()` and
  `TRIBITS_ADD_ADVANCED_TEST()` have been updated from using
  `add_test(<name> <command>)` to using `add_test(NAME <name> COMMAND
  <command>)`.  This now causes CMake to error-out if there is more than one
  test with the same name in the same directory.  Before, CMake would allow
  it (but the behavior in that case was undocumented and undefined).  For
  more details, see trilinos/Trilinos#8110.

## 2020-06-16

* **Added/Deprecated:** The variables `<Package>_FORTRAN_COMPILER` and
  `<Package>_FORTRAN_FLAGS` in the `<Package>Config.cmake` files (in the build
  dir and the install dir) are deprecated.  Please use the new variables
  `<Package>_Fortran_COMPILER` and `<Package>_Fortran_FLAGS`.  (Justification:
  In raw CMake, the compiler is called 'Fortran', not 'FORTRAN'.  Also, the
  name 'Fortran' is already used in the `<Project>Config.cmake` file.)

## 2020-04-16

* **Changed/Removed:** TriBITS Core: `CMAKE_CXX_STANDARD` is now always set to
  at least `11` to enable C++11 support.  The `${PROJECT_NAME}_ENABLE_CXX11`
  option has been removed, but a variable of the same name is hard-coded to ON
  for compatibility.

* **Changed/Removed:** TriBITS Core: `CMAKE_CXX_FLAGS` will no longer contain
  an explicit C++ standard option like `-std=c++11`.  TriBITS clients'
  dependents using CMake will still compile with support for C++11 language
  constructs because libraries come with `INTERFACE_COMPILE_FEATURES`
  including `cxx_std_11`.  However, those using `Makefile.export.<Package>`
  files will no longer get a `-std=c++11` flag.

## 2018-10-10

* **Changed:** TriBITS Core: Changed minimum CMake version from 2.8.11 to
  3.10.0.

## 2017-09-25

* **Added:** TriBITS CTest Driver: Added cache and env vars
  `CTEST_SUBMIT_RETRY_COUNT` and `CTEST_SUBMIT_RETRY_DELAY` to allow the
  number of `ctest_submit()` submit attempts to retry and how long to pause
  between retries.  Before, these were hard-coded to 25 and 120 respectively,
  which means that something like a MySQL insertion error could consume as
  much as 50 minutes before moving on!  The new defaults are set at 5 retries
  with a 3 sec delay (which appear to be the CTest defaults).

## 2017-09-30

* **Added:** TriBITS Core: Added `TEST_<IDX> COPY_FILES_TO_TEST_DIR` block for
    `TRIBITS_ADD_ADVANCED_TEST()`.  This was added in such a way so to avoid
    clashing with existing usages of the script (since the new arguments
    `SOURCE_DIR` and `DEST_DIR` are only parsed if `COPY_FILES_TO_TEST_DIR` is
    listed in the `TEST_<IDX> block`.

## 2017-09-05

* **Changed:** TriBITS Core: Un-parsed and otherwise ignored arguments to many
  TriBITS functions and macros are now flagged (see developers guide
  documentation for `${PROJECT_NAME}_CHECK_FOR_UNPARSED_ARGUMENTS`).  The
  default value is `WARNING` which results in simply printing a warning but
  allow configure to complete.  This allows one to see the warnings but for
  the project to continue to work as before.  But this can be changed to
  `SEND_ERROR` or `FATAL_ERROR` that will fail the configure.

## 2017-06-24

* **Added:** TriBITS CTest Driver: Add new all-at-once mode for `ctest -S`
  driver scripts using `TRIBITS_CTEST_DRIVER()` by setting the variable
  `${PROJECT_NAME}_CTEST_DO_ALL_AT_ONCE=TRUE`.  This works with older versions
  of CMake/CTest and CDash but, by default, will just return a single glob of
  results, not breaking-out results on a package-by-package basis.  Therefore,
  this is disabled by default and package-by-package mode is used by default.
  But if `${PROJECT_NAME}_CTEST_USE_NEW_AAO_FEATURES=TRUE` is set, then
  TriBITS will take advantage of new CMake, CTest, and CDash features
  (currently on a branch) to display the results on CDash broken down
  package-by-package.  Once these changes are merged to the CMake/CTest and
  CDash 'master' branches, then the default for
  `${PROJECT_NAME}_CTEST_USE_NEW_AAO_FEATURES` will be set to `TRUE`
  automatically when it detects an updated version of CMake/CTest is present.
  In the future, at some point, the TriBITS default for
  `${PROJECT_NAME}_CTEST_DO_ALL_AT_ONCE` will change from `FALSE` to `TRUE`
  since that is a much more efficient way to drive automated testing.

## 2017-05-25

* **Added/Deprecated:** TriBITS Core: The usage of `PARSE_ARGUMENTS()` has
  been deprecated and replaced by `CMAKE_PARSE_ARGUMENTS()` everywhere in
  TriBITS. Any call to `PARSE_ARGUMENTS()` will warn users and tell them to
  use `CMAKE_PARSE_ARGUMENTS()` instead.

## 2017-05-17

* **Changed:** TriBITS Core: TriBITS now unconditionally sets
  `${PROJECT_NAME}_ENABLE_Fortran_DEFAULT` to `ON`.  Projects will now need to
  put in special logic to set to `OFF` or `ON` for certain platforms.

## 2017-01-11

* **Changed/Fixed:** TriBITS Core: TriBITS now correctly sets the default
  value for DART_TESTING_TIMEOUT to 1500 seconds and will scale it by
  `<Project>_SCALE_TEST_TIMEOUT` even if `DART_TESTING_TIMEOUT` is not
  explicitly set.

## 2016-12-07

* **Removed:** TriBITS Core: The long deprecated variable
  `${PROJECT_NAME}_ENABLE_SECONDARY_STABLE_CODE` has been removed.  Upgrading
  existing TriBITS projects just requires a simple string replacement of
  `_ENABLE_SECONDARY_STABLE_CODE` with `_ENABLE_SECONDARY_TESTED_CODE` in all
  files.  Since Trilinos has turned on ST code by default and many other
  TriBITS projects don't differentiate between PT and ST code, this change
  should not even break those projects, even if they don't update.

## 2016-11-02

* **Added/Changed/Removed:** TriBITS Python Utils: gitdist now accepts
  `--dist-repos` and `--dist-not-repos` arguments and requires that the base
  repo '.' be explicitly listed in the `.gitdist[.default]` files and in
  `--dist-repos`.  The arguments `--dist-extra-repos`,
  `--dist-not-extra-repos` and `--dist-not-base-repo` are not longer
  supported.  See `gitdist --help` for more details.

* **Changed:** TriBITS projects now install with full RPATH set by default
  (see "Setting install RPATH" in build reference guide).

## 2016-10-22

* **Changed:** TriBITS Core: `TRIBITS_ADD_TEST()` argument for
  `FAIL_REGULAR_EXPRESSION` now works when circular RCP detection is enabled.
  This is technically a break in backward compatibility since now that
  argument will not be ignored and any tests that specified this may change
  behavior.

* **Changed:** TriBITS Core: `TRIBITS_ADD_ADVANCED_TEST()` block `TEST_<IDX>`
  argument `FAIL_REGULAR_EXPRESSION` now works.  Before, it was just being
  ignored.  This is technically a break in backward compatibility since now
  that argument will not be ignored and any tests that specified this may
  change behavior.

* **Added/Changed:** TriBITS Core: Added `TRIBITS_ADD_ADVANCED_TEST()` block
  `TEST_<IDX>` option `WILL_FAIL` that has the same behavior as the built-in
  CTest option `WILL_FAIL`.  Note that this technically can break backward
  compatibility since `WILL_FAIL` may have been interpreted to be a value from
  another argument and now will not.

## 2016-01-22

* **Added/Deprecated:** TriBITS Core: Change test category `WEEKLY` to `HEAVY`
  and depreciate `WEEKLY`.  You can still use `WEEKLY` but it will result in a
  lot of warnings.

## 2015-12-03

* **Added:** TriBITS CI Support: `checkin-test.py`: Added support for tracking
  branches for each repo independently and not assume 'origin' and not assume
  that all of the repos are on the same branch or will be pulling and pushing
  to the same remote branch.  This will make it easier to use the
  `checkin-test.py` script to set up various integration scenarios.  See
  TriBITSPub/TriBITS#15 for details.

## 2015-04-14

* MAJOR: TriBITS Core: When configuring with
    ${PROJECT_NAME}_ENABLE_CXX11=ON, if C++11 support cannot be verified, then
    the configure will fail hard right away.  Before, TriBITS would disable
    C++11 support and continue.

## 2014-11-22

* **Added:** TriBITS Core: Added `${PROJECT_NAME}_TRACE_ADD_TEST`: Now you can
  print a single line to STDOUT if a test got added (and its important
  properties) or not and if not then why the test did not get added.

## 2014-09-22

* **Changed:** TriBITS Core: Changed minimum version of CMake from 2.7 to
  2.8.11.

## 2014-09-21

* **Added:** TriBITS Dashboard Driver: Added support for the env var
  `TRIBITS_TDD_USE_SYSTEM_CTEST` so that if equal to `1`, then the TriBITS
  Dashboard Driver (TDD) system will use the CTest (and CMake) in the env will
  be used instead of being downloaded using `download-cmake.py`.  This not
  only speeds up the automated builds, but it also ensures that the automated
  testing uses exactly the install of CMake/CTest that is used by the
  developers on the system.  Also, it has been found that `download-cmake.py`
  will download and install a 32bit version even on 64bit machines.

<!--

LocalWords: Fortran cmake CMake CMAKE ctest CTest CTEST CDash
LocalWords:  MAKEFILES refactoring tribits TriBITS TriBITSPub trilinos Trilinos
LocalWords: INSTANTIATION STDOUT gitdist

-->