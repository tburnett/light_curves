"""
Extracted from jupydoc to support single-cell output with nbdev
Usage:

from utilities import nbdoc

def doc():
    ''' text to show, with {} strings.
    '''
    # code
nbdev(doc)

"""
import sys, os, shutil, string, pprint


def doc_formatter(
        text:'text string to process',
        vars:'variable dict'={}, 
        mimetype='text/markdown',
    )->'MimeBundleObject':
    # Returns an object that can be displayed by IPython, interpreted as the mimetype

    # Use a string.Formatter subclass to ignore bracketed names that are not found
    #adapted from  https://stackoverflow.com/questions/3536303/python-string-format-suppress-silent-keyerror-indexerror

    class Formatter(string.Formatter):
        class Unformatted:
            def __init__(self, key):
                self.key = key
            def format(self, format_spec):
                return "{{{}{}}}".format(self.key, ":" + format_spec if format_spec else "")

        def vformat(self, format_string,  kwargs):
            try:
                return super().vformat(format_string, [], kwargs)
            except AttributeError as msg:
                return f'Docstring formatting failed: {msg.args[0]}'
        def get_value(self, key, args, kwargs):
            return kwargs.get(key, Formatter.Unformatted(key))

        def format_field(self, value, format_spec):
            if isinstance(value, Formatter.Unformatted):
                return value.format(format_spec)
            #print(f'\tformatting {value} with spec {format_spec}') #', object of class {eval(value).__class__}')
            return format(value, format_spec)
               
    docx = Formatter().vformat(text+'\n', vars)  if vars else text     
    # enhances this: docx = text.format(**vars)

    class MimeBundleObject(object):
        def _repr_mimebundle_(self, include=None, exclude=None):
            return {mimetype: docx}

    return MimeBundleObject()


#---------------------------------------------------------------------------------


def monospace(text:'Either a string, or an object',
                summary:'string for <details>'=None,
                open:'initially show details'=False, 
                indent='5%',
                )->str:

    text = str(text).replace('\n', '<br>')
    out = f'<p style="margin-left: {indent}"><pre>{text}</pre></p>'
    if not summary:
        return out
    return f'<details {"open" if open else ""}><summary> {summary} </summary> {out} </details>'
    
def shell(text:'a shell command ', mono=True, **kwargs):
    import subprocess
    try:
        ret = subprocess.check_output([text], shell=True).decode('utf-8')
    except Exception as e:
        ret = f'Command {text} failed : {e}'
    return monospace(ret, **kwargs) if mono else ret

def capture_print( **kwargs):


    class Capture_print(object):
        _stream = 'stdout'
        
        def __init__(self):
            import io
            self._new = io.StringIO()
            self._old = getattr(sys, self._stream)

        def __enter__(self):
            setattr(sys, self._stream, self._new)
            return self
        
        def __exit__(self, exctype, excinst, exctb):
            setattr(sys, self._stream, self._old)
            
        def __str__(self):
            return monospace(self._new.getvalue(), **kwargs)

    return Capture_print()


"""
This defines a jupydoc helper which manages creation of HTML for objects of selected classes
 
For such classes, replace the object in the variable dictionary with a new one that implements a __str__ function, which returns
markdown, usually HTML.

Implemented here: dict, wrappers for plt.Figure, pd.Dataframe
"""


try:
    import matplotlib.pyplot as plt
except:
    plt=None
try: 
    import pandas as pd
except:
    pd=None


# a dict accumulated here, used to initialze set of wrappers for ObjectReplacer
wrappers = {}
                     
class Wrapper(object):
    """Base class for the replacement classes
    Itself uses the str for the object in question
    """
    def __init__(self, *pars, **kwargs):
        self.obj = pars[0]
        self.vars=pars[1]
        self.indent = kwargs.pop('indent', '5%')
        self.replacer = kwargs.pop('replacer')

    def __repr__(self): return str(self)
    def _repr_html_(self): return str(self)
    def __str__(self):
        text = str(self.obj).replace('\n', '\n<br>')
        return f'<p style="margin-left: {self.indent}"><samp>{text}</samp></p>'

