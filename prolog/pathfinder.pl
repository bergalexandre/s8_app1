player_is_within_x_axis_of_wall(Wall_x, Wall_width, Player_x) :-
    Player_x < (Wall_x+Wall_width),
    Player_x > (Wall_x).

player_is_within_y_axis_of_wall(Wall_y, Wall_height, Player_y) :-
    Player_y < (Wall_y+Wall_height),
    Player_y > (Wall_y).

is_wall_north([X, Y, Width, Height], [Player_x, Player_y]) :-
    format("Wall~w, ~w, ~w, ~w and player ~w, ~w", [X, Y, Width, Height, Player_x, Player_y]),
    player_is_within_x_axis_of_wall(X, Width, Player_x),
    Player_y > Y.
 
is_wall_south([X, Y, Width, Height], [Player_x, Player_y]) :-
    format("Wall~w, ~w, ~w, ~w and player ~w, ~w", [X, Y, Width, Height, Player_x, Player_y]),
    player_is_within_x_axis_of_wall(X, Width, Player_x),
    Player_y < Y.

is_wall_east([X, Y, Width, Height], [Player_x, Player_y]) :-
    format("Wall~w, ~w, ~w, ~w and player ~w, ~w", [X, Y, Width, Height, Player_x, Player_y]),
    player_is_within_y_axis_of_wall(Y, Height, Player_y),
    Player_x > X.

is_wall_west([X, Y, Width, Height], [Player_x, Player_y]) :-
    format("Wall~w, ~w, ~w, ~w and player ~w, ~w", [X, Y, Width, Height, Player_x, Player_y]),
    player_is_within_y_axis_of_wall(Y, Height, Player_y),
    Player_x < X.

free_direction([X, Y, Width, Height], [Player_x, Player_y], res) :-
    findall(North, is_wall_north([X, Y, Width, Height], [Player_x, Player_y]), res).