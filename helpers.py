import warnings
import nest_asyncio
from a2a.types import AgentCard
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
from pathlib import Path
import base64
import pypdf
import re
import logging
import warnings
from dotenv import load_dotenv
from google.auth import impersonated_credentials
from google.oauth2 import service_account

console = Console()

### Environment setup
def setup_env() -> None:
    """Initializes the environment by loading .env and applying nest_asyncio."""
    load_dotenv(override=True)
    nest_asyncio.apply()

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

### Output formatting helpers

def display_markdown(text: str):
    console.print(Markdown(text))

def mute_logs():
    logging.disable(level=logging.WARNING)
    warnings.filterwarnings("ignore")


def format_llm_response(text: str) -> str:
    """formats llms response for clean terminal display"""
        # color helpers
    def c(txt, *codes):
        return "".join(codes) + txt + "\033[0m"

    BOLD    = "\033[1m"
    WHITE   = "\033[97m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    GREY    = "\033[90m"
    BG_BLUE = "\033[44m"

    #  title
    formatted = []

    # Lines
    for line in text.strip().split("\n"):
        line = line.rstrip()

        if not line:
            formatted.append("")

        elif line.startswith("# "):
            formatted.append("")
            formatted.append(c(f"  {line[2:].upper()}  ", BOLD, WHITE, BG_BLUE))
            formatted.append("")

        elif line.startswith("## "):
            content = line[3:]
            formatted.append("")
            formatted.append(c(content.upper(), BOLD, CYAN))
            formatted.append(c("─" * len(content), CYAN))

        elif line.startswith("### "):
            formatted.append(c(f"  {line[4:]}", BOLD, BLUE))

        elif re.match(r"^[-*] ", line):
            formatted.append(c("  •", GREEN, BOLD) + c(f"  {line[2:]}", WHITE))

        elif re.match(r"^\d+\. ", line):
            m = re.match(r"^(\d+)\. (.*)", line)
            formatted.append(c(f"  {m.group(1)}.", YELLOW, BOLD) + c(f"  {m.group(2)}", WHITE))

        elif line.startswith("```"):
            lang  = line[3:]
            label = f" {lang} " if lang else " code "
            formatted.append(c(f"  ┌─{label}{'─' * (34 - len(label))}┐", GREY))

        else:
            # inline code  →  magenta
            if "`" in line:
                line = re.sub(r"`(.*?)`", lambda m: c(m.group(1), MAGENTA), line)

            # bold text  →  yellow bold
            if "**" in line:
                line = re.sub(r"\*\*(.*?)\*\*", lambda m: c(m.group(1), BOLD, YELLOW), line)

            formatted.append(c(line, WHITE))

    return "\n".join(formatted)
     
    
def print_llm_response(text: str, title: str = None) -> None:
    """Print formatted LLM response to terminal."""
    if title:
        print(f"\n{'═' * 40}")
        print(f"  {title}")
        print(f"{'═' * 40}")

    print(format_llm_response(text))
    print()

### File handling helpers

def encode_file_to_base64(file_path: str) -> str:
    """This function takes a file path as an input and returns base64 encoded strings of the file content(LLMs which support native pdf formats)"""
    with Path(file_path).open("rb") as file:
        return base64.standard_b64encode(file.read()).decode("utf-8")
def pdf_to_text(file_path: str) -> str:
    """This functions takes a pdf file path as an input and returns the extracted text content of the pdf file(LLMs which do not support native pdf formats)"""
    with Path(file_path).open("rb") as file:
        reader = pypdf.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages)

### A2A helpers

def display_agent_card(agent_card: AgentCard) -> None:
    """Nicely formats and displays an AgentCard."""

    def esc(text: str) -> str:
        """Escapes pipe characters for Markdown table compatibility."""
        return str(text).replace("|", r"\|")

    # --- Part 1: Main Metadata Table ---
    md_parts = [
        "### Agent Card Details",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Name** | {esc(agent_card.name)} |",
        f"| **Description** | {esc(agent_card.description)} |",
        f"| **Version** | `{esc(agent_card.version)}` |",
        f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
        f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
    ]

    # --- Part 2: Skills Table ---
    if agent_card.skills:
        md_parts.extend(
            [
                "\n#### Skills",
                "| Name | Description | Examples |",
                "| :--- | :--- | :--- |",
            ]
        )
        for skill in agent_card.skills:
            examples_str = (
                "<br>".join(f"• {esc(ex)}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            md_parts.append(
                f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
            )

    # Join all parts and display
    # display(Markdown("\n".join(md_parts)))
    console.print(Markdown("\n".join(md_parts)))



