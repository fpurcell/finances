from pathlib import Path

import matplotlib.pyplot as plt


OUT_DIR = Path(__file__).parent / "images"


DIAGRAMS = [
    {
        "slug": "parser_sequence",
        "title": "fin/parser.py",
        "actors": [
            "User",
            "parser.main()",
            "parse_file()",
            "Input File",
            "Regex",
            "plot.show()",
            "pandas",
            "matplotlib",
        ],
        "messages": [
            ("User", "parser.main()", "run parser with filename"),
            ("parser.main()", "parse_file()", "parse_file(file_path)"),
            ("parse_file()", "Input File", "open and iterate lines"),
            ("Input File", "parse_file()", "line"),
            ("parse_file()", "Regex", "match TOTAL amount"),
            ("parse_file()", "Regex", "match date"),
            ("parse_file()", "parse_file()", "append amount and date"),
            ("parse_file()", "parser.main()", "dates, dollars"),
            ("parser.main()", "User", "print extracted totals"),
            ("parser.main()", "plot.show()", "show(dates, dollars)"),
            ("plot.show()", "pandas", "build DataFrame"),
            ("plot.show()", "matplotlib", "render line chart"),
            ("matplotlib", "User", "display plot window"),
        ],
    },
    {
        "slug": "four_percent_rule_sequence",
        "title": "fin/four_percent_rule.py",
        "actors": [
            "User",
            "main()",
            "argparse",
            "Projection Loop",
        ],
        "messages": [
            ("User", "main()", "run script with optional flags"),
            ("main()", "argparse", "parse_args()"),
            ("argparse", "main()", "balance, age, growth, withdrawal,\ninflation, years"),
            ("main()", "main()", "compute first-year withdrawal"),
            ("main()", "User", "print projection header"),
            ("main()", "Projection Loop", "compute growth and end balance"),
            ("Projection Loop", "main()", "yearly values"),
            ("main()", "User", "print row"),
            ("main()", "main()", "inflate next withdrawal"),
            ("main()", "User", "print ending balance"),
        ],
    },
    {
        "slug": "pdf_sequence",
        "title": "fin/pdf.py",
        "actors": [
            "User",
            "pdf.main()",
            "extract_pdf_text()",
            "PdfReader",
            "split_sections()",
            "extract_transactions()",
            "extract_descriptions()",
            "normalize_payee()",
            "CSV writers",
        ],
        "messages": [
            ("User", "pdf.main()", "run pdf.py"),
            ("pdf.main()", "extract_pdf_text()", "extract_pdf_text(pdf_path)"),
            ("extract_pdf_text()", "PdfReader", "load PDF pages"),
            ("PdfReader", "extract_pdf_text()", "extracted text"),
            ("extract_pdf_text()", "pdf.main()", "full_text"),
            ("pdf.main()", "split_sections()", "split_sections(full_text)"),
            ("split_sections()", "pdf.main()", "transactions_text,\ndescriptions_text"),
            ("pdf.main()", "extract_transactions()", "extract withdrawal rows"),
            ("extract_transactions()", "pdf.main()", "transactions"),
            ("pdf.main()", "extract_descriptions()", "extract payee descriptions"),
            ("extract_descriptions()", "pdf.main()", "descriptions"),
            ("pdf.main()", "normalize_payee()", "normalize each description"),
            ("normalize_payee()", "pdf.main()", "canonical payee"),
            ("pdf.main()", "CSV writers", "write 3 CSV outputs"),
            ("pdf.main()", "User", "print totals and output paths"),
        ],
    },
]


def draw_sequence_diagram(title: str, actors: list[str], messages: list[tuple[str, str, str]], output_path: Path) -> None:
    fig_width = max(12, len(actors) * 1.8)
    fig_height = max(8, len(messages) * 0.75 + 2.5)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=180)
    ax.set_xlim(0, len(actors) + 1)
    ax.set_ylim(len(messages) + 2, 0)
    ax.axis("off")

    x_positions = {actor: idx + 1 for idx, actor in enumerate(actors)}

    for actor, xpos in x_positions.items():
        ax.text(
            xpos,
            0.6,
            actor,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "#f3f4f6", "edgecolor": "#374151"},
        )
        ax.plot([xpos, xpos], [1.0, len(messages) + 1], linestyle="--", linewidth=1, color="#9ca3af")

    for row, (src, dst, label) in enumerate(messages, start=1):
        y = row + 0.4
        x1 = x_positions[src]
        x2 = x_positions[dst]

        if src == dst:
            loop_width = 0.35
            ax.plot([x1, x1 + loop_width], [y, y], color="#2563eb", linewidth=1.6)
            ax.plot([x1 + loop_width, x1 + loop_width], [y, y + 0.3], color="#2563eb", linewidth=1.6)
            ax.annotate(
                "",
                xy=(x1, y + 0.3),
                xytext=(x1 + loop_width, y + 0.3),
                arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#2563eb"},
            )
            ax.text(x1 + loop_width + 0.05, y + 0.15, label, fontsize=8.5, va="center", color="#111827")
            continue

        ax.annotate(
            "",
            xy=(x2, y),
            xytext=(x1, y),
            arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#2563eb"},
        )
        ax.text((x1 + x2) / 2, y - 0.12, label, ha="center", va="bottom", fontsize=8.5, color="#111827")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=18)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for diagram in DIAGRAMS:
        draw_sequence_diagram(
            diagram["title"],
            diagram["actors"],
            diagram["messages"],
            OUT_DIR / f"{diagram['slug']}.png",
        )


if __name__ == "__main__":
    main()
