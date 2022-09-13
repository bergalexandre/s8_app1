
IsStart(Maze, [X,Y]) :-
    member(IsStart(X,Y), maze)

Move(Maze, [X,Y], [H|T])
    IsStart(Maze, H)

pathfinder(Maze, Response) :-
    findall([X,Y], Move(Maze, [X,Y], res), Response)