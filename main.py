"""
CLI entry point for the RAG research assistant.

Usage:
    python main.py ingest [--force]
    python main.py ask "your question here" [--top-k 5]
    python main.py chat
"""
import argparse
from rich.console import Console
from rich.markdown import Markdown

from src.rag_pipeline import ingest_documents, ask_question

console = Console()


def cmd_ingest(args):
    console.print("[bold cyan]Ingesting documents...[/bold cyan]")
    n = ingest_documents(force=args.force)
    if n:
        console.print(f"[bold green]Done.[/bold green] Ingested {n} chunk(s).")
    else:
        console.print("[yellow]Nothing new to ingest.[/yellow]")


def cmd_ask(args):
    result = ask_question(args.question, top_k=args.top_k)
    console.print()
    console.print(Markdown(result["answer"]))
    if result["sources"]:
        console.print("\n[bold]Sources:[/bold]")
        console.print(result["sources"])


def cmd_chat(args):
    console.print("[bold cyan]RAG Research Assistant — interactive chat[/bold cyan]")
    console.print("Type your question, or 'exit' to quit.\n")
    while True:
        try:
            question = console.input("[bold]You:[/bold] ")
        except (EOFError, KeyboardInterrupt):
            break
        if question.strip().lower() in {"exit", "quit"}:
            break
        if not question.strip():
            continue
        result = ask_question(question)
        console.print()
        console.print(Markdown(result["answer"]))
        if result["sources"]:
            console.print("\n[bold]Sources:[/bold]")
            console.print(result["sources"])
        console.print()


def main():
    parser = argparse.ArgumentParser(description="RAG Research Assistant with Citations")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest documents from data/documents/")
    p_ingest.add_argument("--force", action="store_true", help="Re-ingest all documents")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="Ask a single question")
    p_ask.add_argument("question", type=str, help="Your question")
    p_ask.add_argument("--top-k", type=int, default=None, help="Number of chunks to retrieve")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="Start an interactive chat session")
    p_chat.set_defaults(func=cmd_chat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
