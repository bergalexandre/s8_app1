player_is_within_x_axis_of_wall(Wall_x, Wall_width, Player_x) :-
    Player_x < (Wall_x+Wall_width+10),
    Player_x > (Wall_x-10).

player_is_within_y_axis_of_wall(Wall_y, Wall_height, Player_y) :-
    Player_y < (Wall_y+Wall_height+10),
    Player_y > (Wall_y-10).

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

is_node_start(X, Y, Node_env) :-
    member(start_node(X, Y), Node_env).

is_node_free(X, Y, Node_env) :-
    member(free_node(X, Y), Node_env).

is_node_wall(X, Y, Node_env) :-
    member(walled_node(X, Y), Node_env).

is_node_end(X, Y, Node_env) :-
    member(end_node(X, Y), Node_env).

path(Node_env, is_node_free(X, Y)) :- is_node_free(X, Y, Node_env).
path(Node_env, is_node_end(X, Y)) :- is_node_end(X, Y, Node_env).

find_node_info(Node_env, Response) :- 
    findall(Path, path(Node_env, Path), Response).

%% find_node_info([walled_node(-1,0), walled_node(0,-1), free_node(0,1), end_node(1,0)], R).