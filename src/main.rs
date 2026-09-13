mod hash;
mod storage;
mod capfile;
mod snapshot;
mod replay;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "capctl")]
struct Cli {
    #[command(subcommand)]
    cmd: Command,
}

#[derive(Subcommand)]
enum Command {
    Init,
    Write { tree: String },
    Verify { id: String },
    Replay { id: String },
}

fn main() {
    let cli = Cli::parse();
    match cli.cmd {
        Command::Init => { storage::init(); println!("init OK"); }
        Command::Write { tree } => {
            let cap = capfile::write(&tree);
            let snap = snapshot::write(&cap, &tree);
            println!("capfile: {}\nsnapshot: {}", cap, snap);
        }
        Command::Verify { id } => { println!("{}", replay::verify(&id)); }
        Command::Replay { id } => { println!("{:#?}", replay::replay_chain(&id)); }
    }
}
