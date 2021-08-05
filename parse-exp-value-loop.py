'''
This program implements a recursive descent parser for the CFG below:

Syntax Rule  Lookahead Set          Strings generated
------------------------------------------------------------
1 <exp> → <term>{+<term> | -<term>}
2 <term> → <factor>{*<factor> | /<factor>}
3 <factor> → (<exp>) | <number> | <func>
4.<func> → <name>(<exp>)
5 <name> → sqrt|sin|cos|tan|abs|exp
'''
import math
from typing import Match

class ParseError(Exception): pass

#=======================================================
#   Define a Node class
#
class Node:
    def __init__(self, data, left = None, right = None):
        self.left = left
        self.right = right
        self.data = data
#=======================================================

#==============================================================
# FRONT END PARSER
#==============================================================

i = 0 # keeps track of what character we are currently reading.
err = None
#---------------------------------------
# Parse an Expression   <exp> → <term>{+<term> | -<term>}
#

val = {'+': 'ADD', '-':'SUB', '*':'MUL', '/':'DIV', 'sin':'SIN', 'cos':'COS', 
            'tan':'TAN', 'exp':'EXP', 'sqrt':'SQRT', 'abs':'ABS', 
            'assign': 'ASSIGN'}

symbol_table = {}

def Lisp(n): 
    if n.right == None:  
        if n.left == None:
            return n.data
        else:
            return  n.left.data + ' ' + Lisp(n.right.data)
            
    if n.data == 'call':        
        return '(' + Lisp(n.left) + ' ' + Lisp(n.right) + ')'
    elif n.data == 'assign':
        return '(= ' + Lisp(n.left) + ' ' + Lisp(n.right) + ')'
    else:
        return '(' + n.data + ' ' + Lisp(n.left) + ' ' + Lisp(n.right) + ')'

def Prefix(n): 
    if n.right == None:  
        if n.left == None:
            return n.data
        else:
            return  n.left.data + ' ' + Prefix(n.right.data)

    if n.data == 'call':        
        return  Prefix(n.left) + ' ' + Prefix(n.right)
    elif n.data == 'assign':
        return  '= ' + Prefix(n.left) + ' ' + Prefix(n.right)
    else:
        return str(n.data) + ' ' + Prefix(n.left) + ' ' + Prefix(n.right)

def RPN(n): 
    if n.right == None:  
        if n.left == None:
            return n.data
        else:
            return  RPN(n.right.data) + ' ' + n.left.data

    if n.data == 'call':
        return RPN(n.right) + ' ' + RPN(n.left)
    elif n.data =='assign':
        return  RPN(n.right) + ' ' + RPN(n.left) + ' ='
    else:
        return RPN(n.left) + ' ' + RPN(n.right) + ' ' + str(n.data)
        
def Func(n): 
    if n.right == None:  
        if n.left == None:
            return n.data
        else:
            return  val[n.left.data] + '(' + Func(n.right.data) + ')'

    if n.data == 'call':
        return  Func(n.left) + '(' + Func(n.right) + ')'
    else:
        return val[n.data] + '(' + Func(n.left) + ', ' + Func(n.right) + ')'

def exp():
    global i, err
    value = term()
    while True:
        if w[i] == '+':
            i += 1
            value = binary_op('+', value, term())
        elif w[i] == '-':
            i += 1
            value = binary_op('-', value, term())
        else:
            break

    return value
#---------------------------------------
# Parse a Term   <term> → <factor>{+<factor> | -<factor>}
#
def term():
    global i, err

    value = factor()
    while True:
        if w[i] == '*':
            i += 1
            value = binary_op('*', value, factor())
        elif w[i] == '/':
            i += 1
            value = binary_op('/', value, factor())
        else:
            break

    return value
#---------------------------------------
# Parse a Factor   <factor> → (<exp>) | <number> 
#       
def factor():
    global i, err
    value = None
    if w[i] == '(':
        i += 1          # read the next character
        value = exp()
        if w[i] == ')':
            i += 1
            return value
        else:
            print('missing )')
            raise ParseError
    elif w[i] in ('sqrt', 'sin', 'cos', 'tan', 'abs', 'exp'):
        fname = w[i]
        i += 1
        if w[i] == '(':
            i += 1 
            param = exp()
            if w[i] == ')':
                i += 1
            else:
                print('missing )')
                raise ParseError
        value = funcCall(fname, param)
        return value
    elif w[i] == 'pi':
        i += 1
        value = atomic(str(math.pi))          # read the next character
        return value
    else:
        try:
            value = atomic(w[i])
            i += 1          # read the next character
        except ValueError:
            print('number expected')
            value = None
    
    #print('factor returning', value)
    
    if value == None: raise ParseError
    return value


#==============================================================
# BACK END PARSER (ACTION RULES)
#==============================================================

def binary_op(op, lhs, rhs):
    if op == '+': return Node('+', lhs, rhs)
    elif op == '-': return Node('-', lhs, rhs)
    elif op == '*': return Node('*', lhs, rhs)
    elif op == '/': return Node('/', lhs, rhs)
    else: return None

def atomic(x):
    return Node(x)

def Eval(n):
    if n.left == None and n.right == None:
        try:
            return float(n.data)
        except:
            if str(n.data) in symbol_table:
                return symbol_table[n.data]
            else: print("parse error: float literal or variable expected")
    elif n.data == 'assign':
        val = Eval(n.right)
        symbol_table[n.left.data] = val 
        return str(n.left.data) + "=" + str(val)
    elif n.data == 'call':
        if n.left.data == 'sin': return math.sin(Eval(n.right))
        elif n.left.data == 'cos': return math.cos(Eval(n.right))
        elif n.left.data == 'tan': return math.tan(Eval(n.right))
        elif n.left.data == 'exp': return math.exp(Eval(n.right))
        elif n.left.data == 'sqrt': return math.sqrt(Eval(n.right))
        elif n.left.data == 'abs': return abs(Eval(n.right))   
    else:
        if n.data == '+': return Eval(n.left) + Eval(n.right)
        elif n.data == '-': return Eval(n.left) - Eval(n.right)
        elif n.data == '*': return Eval(n.left) * Eval(n.right)
        elif n.data == '/': return Eval(n.left) / Eval(n.right)

def funcCall(fname,param):
    return Node('call', Node(fname), param)

def statement():
    global i, err
    Id = w[i]
    i+=1

    if w[i] == "=":
        i+=1
        val = exp()
        value = assign(Id,val)
    else:
        i -= 1
        value = exp()

    return value

def assign(Id, val):
    nodeId = Node(Id)
    return Node('assign',nodeId, val)

#--

w = input('\nEnter expression: ')
while w != '':
    #------------------------------
    # Split string into token list.
    #
    for c in '()+-*/':
        w = w.replace(c, ' '+c+' ')
    w = w.split()
    w.append('$') # EOF marker

    print('\nToken Stream:     ', end = '')
    for t in w: print(t, end = '  ')
    print('\n')
    i = 0
    try:
        n = statement() # call the parser
    except:
        print('parse error')

    print(Lisp(n))
    print(Prefix(n))
    print(RPN(n))
    print(Func(n))
    print(Eval(n))
    print()

    if w[i] != '$': print('Syntax error:')
    print('read | un-read:   ', end = '')
    for c in w[:i]: print(c, end = '')
    print(' | ', end = '')
    for c in w[i:]: print(c, end = '')
    print()
    w = input('\n\nEnter expression: ')

