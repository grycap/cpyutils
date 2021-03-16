# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import re
import logging

_LOGGER = logging.getLogger("[EVAL]")
_LOGGER.level = logging.INFO

class ErrorInExpression(Exception): pass
class UndefinedVar(Exception): pass
class TypeException(Exception): 
    def __init__(self, s = ""):
        self._s = s
    def __str__(self):
        return "TypeException (%s)" % self._s

def TypedDict2Str(d):
    retval = ""
    if d is None:
        return retval
    
    for k, v in list(d.items()):
        if isinstance(v, TypedClass):
            if v.type == TypedClass.STRING:
                retval = "%s%s=\"%s\";" % (retval, k, v.get())
            else:
                retval = "%s%s=%s;" % (retval, k, v.get())
        elif isinstance(v,int) or isinstance(v,float):
            retval = "%s%s=%s;" % (retval, k, v)
        else:
            retval = "%s%s=\"%s\";" % (retval, k, v)
    return retval

class TypedClass(object):
    UNKNOWN = -1
    STRING = 0
    NUMBER = 1
    BOOLEAN = 2
    LIST = 3

    @staticmethod
    def auto(v):
        if v is None:
            return TypedClass(None, TypedClass.UNKNOWN)
        if isinstance(v, list):
            return TypedList(v)
        try:
            f = float(v)
            try:
                e = int(v)
            except ValueError:
                e = f
            if (e == f):
                v = e
            else:
                v = f
            return TypedClass(v, TypedClass.NUMBER)
        except ValueError:
            if len(v)>2 and v[0]=='[' and v[-1]==']':
                l_contents = ",%s" % v[1:-1]
                l_items = []
                expr = re.compile("^,(?P<value>(\"(\\.|[^\"])*\"|[^,]*)*)")
                result = expr.search(l_contents)
                
                while result is not None:
                    l_items.append(TypedClass.auto(result.group('value')))
                    l_contents = l_contents[result.end():]
                    result = expr.search(l_contents)
                    
                return TypedList(l_items)

            b = str(v).lower()
            if b == 'true':
                return TypedClass(True, TypedClass.BOOLEAN)
            elif b == 'false':
                return TypedClass(False, TypedClass.BOOLEAN)

            return TypedClass(str(v), TypedClass.STRING)
    
    def __init__(self, v, t = -1):
        self.value = v
        self.type = t
        
    def __str__(self):
        return "%s (tipo %s) " % (str(self.value), self.type)
    
    def get(self):
        if self.type == self.STRING:
            return str(self.value)
        return self.value
    
    def __eq__(self, v):
        try:
            v.type
        except:
            return False
        if v.type != self.type: return False
        return v.value == self.value

class TypedList(TypedClass):
    def __init__(self, v):
        TypedClass.__init__(self, v, TypedClass.LIST)

    def get(self):
        ret = []
        for v in self.value:
            ret.append(v.get())
        return ret
        
    def __str__(self):
        retval = "[ "
        comma = ""
        for v in self.value:
            retval = "%s%s%s" % (retval, comma, v)
            comma = ", "
        retval = "%s ]" % retval
        return retval
        return "%s (tipo %s) " % (str(self.value), self.type)
    
class TypedNumber(TypedClass):
    def __init__(self, v):
        try:
            f = float(v)
            try:
                e = int(v)
            except ValueError:
                e = f
            if (e == f):
                v = e
            else:
                v = f
            TypedClass.__init__(self, v, TypedClass.NUMBER)
        except ValueError:
            TypedClass.__init__(self, str(v), TypedClass.STRING)

def vars_from_string(s):
    variables = {}
    s=";%s" % s.strip().strip(";")
    expr = re.compile(r'^;(?P<key>[a-zA-Z][a-zA-Z_0-9]*)=(?P<value>(\"(\\.|[^\"])*\"|[^;]*)*)')
    result = expr.search(s)
    while result is not None:
        variables[result.group('key')]=TypedClass.auto(result.group('value'))
        s = s[result.end():]
        result = expr.search(s)
    if len(s)>0:
        raise ErrorInExpression()
    return variables

