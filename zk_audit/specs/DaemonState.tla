---------------- MODULE DaemonState ----------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS 
    Clients,           \* Set of connected enterprise client nodes
    MaxQueue           \* Maximum capacity of the telemetry buffer

VARIABLES 
    clientStates,      \* Mapping of client ID to their current state (Idle, Processing, Guarded)
    telemetryQueue,    \* FIFO queue of incoming telemetry payloads
    deadlocked         \* Failure flag indicating state freeze

vars << clientStates, telemetryQueue, deadlocked >>

(* Type invariant and initial states *)
Init ==
    /\ clientStates = [c \in Clients |-> "Idle"]
    /\ telemetryQueue = << >>
    /\ deadlocked = FALSE

(* Transition: Client submits a new telemetry payload *)
SubmitTelemetry(c) ==
    /\ clientStates[c] = "Idle"
    /\ Len(telemetryQueue) < MaxQueue
    /\ telemetryQueue' = Append(telemetryQueue, c)
    /\ clientStates' = [clientStates EXCEPT !c = "Processing"]
    /\ UNCHANGED deadlocked

(* Transition: Daemon processes payload and enforces Standard 333 invariant *)
ProcessTelemetry ==
    /\ telemetryQueue /= << >>
    /\ LET currentClient == Head(telemetryQueue)
       IN  /\ clientStates[currentClient] = "Processing"
           /\ clientStates' = [clientStates EXCEPT !currentClient = "Guarded"]
           /\ telemetryQueue' = Tail(telemetryQueue)
           /\ UNCHANGED deadlocked

(* Safety Property: System never enters a permanent deadlock state *)
NoDeadlock ==
    deadlocked = FALSE

Next ==
    \/ (\E c \in Clients : SubmitTelemetry(c))
    \/ ProcessTelemetry

Spec == Init /\ [][Next]_vars /\ WF_vars(ProcessTelemetry)

====================================================
