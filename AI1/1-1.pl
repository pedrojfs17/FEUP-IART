:- include('search-methods.pl'). 

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



bucket_dfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_dfs(InitialState, FinalState, Solution).


bucket_bfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_bfs(InitialState, FinalState, Solution).


bucket_iterative(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_iterative(InitialState, FinalState, Solution).