import argparse
import sys
import json
from facts_db.core import FactsDB
from facts_db.telemetry import TelemetryVerifier
from facts_db.policy import PolicyEvaluator
from facts_db.daemon import TelemetryDaemon
from facts_db.prover import TautologyProver

def main():
    parser = argparse.ArgumentParser(description="FactsDB Algebraic Normalization & Telemetry Guard CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("normalize", help="Normalize an expression").add_argument("expression")
    subparsers.add_parser("distribute", help="Apply distributivity").add_argument("expression")
    subparsers.add_parser("demorgan", help="Apply De Morgan's Law").add_argument("expression")
    subparsers.add_parser("ir", help="Export to JSON IR").add_argument("expression")
    
    prov_parser = subparsers.add_parser("prove", help="Prove satisfiability or tautology")
    prov_parser.add_argument("expression")

    ver_parser = subparsers.add_parser("verify", help="Verify telemetry payload JSON")
    ver_parser.add_argument("--log", required=True)
    ver_parser.add_argument("--invariant", required=True)
    ver_parser.add_argument("--standard", default="333")

    tail_parser = subparsers.add_parser("tail", help="Tail stdin telemetry stream and guard appends")
    tail_parser.add_argument("--invariant", required=True)
    tail_parser.add_argument("--standard", default="333")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    db = FactsDB()
    try:
        if args.command == "normalize":
            print(db.normalize(args.expression))
        elif args.command == "distribute":
            print(db.expand_distributivity(args.expression))
        elif args.command == "demorgan":
            print(db.demorgan(args.expression))
        elif args.command == "ir":
            print(json.dumps(db.to_ast(args.expression), indent=2))
        elif args.command == "prove":
            prover = TautologyProver()
            print(prover.prove(args.expression))
        elif args.command == "verify":
            try:
                with open(args.log, "r") as f:
                    payload_data = f.read()
            except FileNotFoundError:
                payload_data = args.log
            verifier = TelemetryVerifier(standard_invariant=args.standard)
            result = verifier.verify_payload(payload_data, args.invariant)
            print(json.dumps(result, indent=2))
            if result.get("status") != "APPROVED":
                sys.exit(1)
        elif args.command == "tail":
            daemon = TelemetryDaemon(invariant=args.invariant, standard=args.standard)
            daemon.watch_stream(sys.stdin)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
