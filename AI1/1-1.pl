:- use_module(library(lists)).

initial_state( b(0,0) ).
final_state( b(2,0) ).

% Fill first bucket
trans( b(X,Y), b(4,Y) ) :- X < 4.

% Fill second bucket
trans( b(X,Y), b(X,3) ) :- Y < 3.

% Empty first bucket
trans( b(X,Y), b(0,Y) ) :- X > 0.

% Empty second bucket
trans( b(X,Y), b(X,0) ) :- Y > 0.

% First bucket to second bucket until second is full
trans( b(X,Y), b(Z,3) ) :-
    Y < 3, X > 0,
    Z is X - (3 - Y), Z >= 0.

% First bucket to second bucket until first is empty
trans( b(X,Y), b(0,Z) ) :-
    Y < 3, X > 0,
    Z is X + Y, Z =< 3.

% Second bucket to first bucket until first is full
trans( b(X,Y), b(4,Z) ) :-
    X < 4, Y > 0,
    Z is Y - (4 - X), Z >= 0.

% Second bucket to first bucket until second is empty
trans( b(X,Y), b(Z,0) ) :-
    X < 4, Y > 0,
    Z is X + Y, Z =< 4.


% DFS
solve_dfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    dfs([], InitialState, FinalState, InvertedSolution),
    reverse(InvertedSolution, Solution). 

dfs(Path, FinalState, FinalState, [FinalState|Path]).
dfs(Path, Node, FinalState, Solution) :-
    trans(Node, Node1),
    \+member(Node1, Path),
    dfs([Node|Path], Node1, FinalState, Solution).


% BFS
solve_bfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    bfs([[InitialState]], FinalState, Solution). 

bfs([[FinalState|Visited]|_], FinalState, Solution) :-
    reverse([FinalState|Visited], Solution).

bfs([N|Rest], FinalState, Solution) :-
    findall(SonExtension, extends_till_son(N, SonExtension), Extensions),
    append(Rest, Extensions, NewRest),
    bfs(NewRest, FinalState, Solution).

extends_till_son([N|Trajectory], [N1,N|Trajectory]):-
    trans(N, N1),
    \+member(N1, Trajectory).