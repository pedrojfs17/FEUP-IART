:- use_module(library(lists)).

% DFS
solve_dfs(InitialState, FinalState, Solution) :-
    dfs([], InitialState, FinalState, InvertedSolution),
    reverse(InvertedSolution, Solution). 

dfs(Path, FinalState, FinalState, [FinalState|Path]).
dfs(Path, Node, FinalState, Solution) :-
    trans(Node, Node1),
    \+member(Node1, Path),
    dfs([Node|Path], Node1, FinalState, Solution).


% BFS
solve_bfs(InitialState, FinalState, Solution) :-
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


% Iterative deepening
solve_iterative(InitialState, FinalState, Solution) :-
    iterative(InitialState, FinalState, InvertedSolution),
    reverse(InvertedSolution, Solution).


iterative(FinalState, FinalState, [FinalState]).

iterative(FirstNode, LastNode, [LastNode|Path]) :- 
    iterative(FirstNode, OneButLast, Path),
    trans(OneButLast, LastNode),
    \+member(LastNode, Path).