def vars_from_string_(s):
    s=s.strip()
    while len(s) > 0:
        eq_pos = s.find('=')
        if eq_pos > -1:
            key = s[:eq_pos]
            
            val=None
            rest = s[eq_pos+1:]
            quot_pos = rest.find('"')
            if quot_pos > -1:
                str_beg = quot_pos
                str_end = rest.find('"', quot_pos+1)
                if str_end == -1:
                    # The quote is not closed, so we assume that it is a whole string
                    val = rest[str_beg:]
                    rest = ""
                else:
                    # We remove the quotes
                    val = rest[str_beg+1:str_end]
                    rest = rest[str_end+1:]
                    
            col_pos = rest.find(';')
            if val is None:
                val = rest[:col_pos]
                rest = rest[col_pos:]
                col_pos = 0
                
            if (col_pos != 0) and (len(rest)>0):
                raise ErrorInExpression()
            
            print(key, val, "rest:", rest)

        s = rest    


class Analyzer:
    def __init__(self, autodefinevars = True, **kwargs):
        import ply.lex as lex
        import ply.yacc as yacc
        self.lexer = lex.lex(module=self, debug=0, optimize=1, **kwargs)
        self.yacc = yacc.yacc(module=self, debug=0, optimize=1)
        self._VAR_VALUES = {}
        self._autodefine_vars = autodefinevars
        self._current_expr = ""

    def check(self, expr):
        self._current_expr = expr
        return self.yacc.parse(expr, debug=0, lexer=self.lexer)

    def clear_vars(self):
        self._VAR_VALUES = {}

    def get_vars(self):
        return self._VAR_VALUES

    def add_vars(self, _vars, clear = False):
        if clear:
            self.clear_vars()
            
        for k, v in list(_vars.items()):
            self._VAR_VALUES[k] = v

    tokens = (
        'NUMBER','VAR','COMMA','SQ_LPAREN','SQ_RPAREN','LPAREN','RPAREN',
        'TRUE','FALSE','IN','SUBSET','EQ','LT','GT','LE','NE','GE','AND','OR','EQUALS','STRING','NOT',
        'PLUS', 'DIVIDE', 'MINUS', 'TIMES', 'SEPARATOR')
    reserved = { 'in': 'IN', 'true':'TRUE', 'false':'FALSE', 'not':'NOT', 'and':'AND', 'or':'OR', 'subset': 'SUBSET'}

    literals = [ '!']

    # Tokens
    t_SEPARATOR = r'\;'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r'\,'
    t_SQ_LPAREN = r'\['
    t_SQ_RPAREN = r'\]'
    t_AND = r'\&\&'
    t_OR = r'\|\|'
    t_EQ = r'\=\='
    t_LT = r'\<'
    t_GT = r'\>'
    t_LE = r'\<\='
    t_GE = r'\>\='
    t_NE = r'\!\='

    def t_STRING(self,t):
        r'"[^\"]*"'
        t.value = t.value[1:-1]
        return t
        
    def t_NUMBER(self, t):
        r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(kb|gb|mb|tb|pb|Kb|Gb|Mb|Tb|Pb)?'
        if re.match(r'^(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(kb|gb|mb|tb|pb|Kb|Gb|Mb|Tb|Pb)?$',t.value):
            multiplyer = 1
            try:
                suffix = (t.value[-2:]).lower()
                if suffix in ['kb']:
                    multiplyer = 1024
                elif suffix in ['mb']:
                    multiplyer = 1024*1024
                elif suffix in ['gb']:
                    multiplyer = 1024*1024*1024
                elif suffix in ['tb']:
                    multiplyer = 1024*1024*1024*1024
                elif suffix in ['pb']:
                    multiplyer = 1024*1024*1024*1024*1024
                
                if multiplyer > 1:
                    t.value = t.value[:-2]
            except:
                pass
            
            try:
                f = float(t.value)
                try:
                    e = int(t.value)
                except ValueError:
                    e = f
                    
                if (e == f):
                    t.value = multiplyer*e
                else:
                    t.value = multiplyer*f
            except ValueError:
                _LOGGER.error("el valor %s no es un numero valido" % t.value)
                t.value = 0
        else:
            t.type = 'STRING'
            
        return t
        
    def t_VAR(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.lower(), 'VAR')
        return t

    def _init_vars(self, v1, v2):
        if v1.type == TypedClass.UNKNOWN:
            if v2.type == TypedClass.LIST:
                v1.value = []
            elif v2.type == TypedClass.BOOLEAN:
                v1.value = False
            elif v2.type == TypedClass.NUMBER:
                v1.value = 0
            elif v2.type == TypedClass.STRING:
                v1.value = ""
            else:
                v1.value = None
            v1.type = v2.type

        if v2.type == TypedClass.UNKNOWN:
            if v1.type == TypedClass.LIST:
                v2.value = []
            elif v1.type == TypedClass.BOOLEAN:
                v2.value = False
            elif v1.type == TypedClass.NUMBER:
                v2.value = 0
            elif v1.type == TypedClass.STRING:
                v2.value = ""
            else:
                v2.value = None
            v2.type = v1.type

    t_ignore = " \t\n"

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('right', 'NOT'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
    )


    def p_kwl_statement(self, p):
        ''' kwl : statement
        '''
        _LOGGER.debug("kwl -> statement")
        p[0] = p[1]

    def p_kwl_empty(self, p):
        ''' kwl : 
        '''
        _LOGGER.debug("kwl -> ")
        p[0] = TypedClass(None, TypedClass.UNKNOWN)
    
    def p_kwl_kwl(self, p):
        ''' kwl : kwl SEPARATOR kwl 
        '''
        _LOGGER.debug("kwl -> kwl ; kwl")
        if p[3] is not None:
            p[0] = p[3]
        elif p[1] is not None:
            p[0] = p[1]
        else:
            p[0] = TypedClass(None, TypedClass.UNKNOWN)
            
    def p_statement_assign(self, p):
        ''' statement : VAR EQUALS expression
        '''
        _LOGGER.debug("statement -> VAR '=' expression")
        self.add_vars({p[1]: p[3]})

    def p_statement_expr(self, p):
        ''' statement : expression
        '''
        _LOGGER.debug("statement -> expression")
        p[0] = p[1]

    def p_statement_notexpr(self, p):
        ''' expression  : NOT expression
                        | '!' expression
        '''
        _LOGGER.debug("expresion -> ! expression")
        if p[2].type == TypedClass.BOOLEAN: 
            p[0] = TypedClass(not p[2].value, TypedClass.BOOLEAN)
        else:
            raise TypeError("operator invalid for this type")

    def p_expression_boolop(self, p):
        """
        expression : expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression AND expression
                  | expression OR expression
        """
        _LOGGER.debug("expresion -> expresion %s expression" % p[2])
        if self._autodefine_vars:
            self._init_vars(p[1], p[3])

        if p[1].type != p[3].type: raise TypeError()

        if p[1].type == TypedClass.LIST:
            raise TypeError("operator not defined for lists")
        if p[1].type == TypedClass.STRING:
            if p[2] == '==':
                p[0] = TypedClass(p[1].value == p[3].value, TypedClass.BOOLEAN)
            elif p[2] == '!=':
                p[0] = TypedClass(p[1].value != p[3].value, TypedClass.BOOLEAN)
            else:
                raise TypeError("operator not defined for strings")

        if p[2] == '>':
            p[0] = TypedClass(p[1].value > p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '<':
            p[0] = TypedClass(p[1].value < p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '>=':
            p[0] = TypedClass(p[1].value >= p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '<=':
            p[0] = TypedClass(p[1].value <= p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '==':
            p[0] = TypedClass(p[1].value == p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '!=':
            p[0] = TypedClass(p[1].value != p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '&&':
            p[0] = TypedClass(p[1].value and p[3].value, TypedClass.BOOLEAN)
        elif p[2] == '||':
            p[0] = TypedClass(p[1].value or p[3].value, TypedClass.BOOLEAN)


    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
        """
        _LOGGER.debug("expresion -> expresion %s expression" % p[2])

        if self._autodefine_vars:
            self._init_vars(p[1], p[3])

        if p[1].type != p[3].type: raise TypeError()
        
        if p[1].type == TypedClass.LIST:
            if p[2] == '+':
                p[0] = TypedList(p[1].value + p[3].value)
            else:
                raise TypeError('operator not defined for lists')
        elif p[1].type == TypedClass.STRING:
            if p[2] == '+':
                p[0] = TypedClass(p[1].value + p[3].value, TypedClass.STRING)
            else:
                raise TypeError('operator not defined for strings')
        elif p[1].type == TypedClass.NUMBER: 
            if p[2] == '+':
                p[0] = TypedClass(p[1].value + p[3].value, TypedClass.NUMBER)
            elif p[2] == '-':
                p[0] = TypedClass(p[1].value - p[3].value, TypedClass.NUMBER)
            if p[2] == '*':
                p[0] = TypedClass(p[1].value * p[3].value, TypedClass.NUMBER)
            if p[2] == '/':
                p[0] = TypedClass(p[1].value / p[3].value, TypedClass.NUMBER)
        else:
            raise TypeError("operator invalid for this type")

    def p_expression_inlist(self, p):
        ''' expression    :   expression IN lexp 
        '''
        _LOGGER.debug("expresion -> expresion IN lexp")

        if self._autodefine_vars:
            self._init_vars(TypedList([]), p[3])

        if p[3].type != TypedClass.LIST: raise TypeError("expected list for IN operator")
        
        retval = False
        for v in p[3].value:
            if p[1] == v:
                retval = True
                break
        
        p[0] = TypedClass(retval, TypedClass.BOOLEAN)
    
    def p_expression_invar(self, p):
        ''' expression    :   expression IN VAR 
        '''
        _LOGGER.debug("expresion -> expresion IN VAR")
    
        if p[3] not in self._VAR_VALUES:
            if self._autodefine_vars:
                self._VAR_VALUES[p[3]] = TypedList([])
            else:
                raise TypeError("list expected for IN operator")
            
        l = self._VAR_VALUES[p[3]]
        if l.type != TypedList.LIST: raise TypeError("list expected for IN operator")
        p[3] = l
        
        self.p_expression_inlist(p)


    def p_expression_subsetlist(self, p):
        ''' expression    :   expression SUBSET lexp 
        '''
        _LOGGER.debug("expresion -> expresion SUBSET lexp")
    
        if p[1].type != TypedClass.LIST: raise TypeError("lists expected for SUBSET operator")
        if p[3].type != TypedClass.LIST: raise TypeError("lists expected for SUBSET operator")
        
        retval = True
        for vl in p[1].value:
            found = False
            for vr in p[3].value:
                if vl == vr:
                    found = True
                    break
            if not found:
                retval = False
                break
        
        p[0] = TypedClass(retval, TypedClass.BOOLEAN)
    
    def p_expression_subsetvar(self, p):
        ''' expression    :   expression SUBSET VAR 
        '''
        _LOGGER.debug("expresion -> expresion SUBSET VAR")
    
        if p[3] not in self._VAR_VALUES:
            if self._autodefine_vars:
                self._VAR_VALUES[p[3]] = TypedList([])
            else:
                raise TypeError("lists expected for SUBSET operator")
            
        l = self._VAR_VALUES[p[3]]
        if l.type != TypedList.LIST: raise TypeError("lists expected for SUBSET operator")
        p[3] = l
        
        self.p_expression_subsetlist(p)

    def p_expression_uminus(self, p):
        ''' expression  :   MINUS expression %prec UMINUS
        '''
        _LOGGER.debug("expresion -> - expresion")

        if p[2].type == TypedClass.NUMBER: 
            p[0] = TypedClass(-p[2].value, TypedClass.NUMBER)
        else:
            raise TypeError("operator invalid for this type")

    def p_expression_group(self, p):
        ''' expression  :   LPAREN expression RPAREN
        '''
        _LOGGER.debug("expresion -> ( expresion )")

        p[0] = p[2]

    def p_expression_term(self, p):
        ''' expression : term
        '''
        _LOGGER.debug("expresion -> term")

        p[0] = p[1]

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def p_lexp_def(self, p):
        ''' lexp    :   SQ_LPAREN l SQ_RPAREN
        '''
        _LOGGER.debug("lexp -> [ l ]")
        p[0] = p[2]
    
    def p_l_empty(self, p):
        ''' l       :   
        '''
        _LOGGER.debug("l -> ")

        p[0] = TypedList( [] )
    
    def p_l_expression(self, p):
        ''' l       :   expression    
        '''
        _LOGGER.debug("l -> expresion")

        l = TypedList( [ p[1] ] )
        p[0] = l
        
    def p_l_comma_l(self, p):
        ''' l       :   expression COMMA l
        '''
        _LOGGER.debug("l -> expresion , l")

        if p[3].type != TypedClass.LIST: raise TypeError("list expected")
        l = TypedList( [ p[1] ] + p[3].value)
        p[0] = l

    def p_term_var(self, p):
        ''' term   :    VAR 
        '''
        _LOGGER.debug("term -> VAR")
        
        # TODO: determine the type of the var
        if p[1] not in self._VAR_VALUES:
            if self._autodefine_vars:
                self._VAR_VALUES[p[1]] = TypedClass(None, TypedClass.UNKNOWN)
                
        if p[1] in self._VAR_VALUES:
            _LOGGER.debug("term -> VAR")
            p[0] = self._VAR_VALUES[p[1]]
        else:
            raise UndefinedVar()
    
    def p_term_bool(self, p):
        ''' term    :   TRUE
                    |   FALSE 
        '''
        _LOGGER.debug("term -> TRUE/FALSE")

        if p[1].lower() == 'true':
            p[0] = TypedClass(True, TypedClass.BOOLEAN)
        else:
            p[0] = TypedClass(False, TypedClass.BOOLEAN)
        
    def p_term_num(self, p):
        ''' term    :   NUMBER 
        '''
        _LOGGER.debug("term -> NUM")
        
        p[0] = TypedNumber(p[1])
    
    def p_term_lexp(self, p):
        ''' term    :   lexp 
        '''
        _LOGGER.debug("term -> lexp")
        
        p[0] = p[1]
        
    def p_term_string(self, p):
        ''' term    :   STRING 
        '''
        _LOGGER.debug("term -> STRING")
        
        p[0] = TypedClass(p[1], TypedClass.STRING)

    def p_term_empty(self, p):
        ''' term    :   
        '''
        _LOGGER.debug("term -> ")

        p[0] = TypedClass(None, TypedClass.UNKNOWN)

if __name__ == '__main__':
    logging.basicConfig(filename=None,level=logging.DEBUG)
    
    keywords={'queues': ['all.q',''], 'hostname': 'vnode10.localdomain', 'hostgroups': []}
    
    
    annie = Analyzer(autodefinevars=False)
    keywords = vars_from_string('queues=[all.q];hostname="vnode10.localdomain";')
    keywords = { 'queues': TypedList([TypedClass.auto("all.q")]), 'hostname': TypedClass.auto("vnode10.localdomain")}
    annie.add_vars(keywords, True)
    print(annie.check(' "all.q" in queues '))
    print(annie.check('hostname=="all.q"'))
    print(annie.check('hostname=="vnode10.localdomain"'))
    exit()
    
    e=vars_from_string('jobs=;sessions=1181;ncpus=4;physmem=3922492kb;ppn=4;netload=20083230506;uname="Linux ngieswnv1 2.6.32-431.29.2.el6.x86_64 #1 SMP Tue Sep 9 13:45:55 CDT 2014 x86_64";nsessions=1;properties=["lcgpro"];gres=;nusers=1;idletime=521677;queues=["chemig","tutig","dteam","biomed","ops","ictig","earthig","opsig","lifeig","rollout","engig","socialig","physig"];hostname="ngieswnv1";varattr=;loadave=0.00;state="free";opsys="linux";totmem=5986872kb;availmem=5827616kb;rectime=1417717220;')
    for k,v in list(e.items()):
        print(k,v)
    exit()
    annie = Analyzer(True)
    print(annie.check('hostname="pbsnode01";rectime=1416575227;varattr=;jobs=;state=free;netload=315839;gres=;loadave=0.00;ncpus=1;physmem=503484kb;availmem=445812kb;totmem=503484kb;idletime=1173;nusers=2;nsessions=2;sessions="1070 1002";uname="Linux pbsnode01 3.2.0-64-virtual #97-Ubuntu SMP Wed Jun 4 22:16:47 UTC 2014 x86_64";opsys=linux;queues=[];properties=["q1"];'))
    # print annie.check('rectime=1416564377;varattr=;jobs=;state=free;netload=207353;gres=;loadave=0.00;ncpus=1;physmem=503484kb;availmem=446368kb;totmem=503484kb;idletime=634;nusers=2;nsessions=3;sessions="1113 1068 1223";uname="Linux pbsnode01 3.2.0-64-virtual #97-Ubuntu SMP Wed Jun 4 22:16:47 UTC 2014 x86_64";opsys=linux;queues=[];')
    for k,v in list(annie.get_vars().items()):
        print("%s = %s" % (k, v.get()))

    exit()
