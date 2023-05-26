
<img src="https://user-images.githubusercontent.com/4897599/198412035-96b075b2-d370-4733-a66c-60ab2ee7b4b0.png" width="400" height="220" />

# Installation:

## Ubuntu/Debian:

Python3.8 or above is required. 
This code was tested with Python3.8 on a linux machine. 
```
python3 setup.py install
```

# Usage: 

This is a limited release of the DLSmith framework. This release should only be considered as a supplementary material with our ISSTA 2023 submission.
You can generate a Datalog program in one of six dialects mentioned in the paper using the following commands: 

```
dlsmith --engine=<ENGINE-NAME>
```
Where `engine = souffle || scallop || formulog || flix || ascent || ddlog`

Running the above command will generate a Datalog program along with one transformation of the generated program. For example: 

```
$ dlsmith --engine=souffle

 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ORIGINAL PROGRAM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 

// ************ Parsed program text begin

.decl A(from:number, to:number, z:number) btree_delete
.decl graph(from:number, to:number)
graph(1, 2).
graph(1, 3).
graph(3, 4).
graph(2, 5).
graph(4, 6).
graph(5, 6).
graph(6, 7).
A(1, 2, 1).
A(1, 3, 1).
A(from, to, c+1) :-
    A(_, from, c),
    graph(from, to).
A(from, to, c1) <= A(_, to, c2) :-
    c1 > c2.
A(from1, to, c) <= A(from2, to, c) :-
    from1 > from2.
.decl eql(a: number, b: number)
.decl rel(a: number, b: number) btree_delete
eql(x,x) :- eql(x,_); eql(_,x).
eql(x,y) :- eql(y,x).
eql(x,z) :- eql(x,y), eql(y,z).
rel(1, 2).
rel(1, 3).
eql(x, x) :- rel(x, _).
eql(2, 3).
rel(a, b) <= rel(c, d) :- eql(a, c), eql(b, d), a <= c, b <= d.
.decl C(x:number) btree_delete
.decl D(x:number, y:number)
C(1).
D(1, 1).
C(x1) <= C(x2) :-
    D(x1, x2),
    x1 <= x2.
    .plan 0:(1,3,2)
.decl E(x:number, y:number) btree_delete
E(1,1).
E(1,2).
E(_, x1) <= E(_, x2) :-
   x1 <= x2.

// ************ Parsed program text end

.decl a__(a:number, b:number, c:number) 
.decl b__(a:number, b:number) 
.decl c__(a:number, b:symbol, c:number) 
.decl d__(a:symbol, b:symbol, c:number) 
.decl e__(a:number) 


.output d__ // Output node


a__(c, d, c) :- eql(d, c), D(c, c).
b__(b, a) :- rel(b, a).
d__(e, e, b) :- a__(g, g, h), c__(f, e, d), graph(a, b).
e__(f) :- b__(a, b), c__(h, d, h), c__(f, d, f), A(n, a, m), C(k), E(m, b).
e__(a) :- c__(c, b, a).


 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
 xxxxxxxxxxxxxxxxxxxxxxxxxxxx TRANSFORMED PROGRAM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 


// ************ Parsed program text begin

.decl A(from:number, to:number, z:number) btree_delete
.decl graph(from:number, to:number)
graph(1, 2).
graph(1, 3).
graph(3, 4).
graph(2, 5).
graph(4, 6).
graph(5, 6).
graph(6, 7).
A(1, 2, 1).
A(1, 3, 1).
A(from, to, c+1) :-
    A(_, from, c),
    graph(from, to).
A(from, to, c1) <= A(_, to, c2) :-
    c1 > c2.
A(from1, to, c) <= A(from2, to, c) :-
    from1 > from2.
.decl eql(a: number, b: number)
.decl rel(a: number, b: number) btree_delete
eql(x,x) :- eql(x,_); eql(_,x).
eql(x,y) :- eql(y,x).
eql(x,z) :- eql(x,y), eql(y,z).
rel(1, 2).
rel(1, 3).
eql(x, x) :- rel(x, _).
eql(2, 3).
rel(a, b) <= rel(c, d) :- eql(a, c), eql(b, d), a <= c, b <= d.
.decl C(x:number) btree_delete
.decl D(x:number, y:number)
C(1).
D(1, 1).
C(x1) <= C(x2) :-
    D(x1, x2),
    x1 <= x2.
    .plan 0:(1,3,2)
.decl E(x:number, y:number) btree_delete
E(1,1).
E(1,2).
E(_, x1) <= E(_, x2) :-
   x1 <= x2.

// ************ Parsed program text end

.decl a__(a:number, b:number, c:number) 
.decl c__(a:number, b:symbol, c:number) 
.decl d__(a:symbol, b:symbol, c:number) 
.decl g__(a:symbol, b:symbol) 


.output d__ // Output node


a__(d, d, d) :- eql(d, d), D(d, d), rel(d, d), a__(d, d, d), eql(d, d).
d__(e, e, b) :- a__(g, g, h), c__(f, e, d), graph(b, b), d__(e, e, h), d__(e, e, b), A(b, h, g).
```