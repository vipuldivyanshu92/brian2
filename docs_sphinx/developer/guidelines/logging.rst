.. currentmodule:: brian2

Logging
=======

Logging in Brian is based on the :mod:`logging` module in Python's standard
library. In Brian2, all logging output is logged to a file (the file name is
available in `brian2.utils.logger.TMP_LOG`). This log file will normally be
deleted on exit, except if an uncaught exception occured or if
:bpref:`delete_log_on_exit` is set to ``False``. The default log level for the
logging on the console is "warn".

Every brian module that needs logging should start with the following line,
using the `get_logger` function to get an instance of `BrianLogger`::

	logger = get_logger(__name__)

In the code, logging can then be done via::

	logger.debug('A debug message')
	logger.info('An info message')
	logger.warn('A warning message')
	logger.error('An error message')

If a module logs similar messages in different places or if it might be useful
to be able to suppress a subset of messages in a module, add an additional
specifier to the logging command, specifying the class or function name, or
a method name including the class name (do not include the module name, it will
be automatically added as a prefix)::

	logger.debug('A debug message', 'CodeString')
	logger.debug('A debug message', 'NeuronGroup.update')
	logger.debug('A debug message', 'reinit')

If you want to log a message only once, e.g. in a function that is called
repeatedly, set the optional ``once`` keyword to ``True``::

	logger.debug('Will only be shown once', once=True)
	logger.debug('Will only be shown once', once=True)

The output of debugging looks like this in the log file::

	2012-10-02 14:41:41,484 DEBUG    brian2.equations.equations.CodeString: A debug message

and like this on the console (if the log level is set to "debug")::

	DEBUG    brian2.equations.equations.CodeString: A debug message

Log level recommendations
-------------------------
debug
	Low-level messages that are not of any interest to the normal user but
	useful for debugging. A typical example is the source code generated by the
	code generation module.
info
	Messages that are not necessary for the user, but possibly helpful in
	understanding the details of what is going on. An example would be
	displaying a message about which stateupdater has been chosen automatically
	after analyzing the equations, when no stateupdater has been specified
	explicitly.
warn
	Messages that alert the user to a potential mistake in the code, e.g. two
	possible solutions for an identifier in an equation. It can also be used to
	make the user aware that he/she is using an experimental feature, an
	unsupported compiler or similar. In this case, normally the ``once=True``
	option should be used to raise this warning only once. As a rule of thumb,
	"common" scripts like the examples provided in the examples folder should
	normally not lead to any warnings.
error
	This log level is not used currently in Brian, an exception should be
	raised instead. It might be useful in "meta-code", running scripts and
	catching any errors that occur.

Showing/hiding log messages
---------------------------
The user can change the level of displayed log messages by using a static
method of `BrianLogger`::

	BrianLogger.log_level_info() # now also display info messages

It is also possible to suppress messages for certain sub-hierarchies by using
`BrianLogger.suppress_hierarchy`::

	# Suppress code generation messages on the console
	BrianLogger.suppress_hierarchy('brian2.codegen')
	# Suppress preference messages even in the log file
	BrianLogger.suppress_hierarchy('brian2.core.preferences',
	                               filter_log_file=True)

Similarly, messages ending in a certain name can be suppressed with
`BrianLogger.suppress_name`::

    # Suppress resolution conflict warnings
    BrianLogger.suppress_name('resolution_conflict')

These functions should be used with care, as they suppresses messages
independent of the level, i.e. even warning and error messages.

Testing log messages
--------------------
It is possible to test whether code emits an expected log message using the
`~brian2.utils.logger.catch_logs` context manager. This is normally not
necessary for debug and info messages, but should be part of the unit tests
for warning messages (`~brian2.utils.logger.catch_logs` by default only catches
warning and error messages)::

    with catch_logs() as logs:
        # code that is expected to trigger a warning
        # ...
        assert len(logs) == 1
        # logs contains tuples of (log level, name, message)
        assert logs[0][0] == 'WARNING' and logs[0][1].endswith('warning_type')
