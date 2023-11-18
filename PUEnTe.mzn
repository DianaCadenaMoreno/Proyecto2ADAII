% Data and Parameters
int: J;   % Number of generation units
int: K;   % Number of planning time intervals
array[1..J] of int: Ej;    % Cost of turning on each unit
array[1..J] of float: Aj;  % Cost of turning off each unit
array[1..J] of int: Fj;    % Fixed operating cost of each unit
array[1..J] of float: Vj;  % Variable cost coefficient for turning on each unit
array[1..J] of int: Pj;    % Lower limit of power generation for each unit if it's generating
array[1..J] of int: Pj_max; % Upper limit of power generation for each unit if it's generating
array[1..J] of int: Supj;  % Upper limit of power expansion for each unit
array[1..J] of int: Infj;  % Lower limit of power reduction for each unit
array[1..J] of int: P0j;   % Initial power generation for each unit just before the planning horizon
array[1..K] of int: Dk;    % Global energy demand for each time interval
array[1..K] of int: Rk;    % Energy reserve for each time interval
array[1..J] of int: Gj;  % Indicator of whether the unit generated in the previous cycle

% Variables:
array[1..J, 1..K] of var int: pjk;
array[1..J, 1..K] of var 0..1: UnitOperatingState;
array[1..J, 1..K] of var 0..1: UnitStartup;
array[1..J, 1..K] of var 0..1: UnitShutdown;

% Constraints
constraint forall(j in 1..J, k in 1..K) (
    (pjk[j, k] >= 0) /\
    ((pjk[j, k] >= 0 /\ pjk[j, k] <= 0) \/ (pjk[j, k] >= Pj[j])) /\
    (pjk[j, k] <= Pj_max[j])
);

constraint forall(k in 1..K) (
    (sum(j in 1..J) (pjk[j, k]) = Dk[k]) /\
    (sum(j in 1..J) (Pj_max[j] * UnitOperatingState[j, k]) >= (Dk[k] + Rk[k]))
);

% Constraints 3 and 4 combined: Limits on power variation
constraint forall(j in 1..J, k in 2..K) (
    (if pjk[j, k] > 0 /\ pjk[j, k - 1] > 0 then
        (pjk[j, k] - pjk[j, k - 1]) <= Supj[j] /\
        (pjk[j, k - 1] - pjk[j, k]) <= Infj[j]
    else true endif)
);

%  Unit startup and shutdown
constraint forall(j in 1..J, k in 1..K) (
    %  Unit operating state
    UnitOperatingState[j, k] = (pjk[j, k] > 0) /\
    % Unit startup
    UnitStartup[j, k] = ((k > 1 /\ pjk[j, k - 1] = 0 /\ pjk[j, k] > 0) \/ (k = 1 /\ Gj[j] = 0 /\ pjk[j, k] > 0)) /\
    % Unit shutdown
    UnitShutdown[j, k] = ((k > 1 /\ pjk[j, k - 1] > 0 /\ pjk[j, k] = 0) \/ (k = 1 /\ Gj[j] = 1 /\ pjk[j, k] = 0))
);

% Objective function
var float: costo_total;
constraint costo_total = sum(k in 1..K) (
    sum(j in 1..J) (Fj[j] * UnitOperatingState[j, k] + Vj[j] * pjk[j, k] + Ej[j] * UnitStartup[j, k] + Aj[j] * UnitShutdown[j, k])
);

% Minimization Objective
solve minimize costo_total;

% Output
output ["\(costo_total);"];
output ["\(pjk);"];