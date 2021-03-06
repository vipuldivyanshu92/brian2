'''
Base class for languages, gives the methods which should be overridden to
implement a new language.
'''
import functools

from brian2.utils.stringtools import get_identifiers, deindent

from ..specifiers import ArrayVariable
from ..templating import apply_code_template
from ..functions import UserFunction


__all__ = ['Language', 'CodeObject']

class Language(object):
    '''
    Base class for all languages.
    
    See definition of methods below.
    
    TODO: more details here
    '''
    
    # Subclasses should override this
    language_id = ''
    
    def translate_expression(self, expr):
        '''
        Translate the given expression string into a string in the target
        language, returns a string.
        '''
        raise NotImplementedError
    
    def translate_statement(self,statement):
        '''
        Translate a single line Statement into the target language, returns
        a string.
        '''
        raise NotImplementedError

    def translate_statement_sequence(self, statements, specifiers):
        '''
        Translate a sequence of Statements into the target language, taking
        care to declare variables, etc. if necessary.
        
        Returns either a string, in which case when it in inserted into a
        template it should go in the ``%CODE%`` slot, or a dictionary
        of pairs ``(slot, code)`` where the given ``code`` should be inserted
        in the given ``slot``. These should appear in the templates returned
        by the language.
        '''
        raise NotImplementedError
    
    def code_object(self, code):
        '''
        Return an executable code object from the given code string.
        '''
        raise NotImplementedError
    
    def compile_methods(self, specifiers):
        meths = []
        for var, spec in specifiers.items():
            if isinstance(spec, UserFunction):
                meths.append(functools.partial(spec.on_compile, language=self,
                                               var=var))
        return meths
    
    def apply_template(self, code, template):
        '''
        Applies the inner code to the template. The code should either be a
        string (in which case it goes in the ``%CODE%`` slot) or it should be
        a dict of pairs ``(slot, section)`` where the string ``section``
        goes in slot ``slot``. The template should be a string (in which case
        it is assigned to the slot ``%MAIN%`` or a dict of ``(slot, code)``
        pairs. Returns either a string (if the template was a string) or a
        dict with the same keys as the template.
        '''
        if isinstance(code, str):
            code = {'%CODE%': code}
        if isinstance(template, str):
            return_str = True
            template = {'%MAIN%': template}
        else:
            return_str = False
        output = template.copy()
        for name, tmp in output.items():
            tmp = deindent(tmp)
            for slot, section in code.items():
                tmp = apply_code_template(section, tmp, placeholder=slot)
            output[name] = tmp
        if return_str:
            return output['%MAIN%']
        else:
            return output

    def array_read_write(self, statements, specifiers):
        '''
        Helper function, gives the set of ArrayVariables that are read from and
        written to in the series of statements. Returns the pair read, write
        of sets of variable names.
        '''
        read = set()
        write = set()
        for stmt in statements:
            ids = set(get_identifiers(stmt.expr))
            # if the operation is inplace this counts as a read.
            if stmt.inplace:
                ids.add(stmt.var)
            read = read.union(ids)
            write.add(stmt.var)
        read = set(var for var, spec in specifiers.items() if isinstance(spec, ArrayVariable) and var in read)
        write = set(var for var, spec in specifiers.items() if isinstance(spec, ArrayVariable) and var in write)
        return read, write

    def template_iterate_all(self, index, size):
        '''
        Return a template where the variable ``index`` ranges from ``0:size``.
        Both ``index`` and ``size`` should be strings. Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        raise NotImplementedError
    
    def template_iterate_index_array(self, index, array, size):
        '''
        Return a template where the variable ``index`` ranges through the
        values in ``array`` which is of length ``size``, each of these should
        be a string. Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        raise NotImplementedError

    def template_state_update(self):
        '''
        Template for state updater code, by default just iterate over all neurons.
        Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        return self.template_iterate_all('_neuron_idx', '_num_neurons')
    
    def template_reset(self):
        '''
        Template for state updater code, by default just iterate over ``_spikes``.
        Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        return self.template_iterate_index_array('_neuron_idx', '_spikes', '_num_spikes')
    
    def template_threshold(self):
        '''
        Template for threshold code.
        Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        raise NotImplementedError

    def template_synapses(self):
        '''
        Template for synapses code.
        Templates should have
        slots indicated by strings like ``%CODE%`` (the default slot).
        '''
        raise NotImplementedError
    

class CodeObject(object):
    '''
    Executable code object, returned by Language
    
    Code object is initialised by Language object, typically just by doing
    ``CodeObject(code)``. The ``code`` can either be a string, or a dict
    of ``(name, code)`` pairs if there are multiple elements of the code.
    
    After initialisation, the code is compiled with the given namespace
    using ``code.compile(namespace)``.
    
    Calling ``code(key1=val1, key2=val2)`` executes the code with the given
    variables inserted into the namespace.
    '''
    def __init__(self, code, compile_methods=[]):
        self.code = code
        self.compile_methods = compile_methods
    
    def compile(self, namespace):
        self.namespace = namespace
        for meth in self.compile_methods:
            meth(namespace)
    
    def __call__(self, **kwds):
        raise NotImplementedError