if plt: 

    class FigureWrapper(Wrapper,plt.Figure):
        
        def __init__(self, *pars, **kwargs): 
            
            super().__init__(*pars, **kwargs)

            fig = self.obj
            self.__dict__.update(fig.__dict__)
            self.fig = fig
            # from kwargs
            self.folder_name=kwargs.pop('folder_name', 'figs')
            self.fig_folders=kwargs.pop('fig_folders', self.replacer.document_folders)
            # print(f'***fig_folders: {self.fig_folders}')

            self.replacer.figure_number += 1
            self.number = self.replacer.figure_number
            self.prefix = self.replacer.figure_prefix
            self.fig_class=kwargs.pop('fig_class', 'jupydoc_fig') 

            for folder in self.fig_folders:
                t = os.path.join(folder,  self.folder_name)
                os.makedirs(t, exist_ok=True)
                assert os.path.isdir(t), f'{t} not found'
                # print(f'*** saving to {t}, with prefix {self.prefix}')

        def __str__(self):
            
            if not hasattr(self, '_html') :
            
                # only has to do this once:
                fig=self.fig
                n =self.number
                prefix = self.prefix+'_' if self.prefix else ''

                # the caption, which may be absent.
                caption = getattr(fig,'caption', '')
                if caption is not None:
                    caption = f'<b>Figure {n}</b>. ' + getattr(fig,'caption', '').format(**self.vars)
                    figcaption = f' <figcaption>{caption}</figcaption>'
                else: figcaption=''

                # save the figure to a file, then close it
                fn = os.path.join(self.folder_name, f'{prefix}fig_{n:02d}.png')
                browser_fn =fn
                
                # actually save it for the document, perhaps both in the local, and document folders
                for folder in self.fig_folders:
                    fig.savefig(os.path.join(folder,fn), bbox_inches='tight', pad_inches=0.5)#, **fig_kwargs)
                plt.close(fig) 
                img_width = f'width={fig.width}' if hasattr(fig,'width') else ''

                # add the HTML as an attribute, to insert the image, including  caption
                self._html =\
                    f'<div class="{self.fig_class}">'\
                      f'<figure>'\
                        f'   <img src="{browser_fn}" alt="Figure {n} at {browser_fn}" {img_width}>'\
                        f' {figcaption}' \
                      '</figure>'\
                    '</div>\n'
            return self._html

    # def __str__(self):
    #     return str(self.img)

    wrappers['Figure'] = (FigureWrapper, {'folder_name': 'images'}) # was 'figs', but this is OK, what nbdev wants

if pd:
    class DataFrameWrapper(Wrapper): 
        def __init__(self, *pars, **kwargs):

            super().__init__(*pars, **kwargs)
            self._df = self.obj
            kwargs.pop('replacer') # rest should be OK
            self.kw = kwargs

        def __str__(self):
            if not hasattr(self, '_html'):
                self._html = self._df.to_html(**self.kw)                
            return self._html
    df_kwargs= dict( notebook=True, 
                    max_rows=6, 
                    index=False,
                    show_dimensions=False, #True, 
                    justify='right',
                    float_format=lambda x: f'{x:.3f}',
                    )
    wrappers['DataFrame'] = (DataFrameWrapper,  df_kwargs) 

class PPWrapper(Wrapper):
    """Use PrettyPrint
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=2)
        text = pp.pformat(self.obj)#.replace('\n', '<br>\n')
        return f'<p style="margin-left: {self.indent}"><samp>{text}</samp></p>'

wrappers['dict'] = (PPWrapper, {} )
wrappers['list'] = (PPWrapper, {} )

class ImageWrapper(Wrapper):
    """ Wrap IPython.display.Image
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._image = self.obj
    def __str__(self):
        return self._image._repr_mimebundle_()
# Placeholder until I figure out how IPyton does this in a notebook
# Until then, must create jpeg or png, save with the document, link in in
# wrappers['Image'] = (ImageWrapkper, {})

