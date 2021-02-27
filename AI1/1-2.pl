/**
 * 3 Missionares
 * 3 Cannibals
 * 
 * Boat takes 1 or 2 people at a time
 * 
 * M - Number of missionares
 * C - Number of cannibals
 * 
 * M >= C all times
 * 
 * State Representation: (CLeft, MLeft, Boat, CRight, MRight)
 * 
 * Initial State: (3,3,left,0,0)
 * Final State: (0,0,right,3,3)
 */

:- include('search-methods.pl'). 

initial_state( r(3,3,left,0,0) ).

final_state( r(0,0,right,3,3) ).

valid_state(CLeft, MLeft, CRight, MRight) :-
    CLeft >= 0, MLeft >= 0, CRight >= 0, MRight >= 0,
    CLeft =< 3, MLeft =< 3, CRight =< 3, MRight =< 3,
    (MLeft >= CLeft ; MLeft = 0),
    (MRight >= MRight ; MRight = 0).


% Two missionaries cross left to right.
trans( r(CL,ML,left,CR,MR) , r(CL,ML2,right,CR,MR2) ):-
	MR2 is MR+2,
	ML2 is ML-2,
	valid_state(CL,ML2,CR,MR2).

% Two cannibals cross left to right.
trans( r(CL,ML,left,CR,MR) , r(CL2,ML,right,CR2,MR) ):-
	CR2 is CR+2,
	CL2 is CL-2,
	valid_state(CL2,ML,CR2,MR).

% One missionary and one cannibal cross left to right.
trans( r(CL,ML,left,CR,MR) , r(CL2,ML2,right,CR2,MR2) ):-
	CR2 is CR+1,
	CL2 is CL-1,
	MR2 is MR+1,
	ML2 is ML-1,
	valid_state(CL2,ML2,CR2,MR2).

% One missionary crosses left to right.
trans( r(CL,ML,left,CR,MR) , r(CL,ML2,right,CR,MR2) ):-
	MR2 is MR+1,
	ML2 is ML-1,
	valid_state(CL,ML2,CR,MR2).

% One cannibal crosses left to right.
trans( r(CL,ML,left,CR,MR) , r(CL2,ML,right,CR2,MR) ):-
	CR2 is CR+1,
	CL2 is CL-1,
	valid_state(CL2,ML,CR2,MR).

% Two missionaries cross right to left.
trans( r(CL,ML,right,CR,MR) , r(CL,ML2,left,CR,MR2) ):-
	MR2 is MR-2,
	ML2 is ML+2,
	valid_state(CL,ML2,CR,MR2).

% Two cannibals cross right to left.
trans( r(CL,ML,right,CR,MR) , r(CL2,ML,left,CR2,MR) ):-
	CR2 is CR-2,
	CL2 is CL+2,
	valid_state(CL2,ML,CR2,MR).

%  One missionary and one cannibal cross right to left.
trans( r(CL,ML,right,CR,MR) , r(CL2,ML2,left,CR2,MR2) ):-
	CR2 is CR-1,
	CL2 is CL+1,
	MR2 is MR-1,
	ML2 is ML+1,
	valid_state(CL2,ML2,CR2,MR2).

% One missionary crosses right to left.
trans( r(CL,ML,right,CR,MR) , r(CL,ML2,left,CR,MR2) ):-
	MR2 is MR-1,
	ML2 is ML+1,
	valid_state(CL,ML2,CR,MR2).

% One cannibal crosses right to left.
trans( r(CL,ML,right,CR,MR) , r(CL2,ML,left,CR2,MR) ):-
	CR2 is CR-1,
	CL2 is CL+1,
	valid_state(CL2,ML,CR2,MR).



river_dfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_dfs(InitialState, FinalState, Solution).


river_bfs(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_bfs(InitialState, FinalState, Solution).


river_iterative(Solution) :-
    initial_state(InitialState),
    final_state(FinalState),
    solve_iterative(InitialState, FinalState, Solution).