class ObjectReplacer(dict):
    """
    Functor that will replace objects in a variables dictionary
    It is a dictionary,
        key: a name of a class to have its instances replaced
        value: tuple with two elements: 
            1. the replacement class, which implements a __str__ method
            2. kwargs to apply to new object
    """
    def __init__(self, 
                 folders:'one or more document folders to save images'=['.'], 
                 figure_prefix:'prefix for figure filename'='',
                ):

        self.update(wrappers)
        self.set_folders(folders)
        self.figure_number=0
        self.figure_prefix = figure_prefix
        self.debug=False
        
    # def add_rep(self, class_name:'name of class to replace', 
    #                 out_class:'replacement class', 
    #                 kwargs:'Any parameters to pass to output class'={}):
    #     """
    #     add a replacement entry
    #     """
    #     self[class_name] = (out_class, kwargs)
    
    def set_folders(self, folders):
        # folder management for these guys
        #global document_folders
        self.document_folders = folders
        self.clear()

    def clear(self):
        self.figure_number= 0
 
    @property
    def folders(self):
        return self.document_folders

    def __call__(self, vars):
        """for each value in the vars dict, replace it with a new object that
        implements return of appropriate HTML for the original object
        (Note uses the *class name*, which may not be unique, as a key)
        """
        for key,value in vars.items():
            tkey = value.__class__.__name__
            if self.debug:
                print(f'{key}: {tkey} ')

            new_class, kwargs = self.get(tkey, (None,None))
            
            if new_class:
                newvalue = new_class(value, vars, replacer=self, **kwargs)
                vars[key] = newvalue
                
    def test(self, var:'any object'):
        """Test replacement for a given value. print str(var) before and after replacement
        """
        _class = var.__class__
        _name = _class.__name__
        if _name not in self:
            print(f'no subsitution for class {_name}: "{var}"')
            return

        print(f'replacement: {self[_name]}')
        print(f'{"-"*37}before{"-"*37}\n{var}\n')
        # make a simple vars dict: key is the variable name, value its object
        vars = {'x': var}
        self(vars)
        x = vars['x']
        print(f'{"-"*37}after {"-"*37}\n{x}\n{"-"*80}\n')
        return 

def test_OR(previous=20):
    # define a few figures, assign differned fignumbers
    fig1, ax1 = plt.subplots(num=1) 
    fig2, ax2 = plt.subplots(num=2) 
    
    # set up the replacer, to start after given value
    r = ObjectReplacer(previous_fignumber=previous)
    
    # set up variable dictionary
    vars = dict(fig1=fig1, fig2=fig2)
    before = (vars['fig1'].number, vars['fig2'].number)
    r(vars)
    after = (vars['fig1'].number, vars['fig2'].number)
    print(f'Figure nubers:\nbefore: {before}\nafter : {after}')
    plt.close('all')
    
    assert after[0]==previous+1,f'Failed to set number: got {after[0]}'


def nbdoc(userfun:'a function'):
    """Assume called from a jupyter cell, with a function of no args
    which has a docstring in markdown format. The code is extracted, a 
    function call appended, and then executed.
    """   
    import inspect

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import IPython.display as display

    # now defined locally
    # from jupydoc.replacer import ObjectReplacer
    # from jupydoc.helpers import doc_formatter, monospace, capture_print, shell

    # process the function's code
    source, _ = inspect.getsourcelines(userfun)
    assert source[0].startswith('def '), 'Expect first line to be a "def"'
    code = inspect.cleandoc(''.join(source[1:]))
    name = userfun.__name__

    # this object will replace references to objects that it recognizes, like "Figure"
    # It needs to know where to put image files
    ### TODO: figure out where the doc folder is. Now assume using nbs folder
    orep = ObjectReplacer(folders=['','../docs'], figure_prefix=name)
    
    # get the function's docstring, assumed to be MD
    doc = inspect.cleandoc(userfun.__doc__)
    
    # a call to this is added to end of the user code
    def _generate(name):
        # gets local symbols from calling function
        back =inspect.currentframe().f_back
        locs = inspect.getargvalues(back).locals
        
        vars = locs
        # replace variable objects if recognized
        orep(vars)
        # format the doc string> replacing recognized {name} with a str(obj), where "name" is a key to the object obj
        # in the local symbol table
        md_data = doc_formatter(doc, vars)
        # have IPython display it
        display.display( md_data )  

    # TODO: try -- except
    exec(code + f'\n_generate("{name}")', globals(), locals())
